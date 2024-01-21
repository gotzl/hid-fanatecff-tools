#!/usr/bin/python
import os
import glob
import logging

from pydbus.generic import signal
from pydbus import SystemBus
from gi.repository import GLib

FANATEC_VENDOR_ID = "0EB7"
# Base IDs
CLUBSPORT_V2_WHEELBASE_DEVICE_ID = "0001"
CLUBSPORT_V25_WHEELBASE_DEVICE_ID = "0004"
CLUBSPORT_PEDALS_V3_DEVICE_ID = "183b"
PODIUM_WHEELBASE_DD1_DEVICE_ID = "0006"
PODIUM_WHEELBASE_DD2_DEVICE_ID = "0007"
CSL_ELITE_WHEELBASE_DEVICE_ID = "0E03"
CSL_ELITE_PS4_WHEELBASE_DEVICE_ID = "0005"
CSL_ELITE_PEDALS_DEVICE_ID = "6204"
CSL_DD_WHEELBASE_DEVICE_ID = "0020"
CSR_ELITE_WHEELBASE_DEVICE_ID = "0011"

# Wheel IDs
CSL_STEERING_WHEEL_P1_V2 = "0008"
CSL_ELITE_STEERING_WHEEL_WRC_ID = "0112"
CSL_ELITE_STEERING_WHEEL_MCLAREN_GT3_V2_ID = "280b"
CLUBSPORT_STEERING_WHEEL_F1_IS_ID = "1102"
CLUBSPORT_STEERING_WHEEL_FORMULA_V2_ID = "280a"
PODIUM_STEERING_WHEEL_PORSCHE_911_GT3_R_ID = "050c"


import time


def get_sysfs_base(PID):
    sysfs_pattern = (
        "/sys/module/hid_fanatec/drivers/hid:ftec_csl_elite/0003:%s:%s.*"
        % (FANATEC_VENDOR_ID, PID)
    )
    sysfs = glob.glob(sysfs_pattern)
    if len(sysfs) == 0:
        raise Exception("Device with PID=%s not found (%s)" % (PID, sysfs_pattern))
    return sysfs[0]


class FanatecWheelBase(object):
    """
    <node>
      <interface name='org.fanatec'>
        <property name="RPM" type="ab" access="write">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
      </interface>
    </node>
    """

    def __init__(self):
        pass


class CSLElite(object):
    """
    <node>
      <interface name='org.fanatec.CSLElite'>
        <property name="SLOT" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="SEN" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="FF" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="DRI" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="FEI" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="FOR" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="SPR" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="DPR" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="BLI" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="SHO" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
      </interface>
    </node>
    """

    def __init__(self):
        pass

    @staticmethod
    def get_sysfs(self, name, device=CSL_ELITE_PS4_WHEELBASE_DEVICE_ID):
        return "%s/%s" % (get_sysfs_base(CSL_ELITE_PS4_WHEELBASE_DEVICE_ID), name)

    def tuning_get(self, name):
        return int(open(self.get_sysfs(name), "r").read())

    def tuning_set(self, name, value):
        return int(open(self.get_sysfs(name), "w").write(str(value)))

    @property
    def SLOT(self):
        return self.tuning_get("SLOT")

    @SLOT.setter
    def SLOT(self, value):
        return self.tuning_set("SLOT", value)

    @property
    def SEN(self):
        return self.tuning_get("SEN")

    @SEN.setter
    def SEN(self, value):
        return self.tuning_set("SEN", value)

    @property
    def FF(self):
        return self.tuning_get("FF")

    @FF.setter
    def FF(self, value):
        return self.tuning_set("FF", value)

    @property
    def DRI(self):
        return self.tuning_get("DRI")

    @DRI.setter
    def DRI(self, value):
        return self.tuning_set("DRI", value)

    @property
    def FEI(self):
        return self.tuning_get("FEI")

    @FEI.setter
    def FEI(self, value):
        return self.tuning_set("FEI", value)

    @property
    def FOR(self):
        return self.tuning_get("FOR")

    @FOR.setter
    def FOR(self, value):
        return self.tuning_set("FOR", value)

    @property
    def SPR(self):
        return self.tuning_get("SPR")

    @SPR.setter
    def SPR(self, value):
        return self.tuning_set("SPR", value)

    @property
    def DPR(self):
        return self.tuning_get("DPR")

    @DPR.setter
    def DPR(self, value):
        return self.tuning_set("DPR", value)

    @property
    def BLI(self):
        return self.tuning_get("BLI")

    @BLI.setter
    def BLI(self, value):
        return self.tuning_set("BLI", value)

    @property
    def SHO(self):
        return self.tuning_get("SHO")

    @SHO.setter
    def SHO(self, value):
        return self.tuning_set("SHO", value)


class CSLElitePedals(object):
    """
    <node>
      <interface name='org.fanatec.CSLElite.Pedals'>
        <property name="Load" type="i" access="readwrite">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="Rumble" type="i" access="write">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
      </interface>
    </node>
    """

    def __init__(self):
        pass

    @staticmethod
    def get_sysfs(self, name, device=CSL_ELITE_PEDALS_DEVICE_ID):
        return "%s/%s" % (get_sysfs_base(device), name)

    @property
    def Load(self):
        return int(open(self.get_sysfs("load"), "r").read())

    @Load.setter
    def Load(self, value):
        return int(open(self.get_sysfs("load"), "w").write(str(value)))

    @property
    def Rumble(self):
        pass

    @Rumble.setter
    def Rumble(self, value):
        return int(open(self.get_sysfs("rumble"), "w").write(str(value)))

    PropertiesChanged = signal()


class CSLEliteWheel(object):
    """
    <node>
      <interface name='org.fanatec.CSLElite.Wheel'>
        <property name="Display" type="i" access="write">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
      </interface>
    </node>
    """

    LEDS = 9

    def __init__(self):
        pass

    @staticmethod
    def get_sysfs(name, device=CSL_ELITE_PS4_WHEELBASE_DEVICE_ID):
        return "%s/%s" % (get_sysfs_base(device), name)

    @staticmethod
    def get_sysfs_rpm(device=CSL_ELITE_PS4_WHEELBASE_DEVICE_ID):
        sysfs_base = get_sysfs_base(device)
        return "%s/leds/0003:0EB7:%s.%s::RPM" % (
            sysfs_base,
            device,
            sysfs_base.split(".")[-1],
        )

    @staticmethod
    def set_sysfs_rpm(
        rev_lights_percent: float, device=CSL_ELITE_PS4_WHEELBASE_DEVICE_ID
    ):
        leds = [
            100 * i / CSLEliteWheel.LEDS < rev_lights_percent
            for i in range(CSLEliteWheel.LEDS)
        ]
        print("leds:", leds)
        print("rev_lights_percent:", rev_lights_percent)
        value = list(
            map(
                lambda i: open(
                    "%s%i/brightness" % (CSLEliteWheel.get_sysfs_rpm(device), i[0] + 1),
                    "w",
                ).write("1" if i[1] else "0"),
                enumerate(leds),
            )
        )
        return value

    @property
    def Display(self):
        return 0

    @property
    def RPM(self):
        return 0

    @Display.setter
    def Display(self, value):
        return int(open(self.get_sysfs("display"), "w").write(str(value)))

    @RPM.setter
    def RPM(self, values):
        return set_sysfs_rpm(values)

    PropertiesChanged = signal()


class CSLP1V2Wheel(object):
    """
    <node>
      <interface name='org.fanatec.CSLElite.Wheel'>
        <property name="Display" type="i" access="write">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
      </interface>
    </node>
    """

    @staticmethod
    def get_sysfs(name, device=CSL_DD_WHEELBASE_DEVICE_ID):
        return "%s/%s" % (get_sysfs_base(device), name)

    @staticmethod
    def get_sysfs_rpm(device=CSL_DD_WHEELBASE_DEVICE_ID):
        sysfs_base = get_sysfs_base(device)
        return "%s/leds/0003:0EB7:%s.%s::RPM" % (
            sysfs_base,
            device,
            sysfs_base.split(".")[-1],
        )

    @staticmethod
    def set_sysfs_rpm(value, device=CSL_DD_WHEELBASE_DEVICE_ID):
        """
        On the CSL DD P1 V2 (and likely the BMW Wheel)
        there is a single LED light that changes colour.

        The apparent 9 sysfs LED addresses correspond
        to three different ON/OFF signals to the LED.
        The LED contains GRB (Green, Red, Blue) LEDs,
        with the possibility of 2^3 = 8 colours:
           - off,
           - green,
           - red,
           - blue,
           - yellow,
           - turquoise,
           - pink,
           - white.

        As a result we can utilise this to get nice RPM colours.

        This requires a different approach to the CSLEliteWheelBase
        class in the original code.
        """

        def get_colour(value):
            """
            In this function, we encode the _rpmLightsPercent values to
            the appropriate colour. The colours are encoded as follows:
            """
            colours = {
                0,  # off
                7,  # green
                8,  # red
                64 + 128,  # blue
                15,  # yellow
                135,  # turquoise
                136,  # pink
                255,  # white
            }
            colour_ranges = {0.3: 0, 0.5: 7, 0.7: 15, 0.8: 8, 0.95: 64 + 128, 1: 255}
            colour_names = {
                0: "off",
                7: "green",
                8: "red",
                64 + 128: "blue",
                15: "yellow",
                135: "turquoise",
                136: "pink",
                255: "white",
            }
            # find which colour you want
            # colour = 0
            if value < 0.5 * 100:  # off until 50
                colour = 0  # off
            elif value < 0.7 * 100:  # green until 70
                colour = 7
            elif value < 0.9 * 100:  # yellow until 90
                colour = 15
            elif value < 0.95 * 100:  # red until 95
                colour = 8
            else:  # now change gear with a big blue light you nerd
                colour = 64 + 128

            # return the right list of True and False
            return get_list(colour)

        def get_list(colour: int):
            my_values = list()
            for j in range(8):
                my_values.append(((colour >> j) & 1 == 1))
            return my_values

        colour_value_list = get_colour(value)
        # here we write to the appropriate addresses in the appropriate fashion
        values = list(
            map(
                lambda i: open(
                    "%s%i/brightness" % (CSLEliteWheel.get_sysfs_rpm(device), i[0] + 1),
                    "w",
                ).write("1" if i[1] else "0"),
                enumerate(colour_value_list),
            )
        )
        return values

    @property
    def Display(self):
        return 0

    @property
    def RPM(self):
        return 0

    @Display.setter
    def Display(self, value):
        return int(open(self.get_sysfs("display"), "w").write(str(value)))

    @RPM.setter
    def RPM(self, values):
        return self.set_sysfs_rpm(values)

    PropertiesChanged = signal()


def run():
    bus = SystemBus()
    r = bus.publish(
        "org.fanatec.CSLElite",
        CSLElite(),
        ("Pedals", CSLElitePedals()),
        ("Wheel", CSLEliteWheel()),
    )
    try:
        loop = GLib.MainLoop()
        loop.run()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    except Exception as e:
        raise e
    finally:
        r.unpublish()


if __name__ == "__main__":
    run()
