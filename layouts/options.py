import os
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QDoubleSpinBox, QPushButton


class Options(QDialog):
    speedChanged = pyqtSignal(float)
    frameUnitChanged = pyqtSignal(float)
    frameSpaceChanged = pyqtSignal(float)
    frameLenChanged = pyqtSignal(float)
    sizeChanged = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            self.my_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.my_path = os.path.dirname(os.path.abspath(__file__))
        self.setModal(True)
        self.setWindowTitle("설정")
        self.optsLayout = QVBoxLayout()

        self.speedLayout = QHBoxLayout()
        self.speedLabel = QLabel('배속지정')
        self.speedSetter = QDoubleSpinBox()
        self.speedSetter.setMinimum(0.1)
        self.speedSetter.setMaximum(10.0)
        self.speedSetter.setSingleStep(0.1)
        self.speedSetter.setValue(1.0)
        self.speedSetter.valueChanged.connect(self.valueChangedFunc)
        self.speedLayout.addWidget(self.speedLabel, 2)
        self.speedLayout.addWidget(self.speedSetter, 8)

        self.frameUnitLayout = QHBoxLayout()
        self.frameUnitLabel = QLabel('포착간격(초)')
        self.frameUnitSetter = QDoubleSpinBox()
        self.frameUnitSetter.setMinimum(0.1)
        self.frameUnitSetter.setMaximum(10.0)
        self.frameUnitSetter.setSingleStep(0.1)
        self.frameUnitSetter.setValue(1.0)
        self.frameUnitSetter.valueChanged.connect(self.valueChangedFunc2)
        self.frameUnitLayout.addWidget(self.frameUnitLabel, 2)
        self.frameUnitLayout.addWidget(self.frameUnitSetter, 8)

        self.frameSpaceLayout = QHBoxLayout()
        self.frameSpaceLabel = QLabel('포착트랙간 공백(초)')
        self.frameSpaceSetter = QDoubleSpinBox()
        self.frameSpaceSetter.setMinimum(1.0)
        self.frameSpaceSetter.setMaximum(100.0)
        self.frameSpaceSetter.setSingleStep(1.0)
        self.frameSpaceSetter.setValue(10.0)
        self.frameSpaceSetter.valueChanged.connect(self.valueChangedFunc3)
        self.frameSpaceLayout.addWidget(self.frameSpaceLabel, 3)
        self.frameSpaceLayout.addWidget(self.frameSpaceSetter, 7)

        self.frameLenLayout = QHBoxLayout()
        self.frameLenLabel = QLabel('포착트랙 최소길이(초)')
        self.frameLenSetter = QDoubleSpinBox()
        self.frameLenSetter.setMinimum(1.0)
        self.frameLenSetter.setMaximum(100.0)
        self.frameLenSetter.setSingleStep(1.0)
        self.frameLenSetter.setValue(3.0)
        self.frameLenSetter.valueChanged.connect(self.valueChangedFunc4)
        self.frameLenLayout.addWidget(self.frameLenLabel, 3)
        self.frameLenLayout.addWidget(self.frameLenSetter, 7)

        self.sizeLayout = QHBoxLayout()
        self.sizeLabel = QLabel('포착크기')
        self.sizeSetter = QDoubleSpinBox()
        self.sizeSetter.setMinimum(10.0)
        self.sizeSetter.setMaximum(1000.0)
        self.sizeSetter.setSingleStep(10.0)
        self.sizeSetter.setValue(100.0)
        self.sizeSetter.valueChanged.connect(self.valueChangedFunc5)
        self.sizeLayout.addWidget(self.sizeLabel, 2)
        self.sizeLayout.addWidget(self.sizeSetter, 8)

        self.btnsLayout = QHBoxLayout()
        self.defaultBtn = QPushButton("기본값으로 지정")
        self.defaultBtn.clicked.connect(self.setDefault)
        self.btnsLayout.addWidget(self.defaultBtn, 2)

        self.optsLayout.addLayout(self.speedLayout)
        self.optsLayout.addLayout(self.frameUnitLayout)
        self.optsLayout.addLayout(self.frameSpaceLayout)
        self.optsLayout.addLayout(self.frameLenLayout)
        self.optsLayout.addLayout(self.sizeLayout)
        self.optsLayout.addLayout(self.btnsLayout)

        self.setLayout(self.optsLayout)

    def setDefault(self):
        self.speedSetter.setValue(1.0)
        self.frameUnitSetter.setValue(1.0)
        self.frameSpaceSetter.setValue(10.0)
        self.frameLenSetter.setValue(3.0)
        self.sizeSetter.setValue(100.0)

    def valueChangedFunc(self):
        self.speedChanged.emit(self.speedSetter.value())

    def valueChangedFunc2(self):
        self.frameUnitChanged.emit(self.frameUnitSetter.value())

    def valueChangedFunc3(self):
        self.frameSpaceChanged.emit(self.frameSpaceSetter.value())

    def valueChangedFunc4(self):
        self.frameLenChanged.emit(self.frameLenSetter.value())

    def valueChangedFunc5(self):
        self.sizeChanged.emit(self.sizeSetter.value())

    def closeEvent(self, event):
        self.saveSettings()
        super(Options, self).closeEvent(event)

    def saveSettings(self):
        f = open(os.path.join(self.my_path,"mt_settings.txt"), 'w')
        f.write(str(self.speedSetter.value()) + "\n")
        f.write(str(self.frameUnitSetter.value()) + "\n")
        f.write(str(self.frameSpaceSetter.value()) + "\n")
        f.write(str(self.frameLenSetter.value()) + "\n")
        f.write(str(self.sizeSetter.value()))
        f.close()

    def openSettings(self):
        if os.path.isfile(os.path.join(self.my_path,"mt_settings.txt")):
            f = open(os.path.join(self.my_path,"mt_settings.txt"), "r")
            lines = f.readlines()
            if len(lines) >= 5:
                temp = lines[0].strip()
                self.speedSetter.setValue(float(temp))
                temp = lines[1].strip()
                self.frameUnitSetter.setValue(float(temp))
                temp = lines[2].strip()
                self.frameSpaceSetter.setValue(float(temp))
                temp = lines[3].strip()
                self.frameLenSetter.setValue(float(temp))
                temp = lines[4].strip()
                self.sizeSetter.setValue(float(temp))
                self.valueChangedFunc()
                self.valueChangedFunc2()
                self.valueChangedFunc3()
                self.valueChangedFunc4()
                self.valueChangedFunc5()
            f.close()
