from PyQt5.QtCore import QUrl, pyqtSlot, pyqtSignal, QObject, QRectF, QPointF, Qt, QSizeF
from PyQt5.QtGui import QPen
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtWidgets import QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, \
    QGraphicsObject
from PyQt5.uic.properties import QtGui


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


class Box(QGraphicsRectItem):

    def __init__(self, position, rect=QRectF(0, 0, 100, 50)):
        super().__init__(rect)

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



class VideoWidget(QGraphicsView):
    stateChanged = pyqtSignal(QMediaPlayer.State)
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)
    error = pyqtSignal(str)
    pos = QPointF(0,0)
    rect = QRectF(0,0,0,0)
    box_created = False

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.video = QGraphicsVideoItem()
        self.scene.addItem(self.video)
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.setScene(self.scene)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.video.setSize(QSizeF(self.width(), self.height()))
        self.fitInView(self.video, Qt.IgnoreAspectRatio)

    def set_player(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        print("set_player")
        self.player.setVideoOutput(self.video)
        self.player.stateChanged.connect(self.stateChangedFunc)
        self.player.positionChanged.connect(self.positionChangedFunc)
        self.player.durationChanged.connect(self.durationChangedFunc)
        self.player.error.connect(self.errorFunc)
        fileName = "E:/dev/moving_tracer/test.wmv"
        try:
            file = QUrl.fromLocalFile(fileName)
            print(file)
            self.player.setMedia(QMediaContent(file))
        except:
            print("파일이 존재하지 않습니다")
        finally:
            self.show()

    def stateChangedFunc(self, state):
        self.stateChanged.emit(self.player.state())

    def positionChangedFunc(self, position):
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
        else:
            self.deleteRect()

    def setPosition(self, position):
        self.player.setPosition(position)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    # Video의 현재 화면을 캡쳐해서 저장한다
    def captureVideo(self):
        self.captured = self.grab()

    def makeRect(self):
        if self.box_created == False:
            self.rect = QRectF(0,0, self.scene.width(), self.scene.height())
            self.box = Box(self.pos, rect=self.rect)
            self.scene.addItem(self.box)
            self.box.show()
            self.box_created = True
        else:
            self.box.show()

    def deleteRect(self):
        self.box.hide()