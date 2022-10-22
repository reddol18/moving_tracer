import qimage2ndarray

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl, pyqtSignal, QRectF, QPointF, Qt, QSizeF, QObject
from PyQt5.QtGui import QPen, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, \
    QGraphicsObject, QMessageBox


class Resizer(QGraphicsObject):

    resizeSignal = pyqtSignal(QPointF)

    def __init__(self, rect=QRectF(0, 0, 10, 10), parent=None):
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.rect = rect

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            pen = QPen()
            pen.setStyle(Qt.DotLine)
            painter.setPen(pen)
        painter.drawRect(self.rect)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.isSelected():
                self.resizeSignal.emit(value - self.pos())
        return value

class BoxSignalProxy(QObject): rectChanged = pyqtSignal()

class Box(QGraphicsRectItem):
    def __init__(self, position, rect):
        super().__init__(rect)
        print(position, rect)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self.setPos(position)

        self.resizer = Resizer(parent=self)
        resizerWidth = self.resizer.rect.width()
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self.rect().bottomRight() - resizerOffset)
        self.resizer.resizeSignal.connect(self.resize)
        self._proxy = BoxSignalProxy()
        self.rectChanged = self._proxy.rectChanged

    def setPosAndRect(self, pos, rect):
        self.setPos(pos)
        self.setRect(QRectF(0,0,rect.width(),rect.height()))
        resizerWidth = self.resizer.rect.width()
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self.rect().bottomRight() - resizerOffset)
        self.prepareGeometryChange()
        self.update()

    def paint(self, painter, option, widget=None):
        pen = QPen()
        pen.setColor(Qt.green)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.rect())

    def resize(self, change):
        self.setRect(self.rect().adjusted(0, 0, change.x(), change.y()))
        self.prepareGeometryChange()
        self.update()
        self.rectChanged.emit()

    def getBoxRect(self):
        return QRectF(self.pos().x(), self.pos().y(),
                      self.resizer.pos().x() + 10, self.resizer.pos().y() + 10)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.isSelected():
                self.rectChanged.emit()
        return value


class VideoWidget(QGraphicsView):
    stateChanged = pyqtSignal(QMediaPlayer.State)
    boxRectChanged = pyqtSignal(QRectF)
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)
    error = pyqtSignal(str)
    pos = QPointF(0,0)
    rect = QRectF(0,0,0,0)
    rate_rect = QRectF(0.1, 0.2, 0.8, 0.5)
    box_created = False
    range_of_end = -1
    range_of_start = 0
    is_play_in_range = False
    has_before_rect = False
    on_preview = False

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.video = QGraphicsVideoItem()
        self.scene.addItem(self.video)
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.setScene(self.scene)
        print("video init finish")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.video.setSize(QSizeF(self.width(), self.height()))
        #self.fitInView(self.video, Qt.IgnoreAspectRatio)
        self.setDetectRect(self.rate_rect)

    def wheelEvent(self, ev):
        if ev.type() == QtCore.QEvent.Wheel:
            ev.ignore()

    def set_player(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        print("set_player")
        self.player.setVideoOutput(self.video)
        self.player.stateChanged.connect(self.stateChangedFunc)
        self.player.positionChanged.connect(self.positionChangedFunc)
        self.player.durationChanged.connect(self.durationChangedFunc)
        self.player.error.connect(self.errorFunc)
        self.player.videoAvailableChanged.connect(self.videoAvailable)
        self.show()
        #fileName = "E:/dev/moving_tracer/test.wmv"
        #self.setFile(fileName)

    def videoAvailable(self):
        self.video.setSize(QSizeF(self.width(), self.height()))
        #self.fitInView(self.video, Qt.IgnoreAspectRatio)
        self.setDetectRect(self.rate_rect)


    def stateChangedFunc(self, state):
        self.stateChanged.emit(self.player.state())

    def positionChangedFunc(self, position):

        if self.is_play_in_range == True and self.range_of_end > -1 and self.range_of_end <= position:
            print("pause after second", self.range_of_end, position)
            #self.player.pause()
            self.player.setPosition(self.range_of_start)
            self.positionChanged.emit(self.range_of_start)
            self.play()
        else:
            self.positionChanged.emit(position)

    def durationChangedFunc(self, duration):
        self.durationChanged.emit(duration)

    def errorFunc(self):
        self.error.emit(self.player.errorString())

    def setDetectOptionEnable(self, value):
        if value == True:
            self.player.pause()
            self.captureVideo()
            self.makeRect()

    def setPosition(self, position):
        self.player.setPosition(position)

    def play(self):
        if self.on_preview:
            if len(self.scene.items()) > 1:
                self.scene.removeItem(self.scene.items()[0])
            self.box.show()
        self.on_preview = False
        self.player.play()

    def pause(self):
        print("Pause")
        self.range_of_end = -1
        self.range_of_start = 0
        self.is_play_in_range = False
        self.player.pause()

    # Video의 현재 화면을 캡쳐해서 저장한다
    def captureVideo(self):
        self.captured = self.grab()

    def setDetectRect(self, rect):
        self.rate_rect = rect
        v_width = self.video.boundingRect().width()
        v_height = self.video.boundingRect().height()
        v_left = self.video.boundingRect().left()
        v_top = self.video.boundingRect().top()
        x = rect.left() * v_width + v_left
        r = rect.right() * v_width + v_left
        t = rect.top() * v_height + v_top
        b = rect.bottom() * v_height + v_top

        self.rect = QRectF(x,t,r-x,b-t)
        self.pos = QPointF(x, t)
        self.has_before_rect = True
        if self.box_created == True:
            self.box.setPosAndRect(self.pos, self.rect)

    def makeRect(self):
        if self.box_created == False:
            if self.has_before_rect == False:
                self.pos = QPointF(0,0)
                self.rect = QRectF(0,0, self.scene.width(), self.scene.height())
            self.box = Box(self.pos, QRectF(0,0,self.rect.width(),self.rect.height()))
            self.box.rectChanged.connect(self.boxRectChangeFunc)
            self.scene.addItem(self.box)
            self.box.show()
            self.box_created = True

    def boxRectChangeFunc(self):
        self.boxRectChanged.emit(self.getBoxRect())

    def setFile(self, filename):
        try:
            file = QUrl.fromLocalFile(filename)
            self.player.setMedia(QMediaContent(file))
            self.player.setPosition(0)
            self.play()
            self.player.pause()
        except:
            QMessageBox.about(self.parent().parent(), "ERROR", filename + "이 존재하지 않습니다")
            print("파일이 존재하지 않습니다")

    def playInRange(self, start, end):
        self.range_of_start = start * 1000
        self.is_play_in_range = True
        self.player.setPosition(start * 1000)
        self.range_of_end = end * 1000
        self.play()

    def getBoxRect(self):
        rectAsTuple = self.box.getBoxRect()

        v_width = self.video.boundingRect().width()
        v_height = self.video.boundingRect().height()
        v_left = self.video.boundingRect().left()
        v_top = self.video.boundingRect().top()

        rectAsTuple.setLeft((rectAsTuple.left() - v_left) / v_width)
        rectAsTuple.setRight((rectAsTuple.right() - v_left) / v_width)
        rectAsTuple.setTop((rectAsTuple.top() - v_top) / v_height)
        rectAsTuple.setBottom((rectAsTuple.bottom() - v_top) / v_height)
        return rectAsTuple

    def setPlaySpeed(self, value):
        self.player.setPlaybackRate(value)

    def drawImage(self, image):
        pxmap = QPixmap.fromImage(qimage2ndarray.array2qimage(image))
        pxmap = pxmap.scaled(self.width(), self.height())
        if self.on_preview:
            if len(self.scene.items()) > 1:
                self.scene.removeItem(self.scene.items()[0])
        self.on_preview = True
        self.scene.addPixmap(pxmap)