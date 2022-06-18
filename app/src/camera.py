from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
    QWidget, QDesktopWidget
)
from PyQt5.QtGui import QIcon

# Camera View Widget Class
class CameraView(QWidget):
    
    # Constructor
    def __init__(self, parent=None):
        super(CameraView, self).__init__(parent)
        self.setup_Ui()
        
    # Setup Ui 
    def setup_Ui(self):

        # ----- Window configurations -----
        self.setWindowTitle("CAMERA VIEW")
        self.setWindowIcon(QIcon(":/icon.png"))

        # ----- Layouts -----
        self.vlayout = QVBoxLayout()
        actionsLayout = QHBoxLayout()
        machinelayout = QHBoxLayout()

        # ----- Widgets -----
        self.detection_status = QLabel("DETECTION STATUS: STOP")
        self.camera_frame = QLabel()
        self.start_detect_btn = QPushButton("START")
        self.stop_detect_btn = QPushButton("STOP")
        self.on_btn = QPushButton("ON")
        self.off_btn = QPushButton("OFF")
        
        self.start_detect_btn.setStyleSheet("QPushButton {background-color:#62b4cf; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #0080ff;}")
        self.stop_detect_btn.setStyleSheet("QPushButton {background-color:#ff6262; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #ff1a1a;}")
        self.detection_status.setStyleSheet("QLabel {font-size:16px; font-weight:bold;} ")
        

        self.camera_frame.setMinimumSize(320, 240)

        actionsLayout.addWidget(self.start_detect_btn)
        actionsLayout.addWidget(self.stop_detect_btn)
        #machinelayout.addWidget(self.on_btn)
        #machinelayout.addWidget(self.off_btn)
        self.vlayout.addWidget(self.camera_frame)
        self.vlayout.addWidget(self.detection_status)
        self.vlayout.addLayout(actionsLayout)
        #self.vlayout.addLayout(machinelayout)
        self.setLayout(self.vlayout)
        self.resize(self.vlayout.sizeHint())

    def setDetectionStatus(self, status):
        self.detection_status.setText("DETECTION STATUS: " + status)

    def center_Ui(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())