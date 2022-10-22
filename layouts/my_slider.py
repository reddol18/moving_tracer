from PyQt5 import QtWidgets
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtWidgets import QStyleOptionSlider, QStyle, QSlider

class MySlider(QtWidgets.QSlider):
    start_range = 0
    end_range = 0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paintEvent(self, event):
        if self.start_range < self.end_range and self.maximum() > 0:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)

            opt.subControls = QStyle.SC_SliderGroove | QStyle.SC_SliderHandle
            if self.tickPosition() != QSlider.NoTicks:
                opt.subControls |= QStyle.SC_SliderTickmarks

            grv_rect = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove)
            #self.paintEvent(event)
            paint_rect = self.getPartialRect(grv_rect)
            painter = QPainter(self)
            painter.fillRect(paint_rect, QBrush(Qt.lightGray))
        super().paintEvent(event)

    def getPartialRect(self, rect):
        start_rate = self.start_range / self.maximum()
        end_rate = self.end_range / self.maximum()
        new_rect = QRect(int(rect.left() + rect.width() * start_rate) - 6,
                         rect.top(),
                         int(rect.width() * (end_rate - start_rate)) + 12,
                         rect.height())
        return new_rect

    def setPartialRange(self, start, end):
        self.start_range = start * 1000
        self.end_range = end * 1000