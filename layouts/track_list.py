import math
import os
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QListWidget, QVBoxLayout, QPushButton, QAbstractItemView


class TrackItem:
    filename = ''
    text = ''
    start = 0
    end = 0

    def start_min_sec_text(self):
        second_text = int(self.start % 60)
        minute_text = math.floor(self.start / 60.0)
        return str(minute_text) + ":" + str(second_text)

    def end_min_sec_text(self):
        second_text = int(self.end % 60)
        minute_text = math.floor(self.end / 60.0)
        return str(minute_text) + ":" + str(second_text)

    def __init__(self, filename, start, end):
        self.filename = filename
        temp = filename.split('/')
        self.text = " {}~{}-".format(self.start_min_sec_text(), self.end_min_sec_text()) + temp[len(temp)-1]
        self.start = start
        self.end = end

    def apply_text(self):
        temp = self.filename.split('/')
        self.text = " {}~{}-".format(self.start_min_sec_text(), self.end_min_sec_text()) + temp[len(temp)-1]

    def get_text_for_file(self):
        return self.filename + "," + str(self.start) + "," + str(self.end)

    def parse_text_for_file(self, text):
        temp = text.split(",")
        self.filename = temp[0]
        self.start = int(temp[1])
        self.end = int(temp[2])
        self.apply_text()

class TrackList(QVBoxLayout):
    itemSelected = pyqtSignal(TrackItem)
    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            self.my_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.my_path = os.path.dirname(os.path.abspath(__file__))
            
        label = QLabel('타임트랙 리스트')
        self.items = []

        self.save_btn = QPushButton('리스트 저장')
        self.save_btn.clicked.connect(self.saveFileList)

        self.delete_btn = QPushButton('삭제')
        self.delete_btn.clicked.connect(self.delete_file)

        self.list1 = QListWidget()
        self.list1.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list1.itemDoubleClicked.connect(self.itemSelectedFunc)

        self.addWidget(label, 1)
        self.addWidget(self.save_btn, 1)
        self.addWidget(self.list1, 20)
        self.addWidget(self.delete_btn, 1)

        self.openFileList()

    def setEnable(self, value):
        self.list1.setEnabled(value)

    def itemSelectedFunc(self, item):
        index = self.list1.currentRow()
        myItem = self.items[index]
        self.itemSelected.emit(myItem)

    def changeText(self, index, end):
        temp = self.items[index].filename.split('/')
        self.items[index].end = end
        self.items[index].text = "{}~{}-".format(self.items[index].start_min_sec_text(), self.items[index].end_min_sec_text()) + "-" + temp[len(temp)-1]
        self.list1.item(index).setText(self.items[index].text)

    def saveFileList(self):
        f = open(os.path.join(self.my_path,"mt_tracks.txt"), 'w')
        for item in self.items:
            f.write(item.get_text_for_file() + "\n")
        f.close()

    def openFileList(self):
        if os.path.isfile(os.path.join(self.my_path,"mt_tracks.txt")):
            f = open(os.path.join(self.my_path,"mt_tracks.txt"), "r")
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                item = TrackItem("", 0, 0)
                item.parse_text_for_file(line)
                self.items.append(item)
                self.list1.addItem(item.text)
            f.close()

    def delete_file(self):
        if len(self.list1.selectedItems()) > 0:
            for item in self.list1.selectedItems():
                self.items.pop(self.list1.row(item))
                self.list1.takeItem(self.list1.row(item))
            if os.path.isfile(os.path.join(self.my_path,"mt_tracks.txt")):
                os.remove(os.path.join(self.my_path,"mt_tracks.txt"))
            self.saveFileList()
