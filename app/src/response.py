from PyQt5.QtCore import QThread, pyqtSignal
import time

# Machine Response Class as a Thread for the Application
class MachineResponse(QThread):

    running = True
    updateResponse = pyqtSignal(int)
    ser_com = None

    # This function runs when the instance of this class started
    def run(self):
        while self.running == True:
            try:
                if self.ser_com is not None:
                    received = self.ser_com.read()
                    value = int.from_bytes(received, 'little')
                    self.updateResponse.emit(value)
                else:
                    self.updateResponse.emit(0)
            except:
                self.updateResponse.emit(-1)
            time.sleep(0.1)