from PyQt5.QtWidgets import QLabel, QListWidget, QVBoxLayout


class FileList(QVBoxLayout):
    def __init__(self):
        super().__init__()
        label = QLabel('파일리스트')
        self.list1 = QListWidget()
        self.list1.insertItem(0, 'List1')
        self.addWidget(label, 1)
        self.addWidget(self.list1, 20)

    def setEnable(self, value):
        self.list1.setEnabled(value)