import os
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from layouts import file_list, track_list, video_part
from layouts.tracer import Tracer
from layouts.video_part import DetectState


class MyApp(QWidget):
    detectValue = {'unit': 1.0, 'space': 10.0, 'len': 3.0, 'size': 100.0}
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout1 = QHBoxLayout()
        self.setLayout(layout1)
        if getattr(sys, 'frozen', False):
            self.my_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.my_path = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(os.path.join(self.my_path,'icon.ico')):
            self.setWindowIcon(QtGui.QIcon(os.path.join(self.my_path,'icon.ico')))

        self.vpart = video_part.VideoPart()
        self.vpart.onDetect.connect(self.doDetect)
        self.vpart.detectValueChange.connect(self.detectValueChange)
        self.flist = file_list.FileList()
        first_file_name = ""
        if len(self.flist.files) > 0:
            first_file_name = self.flist.files[0]
        self.vpart.setButtonState(len(self.flist.files), first_file_name)
        self.flist.itemSelected.connect(self.fileSelected)
        self.flist.listCountChanged.connect(self.vpart.setButtonState)
        self.tlist = track_list.TrackList()
        self.tlist.itemSelected.connect(self.trackSelected)

        layout1.addLayout(self.vpart, 4)
        layout1.addLayout(self.flist, 1)
        layout1.addLayout(self.tlist, 1)

        self.setWindowTitle('CCTV tracer')
        self.move(300,300)
        self.show()
        self.resize(1024,600)
        self.vpart.set_player()
        self.vpart.openRect()
        self.vpart.setting_dialog.openSettings()

    def detectValueChange(self, key, value):
        print(key, value)
        self.detectValue[key] = value

    def fileSelected(self, item):
        self.vpart.changeFile(item)

    def trackSelected(self, item):
        self.vpart.setTrack(item)

    def progressChanged(self, value):
        self.vpart.progrss_bar.setValue(int(value))
        if int(value) >= 100:
            self.vpart.progrss_bar.setEnabled(False)

    def trackAdded(self, track):
        self.tlist.items.append(track)
        self.tlist.list1.addItem(track.text)

    def trackEndChanged(self, end):
        self.tlist.items[len(self.tlist.items)-1].end = end
        self.tlist.changeText(len(self.tlist.items)-1, end)

    def doDetect(self, rect, before_state, state):
        self.vpart.progrss_bar.setMaximum(100)
        self.vpart.progrss_bar.setMinimum(0)
        if before_state == DetectState.Before and state == DetectState.OnDetect:
            self.vpart.progrss_bar.setValue(0)
            self.tracer = Tracer(self, self.flist.files, rect, self.vpart.video.video.boundingRect(), self.detectValue)
            self.tracer.progressChanged.connect(self.progressChanged)
            self.tracer.trackAdded.connect(self.trackAdded)
            self.tracer.trackEndChanged.connect(self.trackEndChanged)
            self.tracer.drawContours.connect(self.vpart.video.drawImage)
            self.tracer.traceEnd.connect(self.vpart.traceEnd)
            self.tracer.start()
        elif before_state == DetectState.OnDetect and state == DetectState.Pause:
            self.tracer.pause = True
        elif before_state == DetectState.Pause and state == DetectState.OnDetect:
            self.tracer.pause = False
        elif state == DetectState.Before:
            self.tracer.stop()

    def keyPressEvent(self, e):
        modifiers = int(e.modifiers())
        if e.key() == Qt.Key_S:
            if modifiers == Qt.ShiftModifier:
                self.vpart.playSpeedChanged(self.vpart.playSpeed - 1.0)
            else:
                self.vpart.playSpeedChanged(self.vpart.playSpeed + 1.0)
        elif e.key() == Qt.Key_Less:
            self.vpart.moveFrameAsSecond(-1.0)
        elif e.key() == Qt.Key_Right:
            self.vpart.moveFrameAsSecond(1.0)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())