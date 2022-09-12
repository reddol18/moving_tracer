from PyQt5.QtCore import Qt, QDir, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QProgressBar, QWidget

from layouts.video_widget import VideoWidget


class VideoPart(QVBoxLayout):
    onDetectOption = pyqtSignal(bool)
    onPlay = False

    def __init__(self):
        super().__init__()
        label = QLabel('재생부')
        self.video = VideoWidget()
        self.addWidget(label, 1)
        self.addWidget(self.video, 18)
        self.addLayout(self.control_part(), 1)
        self.addLayout(self.detect_part(), 1)

    def set_player(self):
        self.video.set_player()
        self.video.stateChanged.connect(self.stateChanged)
        self.video.positionChanged.connect(self.positionChanged)
        self.video.durationChanged.connect(self.durationChanged)
        self.video.error.connect(self.errorFunc)

    def stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText('일시정지')
            self.onPlay = True
        else:
            self.play_btn.setText('재생')
            self.onPlay = False

    def positionChanged(self, position):
        self.track_bar.setValue(position)

    def durationChanged(self, duration):
        self.track_bar.setRange(0, duration)

    def errorFunc(self, error):
        print(error)

    def control_part(self):
        layout = QHBoxLayout()
        self.play_btn = QPushButton('재생')
        self.play_btn.clicked.connect(self.play)

        self.track_bar = QSlider(Qt.Horizontal)
        self.track_bar.setRange(0,0)
        self.track_bar.sliderMoved.connect(self.setPosition)

        layout.addWidget(self.play_btn)
        layout.addWidget(self.track_bar)
        return layout

    def setPosition(self, position):
        self.video.setPosition(position)

    def play(self):
        if self.onPlay == True:
            self.video.pause()
        else:
            self.video.play()

    def detect_part(self):
        layout = QHBoxLayout()
        self.detect_option_btn = QPushButton('포착지정')
        self.detect_option_btn.clicked.connect(self.detect_option)

        self.detect_btn = QPushButton('포착')
        self.progrss_bar = QProgressBar()
        layout.addWidget(self.detect_option_btn)
        layout.addWidget(self.detect_btn)
        layout.addWidget(self.progrss_bar)
        return layout

    def detect_option(self):
        if self.detect_option_btn.text() == '포착지정':
            self.play_btn.setEnabled(False)
            self.track_bar.setEnabled(False)
            self.detect_btn.setEnabled(False)
            self.progrss_bar.setEnabled(False)
            self.detect_option_btn.setText('지정완료')
            self.onDetectOption.emit(False)
            self.video.setDetectOptionEnable(True)
        else:
            self.play_btn.setEnabled(True)
            self.track_bar.setEnabled(True)
            self.detect_btn.setEnabled(True)
            self.progrss_bar.setEnabled(True)
            self.detect_option_btn.setText('포착지정')
            self.onDetectOption.emit(True)
            self.video.setDetectOptionEnable(False)
