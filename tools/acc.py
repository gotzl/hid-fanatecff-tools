import time
import threading
import fanatec_led_server

import pyacc


class AccClient(fanatec_led_server.Client):
    def __init__(self, ev, dbus=True, device=None, display='gear'): 
        fanatec_led_server.Client.__init__(self, ev, dbus, device, display)
        self.physics = None
        self.mmap_check_cnt = 0

    def prerun(self):
        while not self.ev.isSet():
            try:
                self.physics: pyacc.SPageFilePhysics = pyacc.get_mapped_object('acpmf_physics')
                break
            except FileNotFoundError as e:
                time.sleep(1)

    def tick(self):
        if not super().tick():
            return False
            
        # every once in a while check if shared files are still availabl
        if self.mmap_check_cnt > 10:
            self.mmap_check_cnt = 0
            try:
                pyacc.get_mapped_object('acpmf_physics')
            except FileNotFoundError as e:
                return False
        self.mmap_check_cnt += 1
        return True

    @property
    def revLightsPercent(self):
        return AccClient.rpms_to_revlights(self.physics.rpms, self.physics.currentMaxRpm)

    @property
    def tcInAction(self):
        return self.physics.tc > 0

    @property
    def absInAction(self):
        return self.physics.abs > 0
        
    @property
    def speedKmh(self):
        return self.physics.speedKmh

    @property
    def gear(self):
        return self.physics.gear - 1


if __name__ == "__main__":
    try:
        ev = threading.Event()
        acc = AccClient(ev, device='0005', dbus=False)
        acc.start()
        acc.join()

    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    except Exception as e:
        raise e
    finally:
        ev.set()
