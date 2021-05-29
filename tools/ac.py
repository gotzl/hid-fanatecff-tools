import socket
import struct
import select
import threading
import fanatec_led_server


class AcClient(fanatec_led_server.Client):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 9996

    HANDSHAKE = 0
    SUBSCRIBE_UPDATE = 1
    SUBSCRIBE_SPOT = 2
    DISMISS = 3 

    def __init__(self, ev, dbus=True, device=None, display='gear'): 
        fanatec_led_server.Client.__init__(self, ev, dbus, device, display)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)
        self.timeout_cnt = 0

    @staticmethod
    def client_data(sock, operation):
        sock.sendto(bytearray([
            0x0,0x0,0x0,0x2, # android phone
            0x0,0x0,0x0,0x0, # version
            operation,0x0,0x0,0x0, 
        ]), (AcClient.UDP_IP, AcClient.UDP_PORT))

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
            _ = self.sock.recv(2048)
            
            # confirm
            AcClient.client_data(self.sock, AcClient.SUBSCRIBE_UPDATE)
            break

    def postrun(self):
        AcClient.client_data(self.sock, AcClient.DISMISS)
        self.sock.setblocking(1)

    def tick(self):
        ready = select.select([self.sock], [], [], .2)
        if not ready[0]:
            print('Timeout waiting for AC server data,', self.timeout_cnt)
            self.timeout_cnt += 1
            if self.timeout_cnt > 10:
                raise Exception('Too many timeouts received!')
            return False
        
        # https://docs.google.com/document/d/1KfkZiIluXZ6mMhLWfDX1qAGbvhGRC3ZUzjVIt5FQpp4/pub
        self.timeout_cnt = 0
        data = self.sock.recv(2048)
        self._speedKmh = int(struct.unpack('<f', data[8:12])[0])
        self._absInAction = bool(data[21])
        self._tcInAction = bool(data[22])
        self._revLightsPercent = AcClient.rpms_to_revlights(int(struct.unpack('<f', data[68:72])[0]), 8000)
        self._gear = int.from_bytes(data[76:80], byteorder='little') - 1
        return True


if __name__ == "__main__":
    try:
        ev = threading.Event()
        ac = AcClient(ev, device='0005', dbus=False)
        ac.start()
        ac.join()

    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    except Exception as e:
        raise e
    finally:
        ev.set()
