import time
import socket
import select
import threading
import fanatec_led_server

from f1_23_telemetry.f1_23_telemetry import packets


class F1_23Client(fanatec_led_server.Client):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 20777

    def __init__(self, ev, dbus=True, device=None, display='gear'):
        fanatec_led_server.Client.__init__(self, ev, dbus, device, display)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((F1_23Client.UDP_IP, F1_23Client.UDP_PORT))
        self.sock.setblocking(0)
        self.timeout_cnt = 0

    def prerun(self):
        while not self.ev.is_set():
            try:
                self.sock.recv(2048)
                break
            except Exception as e:
                time.sleep(1)

    def tick(self):
        ready = select.select([self.sock], [], [], .2)
        if not ready[0]:
            print('Timeout waiting for F1 23 data,', self.timeout_cnt)
            self.timeout_cnt += 1
            if self.timeout_cnt > 10:
                raise Exception('Too many timeouts received!')
            return False

        self.timeout_cnt = 0
        data = self.sock.recv(2048)
        header = packets.PacketHeader.from_buffer_copy(data)
        key = (header.packet_format, header.packet_version, header.packet_id)
        packet_type = packets.HEADER_FIELD_TO_PACKET_TYPE[key]
        if packet_type == packets.PacketCarTelemetryData:
            packet = packet_type.unpack(data)
            telem = packet.car_telemetry_data[0]
            self._speedKmh = telem.speed
            self._gear = telem.gear
            self._revLightsPercent = telem.rev_lights_percent
            self._suggestedGear = packet.suggested_gear
        return True


if __name__ == "__main__":
    try:
        ev = threading.Event()
        f1 = F1_23Client(ev, device='0005', dbus=False)
        f1.start()
        f1.join()

    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    except Exception as e:
        raise e
    finally:
        ev.set()
