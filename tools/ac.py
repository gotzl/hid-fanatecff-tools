import socket
import struct
import select
import threading
import fanatec_led_server
import time
import json
import sys
import datetime

sys.path.append("../dbus")
from fanatec_input import (
    CSLElite,
    CSLEliteWheel,
    CSLP1V2Wheel,
)

car_data = json.load(open("car_data.json"))


class AcClient(fanatec_led_server.Client):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 9996

    HANDSHAKE = 0
    SUBSCRIBE_UPDATE = 1
    SUBSCRIBE_SPOT = 2
    DISMISS = 3

    def __init__(self, ev, dbus=True, device=None, display="gear"):
        fanatec_led_server.Client.__init__(self, ev, dbus, device, display)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)
        self.timeout_cnt = 0
        self.revbase = None
        self.revmax = None
        self._gear = 0
        self.autorpm = 0
        self.revsavetimer = None
        self.car_name = None

    @staticmethod
    def client_data(sock, operation):
        sock.sendto(
            bytearray(
                [
                    0x0,
                    0x0,
                    0x0,
                    0x2,  # android phone
                    0x0,
                    0x0,
                    0x0,
                    0x0,  # version
                    operation,
                    0x0,
                    0x0,
                    0x0,
                ]
            ),
            (AcClient.UDP_IP, AcClient.UDP_PORT),
        )


    def prerun(self):
        self.sock.setblocking(0)

        while not self.ev.isSet():
            # handshake
            AcClient.client_data(self.sock, AcClient.HANDSHAKE)

            # response
            ready = select.select([self.sock], [], [], 2)
            if not ready[0]:
                # print("Timeout connecting to AC server")
                continue
            #  get the car name to capture the appropriate max rpms
            handshake_response = self.sock.recv(2048)
            car_name = (
                handshake_response[:50]
                .decode("utf-8")
                .strip("\x00")
                .replace("\x00", "")
            )[:-1]
            self.car_name = car_name
            # print("Car name:", car_name)
            # breakpoint()
            if self.revmax is None:
                if car_name in car_data:
                    self.revmax = int(car_data[car_name])
                    autorpm = 0
                    print("Max revs for '%s': %i" % (car_name, self.revmax))
                else:
                    self.revmax = 4000
                    self.autorpm = 1
                    print("Car '%s' not found in car_data! Setting max revs to %i. Rev the car into the limiter while in neutral to adjust." % (car_name, self.revmax))

            # confirm
            AcClient.client_data(self.sock, AcClient.SUBSCRIBE_UPDATE)
            break

    def postrun(self):
        AcClient.client_data(self.sock, AcClient.DISMISS)
        self.revbase = None
        self.revmax = None
        self._gear = 0
        self.sock.setblocking(1)

    def tick(self):
        # https://docs.google.com/document/d/1KfkZiIluXZ6mMhLWfDX1qAGbvhGRC3ZUzjVIt5FQpp4/pub

        ready = select.select([self.sock], [], [], 0.2)
        if not ready[0]:
            print("Timeout waiting for AC server data,", self.timeout_cnt)
            self.timeout_cnt += 1
            if self.timeout_cnt > 10:
                raise Exception("Too many timeouts received!")
            return False

        self.timeout_cnt = 0
        data = self.sock.recv(2048)
        self._speedKmh = int(struct.unpack("<f", data[8:12])[0])
        self._absInAction = bool(data[21])
        self._tcInAction = bool(data[22])

        #  handling the rev measurement
        if self.revbase is None:
            rpms = int(struct.unpack("<f", data[68:72])[0])
            self.revbase = rpms  # save the base value
        else:
            rpms = int(struct.unpack("<f", data[68:72])[0])
            self._revLightsPercent = AcClient.rpms_to_revlights(
                rpms - self.revbase,
                self.revmax - self.revbase,
            )

        if self.revmax < rpms and self.autorpm == 1:
            self.revmax = rpms
            self.revsavetimer= datetime.datetime.now()


        if self.revsavetimer != None and ((datetime.datetime.now().minute * 60)  + datetime.datetime.now().second)  - ((self.revsavetimer.minute * 60 ) + self.revsavetimer.second) >= 3:
            self.autorpm = 0
            self.revsavetimer = None
            print("revlimiter adjusted to %i"%(self.revmax))
            car_data[self.car_name] = "%i"%(self.revmax)
            with open("car_data.json", "w") as write_file:
                json.dump(car_data, write_file, indent=4)
            print("revlimit saved to database")

        self._gear = int.from_bytes(data[76:80], byteorder="little") - 1
        return True



if __name__ == "__main__":
    try:
        ev = threading.Event()
        ac = AcClient(ev, device="0020", dbus=False)
        ac.start()  # start the thread...
        ac.join()  # run until the thread terminates

    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    except Exception as e:
        raise e
    finally:
        ev.set()
