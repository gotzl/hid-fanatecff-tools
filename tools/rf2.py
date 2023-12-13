import os
import mmap
import time
import math
import threading
import fanatec_led_server

from pyRfactor2SharedMemory import rF2data


class RF2Client(fanatec_led_server.Client):
    def __init__(self, ev, dbus=True, device=None, display='gear'):
        fanatec_led_server.Client.__init__(self, ev, dbus, device, display)
        self._scoring = None
        self._tele = None
        self._player_index = None
        self.telemetry = None
        self.mmap_check_cnt = 0
        self.mVersionUpdateBegin = None

    @staticmethod
    def _get_mmap(name):
        with open('/dev/shm/%s' % name, 'r+b') as f:
            return mmap.mmap(f.fileno(), 0)

    def _get_player_index(self):
        for idx, vehicle in enumerate(self._scoring.mVehicles):
            if vehicle.mIsPlayer:
                return idx
        return 0

    def prerun(self):
        while not self.ev.is_set():
            try:
                self._scoring = rF2data.rF2Scoring.from_buffer(RF2Client._get_mmap("$rFactor2SMMP_Scoring$"))
                self._player_index = self._get_player_index()
                # get telemetry for player
                self._tele = rF2data.rF2Telemetry.from_buffer(RF2Client._get_mmap("$rFactor2SMMP_Telemetry$"))
                self.telemetry = self._tele.mVehicles[self._player_index]
                # check if the data is updating, if so, break out of the prerun loop
                if self.mVersionUpdateBegin is not None and\
                        self.mVersionUpdateBegin != self._scoring.mVersionUpdateBegin:
                    self.mVersionUpdateBegin = self._scoring.mVersionUpdateBegin
                    break
                self.mVersionUpdateBegin = self._scoring.mVersionUpdateBegin
            except FileNotFoundError as e:
                pass
            time.sleep(1)

    def tick(self):
        if not super().tick():
            return False

        # every once in a while check if shared files are still available
        # and player index is still the same
        if self.mmap_check_cnt > 10:
            self.mmap_check_cnt = 0

            if not os.path.isfile('/dev/shm/$rFactor2SMMP_Scoring$'):
                return False

            # check if the data is updating, if not, break out of the tick loop
            if self.mVersionUpdateBegin == self._scoring.mVersionUpdateBegin:
                return False

            self.mVersionUpdateBegin = self._scoring.mVersionUpdateBegin

            # check player index
            if not self._scoring.mVehicles[self._player_index].mIsPlayer:
                # index changed, look up the new index
                self._player_index = self._get_player_index()
                self.telemetry = self._tele.mVehicles[self._player_index]

        self.mmap_check_cnt += 1
        return True

    @property
    def revLightsPercent(self):
        return RF2Client.rpms_to_revlights(self.telemetry.mEngineRPM, self.telemetry.mEngineMaxRPM)

    @property
    def tcInAction(self):
        return self.telemetry.mFilteredThrottle != self.telemetry.mUnfilteredThrottle

    @property
    def absInAction(self):
        return self.telemetry.mFilteredBrake != self.telemetry.mUnfilteredBrake

    @property
    def speedKmh(self):
        return 3.6 * math.sqrt(self.telemetry.mLocalVel.x**2 + self.telemetry.mLocalVel.y**2 + self.telemetry.mLocalVel.z**2)

    @property
    def gear(self):
        return self.telemetry.mGear


if __name__ == "__main__":
    try:
        ev = threading.Event()
        rf2 = RF2Client(ev, device='0005', dbus=False)
        rf2.start()
        rf2.join()

    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    except Exception as e:
        raise e
    finally:
        ev.set()
