from PyQt5.QtCore import (
    QThread, pyqtSignal,
    Qt
)
from PyQt5.QtGui import (
    QImage
)
from .detector import Detector
import cv2

class Detection(QThread):
    
    isActive = False
    updateFrame = pyqtSignal(QImage)
    getCount = pyqtSignal(int)
    updateStatus = pyqtSignal(bool)
    detector = Detector(320, 320, 640, 480)

    def run(self):
        running = True
        capture = cv2.VideoCapture(0)
        while running == True:
            ret, frame = capture.read()
            if ret == True:
                if self.isActive == True:
                    frame = self.detector.detect(frame)
                self.updateStatus.emit(self.detector.detected)
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #flipped_img = cv2.flip(img, 1)
                qtformat_img = QImage(img.data,img.shape[1], img.shape[0], QImage.Format_RGB888)
                qtformat_img_scaled = qtformat_img.scaled(320, 240, Qt.KeepAspectRatio)
                self.updateFrame.emit(qtformat_img_scaled)
                self.getCount.emit(self.detector.count)