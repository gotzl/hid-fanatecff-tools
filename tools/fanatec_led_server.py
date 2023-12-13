#!/usr/bin/python3
import sys
import os
import time
import threading

LEDS = 9

def set_leds(values):
    global wheel
    wheel.RPM = values

def set_display(value):
    global wheel
    wheel.Display = value

def set_pedals_rumble(abs, tc):
    global pedals
    pedals.rumble = '%i'%( (0xff if tc else 0) << 16 | (0xff if abs else 0) << 8 )

# clear leds and display
def clear():
    set_leds([False]*9)
    set_display(-1)


class Client(threading.Thread):
    def __init__(self, ev, dbus=True, device=None, display='gear'): 
        threading.Thread.__init__(self)
        if not dbus and device is None:
            raise Exception('If dbus is not used, a device must be specified!')
        self.ev = ev
        self.dbus = dbus
        self.device = device
        self.display = display
        self.rate = 10
        self._revLightsPercent = 0
        self._tcInAction = 0
        self._absInAction = 0
        self._speedKmh = 0
        self._gear = 0
        self._suggestedGear = 0

    def prerun(self):
        pass

    def postrun(self):
        pass

    def tick(self):
        time.sleep(1/self.rate)
        return True

    @staticmethod
    def rpms_to_revlights(rpms, maxrpm, offset=-1):
        if offset < 0: offset = maxrpm-2000
        return (rpms - offset) / ((maxrpm*0.95) - offset)
        
    @property
    def revLightsPercent(self):
        return self._revLightsPercent

    @property
    def tcInAction(self):
        return self._tcInAction

    @property
    def absInAction(self):
        return self._absInAction

    @property
    def speedKmh(self):
        return self._speedKmh

    @property
    def gear(self):
        return self._gear

    @property
    def suggestedGear(self):
        return self._suggestedGear

    def run(self):
        while not self.ev.isSet():
            self._do_run()

    def _do_run(self):
        print(self, 'waiting for game connection')

        self.prerun()

        if not self.dbus:
            sys.path.append('../dbus')
            import fanatec_input
            while not self.ev.isSet():
                try:
                    fanatec_input.get_sysfs_base(self.device)
                except Exception as e:
                    print(e)
                    self.postrun()
                    print(self, 'finished.')
                    time.sleep(1)
                    return

                print('Found sysfs for device', self.device)

                try:
                    display = fanatec_input.CSLEliteWheel.get_sysfs('display', self.device)
                    pedals = fanatec_input.CSLEliteWheel.get_sysfs('rumble', self.device)
                    if not os.path.isfile(display): display = None
                    if not os.path.isfile(pedals): pedals = None
                except:
                    pass
                finally:
                    break

        if not self.ev.isSet():
            print(self, 'connected')

        rpms_maxed = 0
        while not self.ev.isSet():
            if not self.tick():
                break

            if self.revLightsPercent > 0.95:
                rpms_maxed += 1
            else:
                rpms_maxed = 0

            if rpms_maxed % 2 == 1:
                leds = [False]*9
            else:
                leds = [i/LEDS < self.revLightsPercent for i in range(LEDS)]

            if self.dbus:
                set_leds(leds)
                set_display(eval('self.%s'%self.display))
                set_pedals_rumble(self.absInAction, self.tcInAction)
            else:
                rumble = '%i'%( (0xff if self.tcInAction else 0) << 16 | (0xff if self.absInAction else 0) << 8 )
                try:
                    if display is not None:
                        display_val = str(self.speedKmh)
                        if self.display == 'gear':
                            gear = {-1: "R", 0: "N"}
                            display_val = gear[self.gear] if self.gear in gear else str(self.gear)
                        open(display, 'w').write(display_val)

                    if pedals is not None: open(pedals, 'w').write(str(rumble))
                    fanatec_input.CSLEliteWheel.set_sysfs_rpm(leds, self.device)
                except FileNotFoundError:
                    # probably device got disconnected
                    break

        self.postrun()
        print(self, 'finished.')


if __name__ == "__main__":
    from ac import AcClient
    from acc import AccClient
    from f1_2020 import F12020Client
    from rf2 import RF2Client
    from wrc import WrcClient

    import argparse
    parser = argparse.ArgumentParser(description='Advanced functions for fanatec wheels with ACC')
    parser.add_argument('--dbus', action='store_true', help='Use dbus for communicating commands to the wheel.')
    parser.add_argument('--device', type=str, help='PID of the wheel (ClubSportv2 \'0001\', ClubSportv2.5 \'0004\', ...)', default='0005')
    parser.add_argument('--display', type=str, help='property that is shown on display (gear, speedKmh)', default='gear')
    args = parser.parse_args()

    if args.dbus:
        bus = SystemBus()
        wheel = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite/Wheel')
        pedals = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite/Pedals')

    try:
        ev = threading.Event()
        
        threads = []
        for typ in [F12020Client, AcClient, AccClient, RF2Client, WrcClient]:
            threads.append(typ(ev, args.dbus, args.device, args.display))

        for thread in threads:    
            thread.start()
            
        # run as long as the client threads are running, or CTRL+C
        print("Running ...")

        while True:
            died = []
            for thread in threads:
                if not thread.is_alive():
                    print('Thread \'%s\' stopped.'%thread)
                    died.append(thread)
            threads = [t for t in threads if t not in died]
            if len(threads) == 0: break
            time.sleep(1)
            
    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    except Exception as e:
        raise e
    finally:
        ev.set()
        if args.dbus:
            clear()
        
