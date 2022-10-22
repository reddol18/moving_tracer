import os
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QListWidget, QVBoxLayout, QPushButton, QFileDialog, QAbstractItemView


class FileList(QVBoxLayout):
    itemSelected = pyqtSignal(str)
    listCountChanged = pyqtSignal(int, str)
    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            self.my_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.my_path = os.path.dirname(os.path.abspath(__file__))
        label = QLabel('파일리스트')
        self.files = []
        self.list1 = QListWidget()
        self.list1.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list1.itemDoubleClicked.connect(self.itemSelect)

        self.open_btn = QPushButton('파일추가')
        self.open_btn.clicked.connect(self.open_files)

        self.delete_btn = QPushButton('삭제')
        self.delete_btn.clicked.connect(self.delete_file)

        self.addWidget(label, 1)
        self.addWidget(self.open_btn,1)
        self.addWidget(self.list1, 18)
        self.addWidget(self.delete_btn,1)

        self.openFileList()

    def itemSelect(self, item):
        index = self.list1.currentRow()
        myItem = self.files[index]
        self.itemSelected.emit(myItem)

    def setEnable(self, value):
        self.list1.setEnabled(value)

    def open_files(self):
        filter = "ALL Files(*.*)"
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        fnames = dlg.getOpenFileNames(caption = "파일 추가", filter = filter)

        first_file_name = ""
        if len(fnames) > 0 and len(fnames[0]) > 0:
            for item in fnames[0]:
                self.files.append(item)
                self.list1.addItem(item)
            first_file_name = self.files[0]
        self.listCountChanged.emit(len(self.files), first_file_name)
        self.saveFileList()

    def saveFileList(self):
        f = open(os.path.join(self.my_path,"mt_files.txt"), 'w')
        for item in self.files:
            f.write(item + "\n")
        f.close()

    def openFileList(self):
        if os.path.isfile(os.path.join(self.my_path,"mt_files.txt")):
            f = open(os.path.join(self.my_path,"mt_files.txt"), "r")
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                self.files.append(line)
                self.list1.addItem(line)
            f.close()
            first_file_name = ""
            if len(self.files) > 0:
                first_file_name = self.files[0]
            self.listCountChanged.emit(len(self.files), first_file_name)

    def delete_file(self):
        if len(self.list1.selectedItems()) > 0:
            for item in self.list1.selectedItems():
                self.files.pop(self.list1.row(item))
                self.list1.takeItem(self.list1.row(item))
            first_file_name = ""
            if len(self.files) > 0:
                first_file_name = self.files[0]
            self.listCountChanged.emit(len(self.files), first_file_name)
            if os.path.isfile(os.path.join(self.my_path,"mt_files.txt")):
                os.remove(os.path.join(self.my_path,"mt_files.txt"))
            self.saveFileList()
