import cv2
import numpy
from PyQt5.QtCore import pyqtSignal, QThread

from layouts.track_list import TrackItem


class Tracer(QThread):
    traceEnd = pyqtSignal()
    progressChanged = pyqtSignal(float)
    trackAdded = pyqtSignal(TrackItem)
    trackEndChanged = pyqtSignal(int)
    drawContours = pyqtSignal(numpy.ndarray)
    def __init__(self, parent, filelist, rect, video_rect, detect_value):
        super().__init__(parent)
        self.filelist = filelist
        self.pause = False
        #v_width = video_rect.width()
        #v_height = video_rect.height()
        #new_left = rect.left() * v_width
        #new_right = rect.right() * v_width
        #new_top = rect.top() * v_height
        #new_bottom = rect.bottom() * v_height
        #self.rect = QRectF(new_left, new_top, new_right - new_left, new_bottom - new_top)
        self.rect = rect
        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_CROSS, (4, 4))
        self.prev_progress = 0.0
        self.current_treated_frame_count = 0
        self.total_frame_count = self.get_total_frames()
        self.detect_value = detect_value

    def __del__(self):
        self.quit()
        self.wait(1000)

    def get_total_frames(self):
        total_count = 0
        for file in self.filelist:
            cpt = cv2.VideoCapture(file)
            total_count += cpt.get(cv2.CAP_PROP_FRAME_COUNT)
        return total_count

    # 해당 파일의 프레임을 모두 이미지로 변환하여 추적
    def make_frames_and_trace(self, filename):
        cpt = cv2.VideoCapture(filename)
        frame_count = int(cpt.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cpt.get(cv2.CAP_PROP_FPS)
        f_width = cpt.get(cv2.CAP_PROP_FRAME_WIDTH)
        f_height = cpt.get(cv2.CAP_PROP_FRAME_HEIGHT)
        cpt.set(cv2.CAP_PROP_POS_FRAMES, 0)
        _, frame1 = cpt.read()
        on_blank = True
        prev_second = 0.0
        fps_i = int(fps * self.detect_value['unit'])

        has_track = None

        for i in range(1, frame_count - 1, fps_i):
            if self.pause:
                while self.pause:
                    self.sleep(1)
            if i + fps < frame_count:
                cpt.set(cv2.CAP_PROP_POS_FRAMES, i+fps_i)
                print(str(i) + "/" + str(frame_count))
                _, frame2 = cpt.read()
                preview = frame1
                dst1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                dst2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(dst1, dst2)
                ret_thr, thr = cv2.threshold(
                    diff, 30, 255, cv2.THRESH_BINARY)
                dilate = cv2.dilate(thr, self.kernel)
                contours, hierarchy = cv2.findContours(
                    dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                has_it = False
                if len(contours) > 0:
                    print("Has Contours")
                for ct in range(len(contours)):
                    area_size = cv2.contourArea(contours[ct])
                    min_rect = cv2.minAreaRect(contours[ct])
                    rect1 = [self.rect.left(), self.rect.top(),
                             self.rect.right(), self.rect.bottom()]
                    rect2 = [min_rect[0][0] / f_width, min_rect[0][1] / f_height,
                             (min_rect[0][0] + min_rect[1][0]) / f_width,
                             (min_rect[0][1] + min_rect[1][1]) / f_height]
                    if area_size > int(self.detect_value['size']) * 100 and rect2[2] - rect2[0] > 0.01 and rect2[3] - rect2[1] > 0.01 and self.check_overlap(rect1, rect2):
                        print("Detect")
                        x,y,w,h = cv2.boundingRect(contours[ct])
                        cv2.rectangle(preview, (x,y), (x+w,y+h), (255, 0, 0), 5)
                        has_it = True

                current_second = int((i-1) / fps)

                # 변화가 감지되었나?
                if has_it:
                    # 기존에 공백구간이었나?
                    if on_blank:
                        on_blank = False
                        prev_second = current_second
                        has_track = TrackItem(filename, current_second, current_second)
                    else:
                        prev_second = current_second
                        if has_track is not None:
                            has_track.end = current_second
                else:
                    # 10초 이상 감지되지 않았는가?
                    if current_second - prev_second > int(self.detect_value['space']):
                        on_blank = True
                        if has_track is not None:
                            if has_track.end - has_track.start >= int(self.detect_value['len']):
                                has_track.apply_text()
                                self.trackAdded.emit(has_track)
                            has_track = None
                cv2.rectangle(preview,
                              (int(self.rect.left() * f_width), int(self.rect.top() * f_height)),
                              (int(self.rect.right() * f_width), int(self.rect.bottom() * f_height)),
                              (0,255,0), 5)
                self.drawContours.emit(preview)
                frame1 = frame2

                self.current_treated_frame_count += fps_i
                current_progress = (self.current_treated_frame_count / self.total_frame_count) * 100.0
                if current_progress > self.prev_progress + 1.0:
                    self.progressChanged.emit(current_progress)
                    self.prev_progress = current_progress
                self.msleep(1)
        if has_track is not None:
            has_track.apply_text()
            self.trackAdded.emit(has_track)

    def run(self):
        self.prev_progress = 0.0
        self.current_treated_frame_count = 0
        for file in self.filelist:
            self.make_frames_and_trace(file)
        self.progressChanged.emit(100.0)
        self.traceEnd.emit()

    def check_overlap(self, arr1, arr2):
        if arr1[0] == arr1[2] or arr1[1] == arr1[3] or arr2[0] == arr2[2] or arr2[1] == arr2[3]:
            return False
        if arr1[0] > arr2[2] or arr2[0] > arr1[2]:
            return False
        if arr1[1] > arr2[3] or arr2[1] > arr1[3]:
            return False
        return True

    def stop(self):
        self.pause = True
        self.quit()
        self.wait(1000)