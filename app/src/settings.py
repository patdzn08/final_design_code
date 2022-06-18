from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,
    QGridLayout, QLabel,
    QLineEdit, QHBoxLayout,
    QPushButton, QDesktopWidget,
    QComboBox
)
from PyQt5.QtGui import QIcon

class SettingsView(QWidget):
    
    def __init__(self, parent=None):
        super(SettingsView, self).__init__(parent)
        self.setup_Ui()

    def setup_Ui(self):

        # ----- Window configurations -----
        self.setWindowTitle("SETTINGS")
        self.setWindowIcon(QIcon(":/icon.png"))

        # ----- Layouts -----
        self.vlayout = QVBoxLayout()
        self.optionslayout = QGridLayout()
        self.buttonsLayout = QHBoxLayout()

        # ----- Widgets -----
        # Serial port
        port_label = QLabel()
        port_label.setText("Serial Port: ")
        self.port_value = QComboBox()

        # Count Threshold
        count_thresh_label = QLabel()
        count_thresh_label.setText("Count Threshold: ")
        self.count_thresh_value = QComboBox()
        self.count_thresh_value.addItem("2")
        self.count_thresh_value.addItem("3")
        self.count_thresh_value.addItem("4")

        # Buttons
        self.btn_apply = QPushButton()
        self.btn_apply.setText("Apply")
        self.btn_cancel = QPushButton()
        self.btn_cancel.setText("Cancel")
        
        self.btn_apply.setStyleSheet("QPushButton {background-color:#62b4cf; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #0080ff;}")
        self.btn_cancel.setStyleSheet("QPushButton {background-color:#ff6262; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #ff1a1a;}")
       
        
        self.optionslayout.addWidget(port_label, 0, 0)
        self.optionslayout.addWidget(self.port_value, 0, 1)
        self.optionslayout.addWidget(count_thresh_label, 1, 0)
        self.optionslayout.addWidget(self.count_thresh_value, 1, 1)
        self.buttonsLayout.addWidget(self.btn_cancel)
        self.buttonsLayout.addWidget(self.btn_apply)
        self.vlayout.addLayout(self.optionslayout)
        self.vlayout.addStretch()
        self.vlayout.addLayout(self.buttonsLayout)

        self.setLayout(self.vlayout)
        self.resize(self.vlayout.sizeHint())

    def center_Ui(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())