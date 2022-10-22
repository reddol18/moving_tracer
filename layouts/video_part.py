import math
import os
import sys
from enum import Enum

from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar

from layouts.my_slider import MySlider
from layouts.options import Options
from layouts.video_widget import VideoWidget


class DetectState(Enum):
    Before = 0
    OnDetect = 1
    Pause = 2


class VideoPart(QVBoxLayout):
    onDetect = pyqtSignal(QRectF, DetectState, DetectState)
    detectValueChange = pyqtSignal(str, float)
    onPlay = False
    playSpeed = 1.0
    detectState = DetectState.Before
    first_file_name = ""

    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            self.my_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.my_path = os.path.dirname(os.path.abspath(__file__))
        label = QLabel('재생부')
        self.video = VideoWidget()
        self.video.boxRectChanged.connect(self.saveRect)
        self.addWidget(label, 1)
        self.addWidget(self.video, 18)
        self.addLayout(self.control_part(), 1)
        self.addLayout(self.detect_part(), 1)
        self.setting_dialog = Options()
        self.setting_dialog.speedChanged.connect(self.playSpeedChanged)
        self.setting_dialog.frameUnitChanged.connect(self.frameUnitChanged)
        self.setting_dialog.frameSpaceChanged.connect(self.frameSpaceChanged)
        self.setting_dialog.frameLenChanged.connect(self.frameLenChanged)
        self.setting_dialog.sizeChanged.connect(self.sizeChanged)

    def set_player(self):
        self.video.set_player()
        self.video.stateChanged.connect(self.stateChanged)
        self.video.positionChanged.connect(self.positionChanged)
        self.video.durationChanged.connect(self.durationChanged)
        self.video.error.connect(self.errorFunc)

    def playSpeedChanged(self, value):
        if value > 0.0 and value <= 10.0:
            self.playSpeed = value
            self.speed_label.setText(str(value))
            self.video.setPlaySpeed(value)

    def frameUnitChanged(self, value):
        if value > 0.0 and value <= 10.0:
            self.detectValueChange.emit("unit", value)

    def frameSpaceChanged(self, value):
        if value >= 1.0 and value <= 100.0:
            self.detectValueChange.emit("space", value)

    def frameLenChanged(self, value):
        if value >= 1.0 and value <= 100.0:
            self.detectValueChange.emit("len", value)

    def sizeChanged(self, value):
        if value >= 10.0 and value <= 1000.0:
            self.detectValueChange.emit("size", value)

    def stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText('일시정지')
            self.onPlay = True
        else:
            self.play_btn.setText('재생')
            self.onPlay = False

    def getTimeTextByPosition(self, position):
        as_second = position / 1000.0
        second_text = int(as_second % 60)
        minute_text = math.floor(as_second / 60.0)
        return str(minute_text) + ":" + str(second_text)

    def positionChanged(self, position):
        print("position changed", position)
        self.time_label.setText(self.getTimeTextByPosition(position))
        self.track_bar.setValue(position)

    def durationChanged(self, duration):
        self.track_bar.setMaximum(duration)
        self.track_bar.setRange(0, duration)

    def errorFunc(self, error):
        print(error)

    def control_part(self):
        layout = QHBoxLayout()
        self.play_btn = QPushButton('재생')
        self.play_btn.clicked.connect(self.play)
        self.play_btn.setEnabled(False)

        self.time_label = QLabel("00:00")

        self.track_bar = MySlider(Qt.Horizontal)
        self.track_bar.setRange(0,0)
        self.track_bar.sliderMoved.connect(self.setPosition)

        layout.addWidget(self.play_btn)
        layout.addWidget(self.time_label)
        layout.addWidget(self.track_bar)
        return layout

    def setPosition(self, position):
        print("position manually changed")
        self.time_label.setText(self.getTimeTextByPosition(position))
        self.video.setPosition(position)

    def moveFrameAsSecond(self, diff):
        current_pos = self.track_bar.value()
        want_pos = current_pos + (diff * 1000.0)
        if want_pos < 0:
            want_pos = 0
        elif want_pos > self.track_bar.maximum():
            want_pos = self.track_bar.maximum()
        self.setPosition(want_pos)

    def play(self):
        if self.onPlay == True:
            self.detect_btn.setEnabled(True)
            self.video.pause()
        else:
            self.detect_btn.setEnabled(False)
            self.video.play()

    def detect_part(self):
        layout = QHBoxLayout()
        self.setting_btn = QPushButton('설정')
        self.setting_btn.clicked.connect(self.setting_open)

        self.speed_label = QLabel(str(1.0))

        self.detect_btn = QPushButton('포착시작')
        self.detect_btn.clicked.connect(self.detect)

        self.stop_detect_btn = QPushButton('포착종료')
        self.stop_detect_btn.clicked.connect(self.stop_detect)
        self.stop_detect_btn.setEnabled(False)

        self.progrss_bar = QProgressBar()
        layout.addWidget(self.setting_btn)
        layout.addWidget(self.speed_label)
        layout.addWidget(self.detect_btn)
        layout.addWidget(self.stop_detect_btn)
        layout.addWidget(self.progrss_bar)
        return layout

    def traceEnd(self):
        self.setDetectState(DetectState.Before)

    def setting_open(self):
        self.setting_dialog.show()

    def changeFile(self, filename):
        self.play_btn.setEnabled(True)
        self.video.setFile(filename)
        self.video.makeRect()

    def setTrack(self, item):
        try:
            self.video.setFile(item.filename)
        finally:
            self.detect_btn.setEnabled(False)
            self.video.playInRange(item.start, item.end)
            self.track_bar.setPartialRange(item.start, item.end)

    def setDetectState(self, state):
        self.detectState = state
        if state == DetectState.OnDetect:
            self.detect_btn.setText("포착 일시정지")
            self.play_btn.setEnabled(False)
            self.setting_btn.setEnabled(False)
            self.track_bar.setEnabled(False)
            self.detect_btn.setEnabled(True)
            self.progrss_bar.setEnabled(True)
            self.stop_detect_btn.setEnabled(True)
        elif state == DetectState.Pause:
            self.detect_btn.setText("포착 계속")
            self.play_btn.setEnabled(True)
            self.track_bar.setEnabled(True)
            self.detect_btn.setEnabled(True)
            self.progrss_bar.setEnabled(True)
            self.stop_detect_btn.setEnabled(True)
        elif state == DetectState.Before:
            self.detect_btn.setText("포착 시작")
            self.play_btn.setEnabled(True)
            self.setting_btn.setEnabled(True)
            self.track_bar.setEnabled(True)
            self.detect_btn.setEnabled(True)
            self.progrss_bar.setEnabled(False)
            self.stop_detect_btn.setEnabled(False)

    def setButtonState(self, count, first_file_name):
        self.first_file_name = first_file_name
        if count > 0:
            self.detect_btn.setEnabled(True)
        else:
            self.detect_btn.setEnabled(False)

    def stop_detect(self):
        self.setDetectState(DetectState.Before)
        rect = self.video.getBoxRect()
        self.onDetect.emit(rect, DetectState.OnDetect, DetectState.Before)

    def detect(self):
        if self.detectState == DetectState.Before:
            self.changeFile(self.first_file_name)
            rect = self.video.getBoxRect()
            self.setDetectState(DetectState.OnDetect)
            self.onDetect.emit(rect, DetectState.Before, DetectState.OnDetect)
        elif self.detectState == DetectState.OnDetect:
            rect = self.video.getBoxRect()
            self.setDetectState(DetectState.Pause)
            self.onDetect.emit(rect, DetectState.OnDetect, DetectState.Pause)
        elif self.detectState == DetectState.Pause:
            rect = self.video.getBoxRect()
            self.setDetectState(DetectState.OnDetect)
            self.onDetect.emit(rect, DetectState.Pause, DetectState.OnDetect)

    def saveRect(self, rect):
        print("SaveRect")
        f = open(os.path.join(self.my_path,"mt_rect.txt"), 'w')
        f.write(str(rect.left()) + "\n")
        f.write(str(rect.top()) + "\n")
        f.write(str(rect.right()) + "\n")
        f.write(str(rect.bottom()) + "\n")
        self.video.rate_rect = rect
        f.close()

    def openRect(self):
        if os.path.isfile(os.path.join(self.my_path,"mt_rect.txt")):
            f = open(os.path.join(self.my_path,"mt_rect.txt"), "r")
            lines = f.readlines()
            if len(lines) >= 4:
                temp = lines[0].strip()
                x = float(temp)
                temp = lines[1].strip()
                t = float(temp)
                temp = lines[2].strip()
                r = float(temp)
                temp = lines[3].strip()
                b = float(temp)
                self.video.setDetectRect(QRectF(x,t,r-x,b-t))
            f.close()