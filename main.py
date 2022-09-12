import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *

from layouts import file_list, track_list, video_part


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout1 = QHBoxLayout()
        self.setLayout(layout1)

        vpart = video_part.VideoPart()
        vpart.onDetectOption.connect(self.enableLists)
        self.flist = file_list.FileList()
        self.tlist = track_list.TrackList()

        layout1.addLayout(vpart, 4)
        layout1.addLayout(self.flist, 1)
        layout1.addLayout(self.tlist, 1)

        self.setWindowTitle('CCTV tracer')
        self.move(300,300)
        self.show()
        self.resize(1024,600)
        vpart.set_player()


    def enableLists(self, value):
        self.flist.setEnable(value)
        self.tlist.setEnable(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())