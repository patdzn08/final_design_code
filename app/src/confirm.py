from PyQt5.QtWidgets import (
    QMessageBox
)

class Confirm(QMessageBox):

    def __init__(self, icon=QMessageBox.Information, 
                 text="...", title="Title", 
                 standard_btns = QMessageBox.Yes | QMessageBox.No, parent=None):
        super(Confirm, self).__init__(parent)
        self.setIcon(icon)
        self.setText(text)
        self.setWindowTitle(title)
        self.setStandardButtons(standard_btns)
        