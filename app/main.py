from PyQt5.QtWidgets import QApplication
from src.gui import MainWindow
from utils import resources
import sys

if __name__=="__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    main_window.show()
    sys.exit(app.exec())
