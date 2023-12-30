#!/usr/bin/python3
import os
import sys
import time
import pyudev
from pyudev.pyqt5 import MonitorObserver
from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, \
    QGroupBox, QComboBox, QLabel, QSlider, QPushButton

USE_DBUS = False

if USE_DBUS:
    from pydbus import SystemBus
    bus = SystemBus()
    pdl = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite/Pedals')
    whl = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite/Wheel')
    base = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite')
else:
    import fanatec_input
    pdl = fanatec_input.CSLElitePedals()
    whl = fanatec_input.CSLEliteWheel()
    base = fanatec_input.CSLDD()
    # base = fanatec_input.CSLEliteWheelBase()

app = QApplication([])

generalBoxLayout = QHBoxLayout()
generalBox = QGroupBox("General")
generalBox.setLayout(generalBoxLayout)


btns: List[QPushButton] = []


def updateRPM():
    whl.RPM = [b.isChecked() for b in btns]


for i in range(9):
    btn = QPushButton('RPM%i' % i)
    btn.setCheckable(True)
    btn.clicked[bool].connect(updateRPM)
    generalBoxLayout.addWidget(btn)
    btns.append(btn)

tuningBox = QGroupBox("Tuning Menu")

slot = QComboBox()
slot.addItems(['None', 'Auto', '1', '2', '3', '4', '5'])
slotLabel = QLabel("&Slot:")
slotLabel.setBuddy(slot)

# FIXME: can these be exported from the driver?
TUNING_ENTRIES_RANGE = {
    'SEN': (90, 2530),
    'FF': (0, 100),
    'FEI': (0, 100),
    'FOR': (0, 120),
    'SPR': (0, 120),
    'DPR': (0, 120),

    'DRI': (-5, 0),
    'BLI': (0, 100),
    'SHO': (0, 10),

    'INT': (0, 20),
    'NIN': (0, 100),
    'FUL': (0, 100),
}


class TuningSlider(QWidget):
    def __init__(self, key, parent=None):
        super(TuningSlider, self).__init__(parent)
        self.key = key
        self.slider = QSlider(Qt.Horizontal, tuningBox)
        self.slider.setMinimum(TUNING_ENTRIES_RANGE[key][0])
        self.slider.setMaximum(TUNING_ENTRIES_RANGE[key][1])
        self.slider.valueChanged[int].connect(self.valuechange)

        self.label = QLabel("&%s:" % key)
        self.label.setBuddy(self.slider)

        self.value = QLabel()

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value)
        self.setLayout(layout)

    def valuechange(self, x, updateSlider=False):
        if updateSlider:
            self.slider.blockSignals(True)
            self.slider.setValue(x)
            self.slider.blockSignals(False)
        else:
            setattr(base, self.key, x)
        self.value.setText(str(x))


tuningBoxLayout = QVBoxLayout()
tuningSliderBoxLayout = QVBoxLayout()
tuningSliderBox = QGroupBox()
tuningSliderBox.setLayout(tuningSliderBoxLayout)

tuning_sliders = {}
for a in TUNING_ENTRIES_RANGE:
    # only add the attributes the current base offers
    if not hasattr(base, a):
        continue
    tuning_sliders[a] = TuningSlider(a)
    tuningSliderBoxLayout.addWidget(tuning_sliders[a])

tuningBoxLayout.addWidget(slotLabel)
tuningBoxLayout.addWidget(slot)
tuningBoxLayout.addWidget(tuningSliderBox)
tuningBox.setLayout(tuningBoxLayout)


def changeSlot(slot):
    if slot == 'None' or slot == 'Auto':
        base.SLOT = 1
    elif int(slot) != base.SLOT:
        base.SLOT = int(slot)
    # wait for the slot change
    time.sleep(0.2)
    for i, v in tuning_sliders.items():
        v.valuechange(getattr(base, i), updateSlider=True)


slot.activated[str].connect(changeSlot)

layout = QVBoxLayout()
layout.addWidget(generalBox)
layout.addWidget(tuningBox)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FanatecUI")
        self.setLayout(layout)
        self.setAcceptDrops(True)

        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='ftec_tuning')
        self.observer = MonitorObserver(monitor)
        self.observer.deviceEvent.connect(self.device_connected)
        monitor.start()

    def device_connected(self, device):
        # FIXME: should better check device.get('DEVPATH') in case of multiple devices
        # _pid = device.sys_name.split(':')[2].split('.')[0]
        # if _pid != base.device:
        #    return
        slot.setCurrentText(str(base.SLOT))
        changeSlot(base.SLOT)

    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls() or 'XdndFileRoller0' in mime_data.formats():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        _path = None
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            _path = mime_data.text()
        elif 'XdndFileRoller0' in mime_data.formats():
            _path = mime_data.data('XdndFileRoller0')
        if not os.path.isfile(_path):
            print("Not a file: %s" % _path)
            return
        import xml.etree.ElementTree as ET
        root = ET.parse(_path).getroot()
        tuning_menu = root.find('TuningMenu')
        if not tuning_menu:
            return
        # select the auto slot
        base.SLOT = 1
        slot.setCurrentIndex(1)
        for i in tuning_menu:
            if hasattr(base, i.tag):
                tuning_sliders[i.tag].valuechange(i.text)


win = MainWidget()
win.show()

# select current slot and fill values
slot.setCurrentIndex(base.SLOT)
for attr, v in tuning_sliders.items():
    v.valuechange(getattr(base, attr), updateSlider=True)

sys.exit(app.exec_())
