#!/usr/bin/python3

from pydbus import SystemBus
bus = SystemBus()
pdl = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite/Pedals')
print(pdl.Load)


whl = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite/Wheel')
# print(whl.Display)
# print(whl.RPM)
