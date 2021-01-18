#!/usr/bin/python3

from pydbus import SystemBus
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout,\
    QGroupBox, QComboBox, QLabel, QSlider, QPushButton

bus = SystemBus()
pdl = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite/Pedals')
whl = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite/Wheel')
base = bus.get('org.fanatec.CSLElite', '/org/fanatec/CSLElite')

app = QApplication([])

generalBoxLayout = QHBoxLayout()
generalBox = QGroupBox("General")
generalBox.setLayout(generalBoxLayout)

btns = []
def updateRPM():
    whl.RPM = [b.isChecked() for b in btns]

for i in range(9):
    btn = QPushButton('RPM%i'%i)
    btn.setCheckable(True)
    btn.clicked[bool].connect(updateRPM)
    generalBoxLayout.addWidget(btn)
    btns.append(btn)


tuningBox = QGroupBox("Tuning Menu")

slot = QComboBox()
slot.addItems(['1','2','3','4','5'])
slotLabel = QLabel("&Slot:")
slotLabel.setBuddy(slot)

TUNING_ENTRIES = ['SEN', 'FF', 'DRI', 'FEI', 'FOR', 'SPR', 'DPR', 'BLI', 'SHO']
TUNING_ENTRIES_RANGE = {
    'SEN': (9,108),
    'FF': (0,100),
    'DRI': (-5, 0),
    'FEI': (0,100),
    'FOR': (0, 10),
    'SPR': (0, 10),
    'DPR': (0, 10),
    'BLI': (0, 100),
    'SHO': (0, 10),
}

class TuningSlider(QWidget):
    def __init__(self, key, parent=None):
        super(TuningSlider, self).__init__(parent)
        self.key = key
        self.slider = QSlider(Qt.Horizontal, tuningBox)
        self.slider.setMinimum(TUNING_ENTRIES_RANGE[i][0])
        self.slider.setMaximum(TUNING_ENTRIES_RANGE[i][1])
        self.slider.valueChanged[int].connect(self.valuechange)

        self.label = QLabel("&%s:"%key)
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
        else: setattr(base, self.key, x)
        self.value.setText(str(x))

tuningBoxLayout = QVBoxLayout()
tuningSliderBoxLayout = QVBoxLayout()
tuningSliderBox = QGroupBox()
tuningSliderBox.setLayout(tuningSliderBoxLayout)

tuning_sliders = {}
for i in TUNING_ENTRIES:
    tuning_sliders[i] = TuningSlider(i)
    tuningSliderBoxLayout.addWidget(tuning_sliders[i])

tuningBoxLayout.addWidget(slotLabel)
tuningBoxLayout.addWidget(slot)
tuningBoxLayout.addWidget(tuningSliderBox)
tuningBox.setLayout(tuningBoxLayout)

def changeSlot(slot):
    base.SLOT = int(slot)
    for i, v in tuning_sliders.items():
        v.valuechange(getattr(base, i), updateSlider=True)

slot.activated[str].connect(changeSlot)

layout = QVBoxLayout()
layout.addWidget(generalBox)
layout.addWidget(tuningBox)

win = QWidget()
win.setLayout(layout)
win.show()

changeSlot('1')

app.exec_()