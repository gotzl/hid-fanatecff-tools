import struct
import threading
import fanatec_led_server
import socket
import time
import select

from dataclasses import dataclass
from enum import IntEnum

from typing import Optional

# pick up the wheel IDs
import sys

sys.path.append("../dbus")
from fanatec_input import (
    CSL_ELITE_PS4_WHEELBASE_DEVICE_ID,
    CSL_DD_WHEELBASE_DEVICE_ID,
    CSLElite,
    CSLEliteWheel,
    CSLP1V2Wheel,
)


class PacketType(IntEnum):
    CAR_PHYSICS = 0
    RACE_DEFINITION = 1
    PARTICIPANTS = 2
    TIMINGS = 3
    GAME_STATE = 4
    WEATHER_STATE = 5
    VEHICLE_NAMES = 6
    TIME_STATS = 7
    PARTICIPANTS_VEHICLE_NAMES = 8


@dataclass
class CarData:
    gear: int
    rpm: int
    max_rpm: int
    speed: int


class AMS2DataParser:
    """
    A class holding helper methods for parsing the data from the UDP packets
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    @staticmethod
    def get_packet_type(data):
        return data[10]

    @staticmethod
    def get_gear(data):
        """
        According to the PCARS2 UDP protocol, if the packet type is 0, then the
        45th byte has as its first nibble the number of gears followed by the
        current gear in the second nibble; so if you are driving a car with 5
        gears and you are in 3rd gear, the 45th byte will be 0x53.

        To get the gear, then, you can mask this with 0xF.
        """
        try:
            gear_data = data[45]
            gear = gear_data & 0xF
            if gear == 15:
                gear = -1

        except IndexError:
            print("Error unpacking gear: IndexError")
            gear = 0
        return gear

    @staticmethod
    def get_speed(data):
        """
        Read off bytes 36, 37, 38, 39
        """
        try:
            unpacked = struct.unpack("<f", data[36:40])
            # speed in m/s, so we convert to km/h
            speed = int(3.6 * unpacked[0])
        except IndexError:
            print("Error unpacking speed: IndexError")
            speed = 0
        except struct.error:
            print("Error unpacking speed: struct.error")
            speed = 0
        return speed

    @staticmethod
    def get_rpm(data):
        """
        Read off byte 42 and 43
        """
        try:
            rpm_front = data[40]
            rpm_back = data[41]
            rpm = (rpm_back << 8) + rpm_front
        except IndexError:
            print("Error unpacking rpm: IndexError")
            rpm = 0
        return rpm

    @staticmethod
    def get_max_rpm(data):
        try:
            max_rpm_front = data[42]
            max_rpm_back = data[43]
            max_rpm = (max_rpm_back << 8) + max_rpm_front
        except IndexError:
            print("Error unpacking max rpm: IndexError")
            max_rpm = 1
        return max_rpm

    def process_packet(self, data) -> Optional[CarData]:
        packet_type = self.get_packet_type(data[0:44])
        if self.verbose:
            print("Packet type:", packet_type)
        if packet_type == PacketType.CAR_PHYSICS:
            gear = self.get_gear(data)
            rpm = self.get_rpm(data)
            max_rpm = self.get_max_rpm(data)
            speed = self.get_speed(data)
            return CarData(gear, rpm, max_rpm, speed)
        else:
            return None


class AMS2Client(fanatec_led_server.Client):
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5606

    def __init__(
        self,
        ev,
        dbus=True,
        device=None,
        display="gear",
    ):
        fanatec_led_server.Client.__init__(self, ev, dbus, device, display)
        self.data_parser = AMS2DataParser()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        self.sock.setblocking(0)
        self.timeout_cnt = 0

    def prerun(self):
        while not self.ev.isSet():
            try:
                self.sock.recv(2048)
                break
            except Exception as e:
                time.sleep(1)

    def postrun(self):
        pass

    def tick(self):
        ready = select.select([self.sock], [], [], 0.2)
        if not ready[0]:
            print("Timeout waiting for AMS2 data,", self.timeout_cnt)
            self.timeout_cnt += 1
            if self.timeout_cnt > 10:
                raise Exception("Too many timeouts received!")
            return False

        self.timeout_cnt = 0
        packet = self.sock.recv(2048)

        # returns None if the packet is not a car physics packet
        car_data: CarData = self.data_parser.process_packet(packet)

        # not yet implemented stuff
        self._absInAction = False
        self._tcInAction = False
        self._suggestedGear = 0

        if car_data is not None:
            # currently implemented stuff
            self._gear = car_data.gear
            self._revLightsPercent = 100 * car_data.rpm / car_data.max_rpm
            self._speedKmh = car_data.speed

        return True


if __name__ == "__main__":
    try:
        ev = threading.Event()
        ams2 = AMS2Client(
            ev,
            device=CSL_DD_WHEELBASE_DEVICE_ID,
            dbus=False,
        )

        ams2.start()
        ams2.join()

    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    except Exception as e:
        raise e
    finally:
        ev.set()
