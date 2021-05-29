import time
import socket
import select
import threading
import fanatec_led_server

from f1_2020_telemetry.f1_2020_telemetry import packets


class F12020Client(fanatec_led_server.Client):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 20777

    def __init__(self, ev, dbus=True, device=None, display='gear'): 
        fanatec_led_server.Client.__init__(self, ev, dbus, device, display)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((F12020Client.UDP_IP, F12020Client.UDP_PORT))
        self.sock.setblocking(0)
        self.timeout_cnt = 0

    def prerun(self):
        while not self.ev.isSet():
            try:
                self.sock.recv(2048)
                break
            except Exception as e:
                time.sleep(1)

    def tick(self):
        ready = select.select([self.sock], [], [], .2)
        if not ready[0]:
            print('Timeout waiting for F1 2020 data,', self.timeout_cnt)
            self.timeout_cnt += 1
            if self.timeout_cnt > 10:
                raise Exception('Too many timeouts received!')
            return False

        self.timeout_cnt = 0
        data = self.sock.recv(2048)
        packet = packets.unpack_udp_packet(data)
        if packet.header.packetId == packets.PacketID.CAR_TELEMETRY:
            telem = packet.carTelemetryData[packet.header.playerCarIndex]
            self._speedKmh = telem.speed
            self._gear = telem.gear
            self._revLightsPercent = telem.revLightsPercent/100
            self._suggestedGear = packet.suggestedGear
        return True

if __name__ == "__main__":
    try:
        ev = threading.Event()
        f1 = F12020Client(ev, device='0005', dbus=False)
        f1.start()
        f1.join()

    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    except Exception as e:
        raise e
    finally:
        ev.set()
