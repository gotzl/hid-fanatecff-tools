import time
import ctypes
import socket
import select
import threading
import fanatec_led_server


class WrcPacket(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
            ("packet_uid", ctypes.c_uint64),
            ("shiftlights_fraction", ctypes.c_float),
            ("shiftlights_rpm_start", ctypes.c_float),
            ("shiftlights_rpm_end", ctypes.c_float),
            ("shiftlights_rpm_valid", ctypes.c_bool),
            ("vehicle_gear_index", ctypes.c_uint8),
            ("vehicle_gear_index_neutral", ctypes.c_uint8),
            ("vehicle_gear_index_reverse", ctypes.c_uint8),
            ("vehicle_gear_maximum", ctypes.c_uint8),
            ("vehicle_speed", ctypes.c_float),
            ("vehicle_transmission_speed", ctypes.c_float),
            ("vehicle_engine_rpm_current", ctypes.c_float),
    ]


class WrcClient(fanatec_led_server.Client):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 20778

    def __init__(self, ev, dbus=True, device=None, display='gear'):
        fanatec_led_server.Client.__init__(self, ev, dbus, device, display)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((WrcClient.UDP_IP, WrcClient.UDP_PORT))
        self.sock.setblocking(0)
        self.timeout_cnt = 0

    def prerun(self):
        while not self.ev.is_set():
            try:
                self.sock.recv(1024)
                break
            except:
                time.sleep(1)

    def tick(self):
        ready = select.select([self.sock], [], [], .2)
        if not ready[0]:
            print(f'Timeout waiting for WRC data, {self.timeout_cnt}')
            self.timeout_cnt += 1
            if self.timeout_cnt > 10:
                raise Exception('Too many timeouts received!')
            return False

        self.timeout_cnt = 0
        data = self.sock.recv(1024)
        packet = WrcPacket.from_buffer_copy(data)
        self._speedKmh = packet.vehicle_transmission_speed
        self._gear = packet.vehicle_gear_index
        self._revLightsPercent = packet.shiftlights_fraction
        self._suggestedGear = min(self._gear + 1, packet.vehicle_gear_maximum) \
            if packet.shiftlights_rpm_end > packet.vehicle_engine_rpm_current and packet.shiftlights_rpm_valid \
            else self._gear
        return True


if __name__ == "__main__":
    try:
        ev = threading.Event()
        wrc = WrcClient(ev, device='0005', dbus=False)
        wrc.start()
        wrc.join()
    except (KeyboardInterrupt, SystemExit):
        print("Interrupted")
    except Exception as e:
        raise e
    finally:
        ev.set()
