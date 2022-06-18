from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget, QPushButton,
    QHBoxLayout, QVBoxLayout,
    QLabel, QTableWidget,
    QTableWidgetItem, QAbstractScrollArea,
    QAbstractItemView, QGroupBox,
    QLineEdit, QWidget, 
    QGridLayout, QMessageBox,
    QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from datetime import datetime
from src.database import NodesDB
from src.detection import Detection
from src.settings import SettingsView
from src.camera import CameraView
from src.constants import CONFIG_NAME
from src.confirm import Confirm
from src.response import MachineResponse
import serial, serial.tools.list_ports
import logging, configparser
import random

# Main GUI of the Application
class MainWindow(QMainWindow):

    # Contructor
    def __init__(self):
        super(MainWindow, self).__init__()

        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_NAME)

        # Load database
        self.db = NodesDB(self.config.get('DATABASE', 'NAME'))

        self.saved_once = False
        self.conveyor_init = False

        self.machine_response = MachineResponse()
        self.machine_response.updateResponse.connect(self.updateResponse)
        self.machine_response.start()

        # Serial port connection
        try:
            self.ser_com = serial.Serial(self.config.get('SERIAL', 'COM'))
            self.machine_response.ser_com = self.ser_com
        except serial.SerialException as error:
            logging.error("Error encountered {}".format(error))

        # Initialize detection
        self.detection = Detection()
        self.detection.start()
        self.detection.updateFrame.connect(self.updateFrame)
        self.detection.getCount.connect(self.getCount)
        
        # Initialize camera view widget
        self.camera_view = CameraView()
        self.camera_view.start_detect_btn.clicked.connect(self.startProcess)
        self.camera_view.stop_detect_btn.clicked.connect(self.stopProcess)
        self.camera_view.on_btn.clicked.connect(self.sendDataTwo)
        self.camera_view.off_btn.clicked.connect(self.sendDataThree)

        # Initialize settings view widget
        self.settings_view = SettingsView()
        self.settings_view.btn_apply.clicked.connect(self.applySettings)
        self.settings_view.btn_cancel.clicked.connect(lambda: self.settings_view.close())
        self.settings_view.count_thresh_value.setCurrentText(str(self.config.getint("DETECTION", "COUNT_THRESH")))

        self.setup_UI()

        # Update serial connection status
        self.updateSerialConnect()

    # Close the other windows when the main window is closed
    def closeEvent(self, event):
        # Open up a confirmation dialog
        confirm = Confirm(icon=QMessageBox.Warning, 
                          title="Confirm exit application",
                          text="Are you sure you want exit?")
        answer = confirm.exec()
        if answer == QMessageBox.Yes:
            self.camera_view.close()
            event.accept()
        else:
            self.show()
            event.ignore()

    # Apply settings function for apply button in settings view
    def applySettings(self):
        self.config.set("DETECTION", "COUNT_THRESH", self.settings_view.count_thresh_value.currentText())
        self.config.set("SERIAL", "COM", self.settings_view.port_value.currentText())
        with open(CONFIG_NAME, "w") as configfile:
            self.config.write(configfile)
        self.updateSerialConnect()
        self.settings_view.close()

    # Update serial connection status
    def updateSerialConnect(self):
        ports = [port.device for port in serial.tools.list_ports.comports(include_links=False)]
        if self.config.get("SERIAL", "COM") not in ports:
            self.config.set("SERIAL", "COM", random.choice(ports))
            with open(CONFIG_NAME, "w") as configfile:
                self.config.write(configfile)
            self.config.read(CONFIG_NAME)
        try:
            try:
                self.ser_com.close()
            except Exception as error:
                logging.error("Error encountered! {}".format(error))
            self.ser_com = serial.Serial(self.config.get("SERIAL", "COM"))
            self.machine_response.ser_com = self.ser_com
            self.serial_port_value.setText("CONNECTED")
            self.serial_port_value.setToolTip(self.config.get("SERIAL", "COM"))
        except:
            self.serial_port_value.setText("NOT CONNECTED")
            self.serial_port_value.setToolTip(self.config.get("SERIAL", "COM"))

    # Update the machine response
    def updateResponse(self, response_code):
        """
        RESPONSE CODES:
        ~   -1: ERROR
        ~   0:  NULL
        ~   1: CUT
        ~   2: CONVEYOR ON
        ~   3: CONVEYOR OFF 
        """
        response = ""
        if response_code == -1:
            response_code = "ERROR"
        elif response_code == 0:
            response = "NULL"
        elif response_code == 1:
            response = "CUT"
        elif response_code == 2:
            response = "CONVEYOR ON"
        elif response_code == 3:
            response = "CONVEYOR OFF"
        self.machine_response_value.setText(response)

    # Open settings view widget
    def openSettingsView(self):
        ports = serial.tools.list_ports.comports(include_links=False)
        self.settings_view.port_value.clear()
        for port in ports:
            self.settings_view.port_value.addItem(port.device)
        if self.config.get("SERIAL", "COM") not in [port.device for port in ports]:
            self.config.set("SERIAL", "COM", self.settings_view.port_value.currentText())
            with open(CONFIG_NAME, "w") as configfile:
                self.config.write(configfile)
        else:
            for index in range(len(ports)):
                if self.config.get("SERIAL", "COM") == ports[index].device:
                    self.settings_view.port_value.setCurrentIndex(index)
                    break
        self.settings_view.center_Ui()
        self.settings_view.show()

    # Open camera view widget
    def openCamereView(self):
        self.camera_view.center_Ui()
        self.camera_view.show()

    # Update frame in the camera view
    def updateFrame(self, frame):
        self.camera_view.camera_frame.setPixmap(QPixmap.fromImage(frame))

    # Set up Ui
    def setup_UI(self):

        # ----- Window configurations -----
        self.setWindowIcon(QIcon(":/icon.png"))
        self.resize(self.config.getint('WINDOW', 'WIDTH'), self.config.getint('WINDOW', 'HEIGHT'))
        self.setWindowTitle(self.config.get('WINDOW', 'TITLE'))

        # ----- Initial layouts -----
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
       
        # ----- Title layout -----
        self.titleLayout = QVBoxLayout()
        # self.titleLayout.setContentsMargins(20, 20, 20, 20)
     
        # ----- Title -----
        title = QLabel()
        title.setText(self.config.get('WINDOW', 'TITLE'))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titleLayout.addWidget(title)
        
        # ----- Body layout -----
        self.bodyLayout = QHBoxLayout()
        
        # ----- Detection buttons layout -----
        self.detectionBtnsLayout = QHBoxLayout()

        self.detectionControlsLayout = QVBoxLayout()

        # ----- Machine buttons layout -----
        self.machineControlsLayout = QVBoxLayout()
        # Valve layout
        self.valvelayout = QHBoxLayout()
        self.conveyorlayout = QHBoxLayout()

        # ----- Table layout -----
        self.tableLayout = QVBoxLayout()

        # ----- Table actions layout -----
        self.tableActionsLayout = QHBoxLayout()

        # ----- Table widget -----
        table_headers = {
            "data": "Data",
            "date": "Date",
            "time": "Time",
            "thresh": "Threshold"
        }
        self.table = QTableWidget()
        self.table.setColumnCount(len(table_headers))
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(True)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeaderLabels(table_headers.values())
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tableLayout.addWidget(self.table)
     
        # ----- Table actions -----
        refresh = QPushButton()
        refresh.setText("  REFRESH  ")
        refresh.clicked.connect(self.refreshTable)
        camera = QPushButton()
        camera.setText("  CAMERA  ")
        camera.clicked.connect(self.openCamereView)
        settings = QPushButton()
        settings.setText("  SETTINGS  ")
        settings.clicked.connect(self.openSettingsView)
        self.tableActionsLayout.addWidget(refresh)
        self.tableActionsLayout.addWidget(camera)
        self.tableActionsLayout.addWidget(settings)
        self.tableActionsLayout.addStretch()
        self.tableLayout.addLayout(self.tableActionsLayout)
      
        # ----- Detection Controls Group -----
        self.detectionControlsGroup = QGroupBox("Detection Controls")
        self.detectionControlsGroup.setLayout(self.detectionControlsLayout)
        # self.detectionControlsGroup.setContentsMargins(20, 20, 20, 20)

        # ----- Machine Controls Group ----
        self.machineControlsGroup = QGroupBox("Machine Controls")
        self.machineControlsGroup.setLayout(self.machineControlsLayout)
        # self.machineControlsGroup.setContentsMargins(20, 20, 20, 20)
      
        # ----- Detection Control Buttons -----
        #  Start process button
        start = QPushButton()
        start.setText("START")
        start.clicked.connect(self.startProcess)
        self.detectionBtnsLayout.addWidget(start)
        
        # Stop process button
        stop = QPushButton()
        stop.setText("STOP")
        stop.clicked.connect(self.stopProcess)
        self.detectionBtnsLayout.addWidget(stop)

        self.detectionControlsLayout.addLayout(self.detectionBtnsLayout)

        # ----- Machine Control Buttons -----
        # Valve
        valve_label = QLabel("Valve:")
        send_one = QPushButton()
        send_one.setText("Activate")
        send_one.clicked.connect(self.sendDataOne)
        self.valvelayout.addWidget(valve_label)
        self.valvelayout.addWidget(send_one)
        self.machineControlsLayout.addLayout(self.valvelayout)
        # Conveyor
        conveyor_label = QLabel("Conveyor:")
        send_two = QPushButton()
        send_two.setText("On")
        send_two.clicked.connect(self.sendDataTwo)
        send_three = QPushButton()
        send_three.setText("Off")
        send_three.clicked.connect(self.sendDataThree)
        self.conveyorlayout.addWidget(conveyor_label)
        self.conveyorlayout.addWidget(send_two)
        self.conveyorlayout.addWidget(send_three)
        self.machineControlsLayout.addLayout(self.conveyorlayout)
      
        # ----- Logs group -----
        self.logsGroup = QGroupBox("Logs")
        self.logsLayout = QGridLayout()
        self.logsGroup.setLayout(self.logsLayout)
        
        # Count
        count_label = QLabel("Current Count:")
        self.count_value = QProgressBar()
        self.count_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logsLayout.addWidget(count_label, 0, 0)
        self.logsLayout.addWidget(self.count_value, 0, 1)
    
        # Total number of rows
        total_label = QLabel("Total:")
        self.total_value = QLineEdit()
        self.total_value.setReadOnly(True)
        self.total_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logsLayout.addWidget(total_label, 1, 0)
        self.logsLayout.addWidget(self.total_value, 1, 1)

        # Serial port
        serial_port_label = QLabel("Machine Status:")
        self.serial_port_value = QLineEdit()
        self.serial_port_value.setReadOnly(True)
        self.serial_port_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logsLayout.addWidget(serial_port_label, 2, 0)
        self.logsLayout.addWidget(self.serial_port_value, 2, 1)

        # Machine response -----
        machine_response_label = QLabel("Machine Response: ")
        self.machine_response_value = QLineEdit()
        self.machine_response_value.setReadOnly(True)
        self.machine_response_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logsLayout.addWidget(machine_response_label, 3, 0)
        self.logsLayout.addWidget(self.machine_response_value, 3, 1)

        # ----- Side layout -----
        self.sideLayout = QVBoxLayout()
        self.sideLayout.addWidget(self.detectionControlsGroup)
        self.sideLayout.addWidget(self.machineControlsGroup)
        self.sideLayout.addWidget(self.logsGroup)
        self.sideLayout.addStretch()

        # ----- Layouts' configurations -----
        self.bodyLayout.addLayout(self.tableLayout, 60)
        self.bodyLayout.addLayout(self.sideLayout, 40)
        self.mainLayout.addLayout(self.titleLayout)
        self.mainLayout.addLayout(self.bodyLayout)
        
        # ----- Initial Set Up -----
        self.refreshTable()
        
        # ----- Stylesheet   -----
        self.logsGroup.setStyleSheet("QGroupBox {\n" "background-color:#aef3ae; font-size: 14x; font-weight:bold;  \n""\n""\n""}")
        self.detectionControlsGroup.setStyleSheet("QGroupBox {\n" "background-color:#aef3ae; font-size: 16px;  font-weight:bold; \n""\n""\n" "}")
        self.machineControlsGroup.setStyleSheet("QGroupBox {\n" "background-color:#aef3ae; font-size: 16px;  font-weight:bold; \n""\n""\n" "}")
        self.setStyleSheet(" background-color: #084d08")
        title.setStyleSheet("color:white; font-size:22px; font-weight:bold;")
        start.setStyleSheet("QPushButton {background-color:#62b4cf; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #0080ff;}")
        stop.setStyleSheet("QPushButton {background-color:#ff6262; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #ff1a1a;}")
        camera.setStyleSheet("QPushButton {background-color:#ffd589; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #b0f5a4;}")
        refresh.setStyleSheet("QPushButton {background-color:#f5f5a4; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #b0f5a4;}")
        settings.setStyleSheet("QPushButton {background-color:#f5f5a4; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #b0f5a4;}")
        send_one.setStyleSheet("QPushButton {background-color:#62b4cf; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #0080ff;}}")
        send_two.setStyleSheet("QPushButton {background-color:#62b4cf; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #ff1a1a;}")
        send_three.setStyleSheet("QPushButton {background-color:#ff6262; border-radius: 7px; font-size:14px; font-weight:bold;} QPushButton:hover {background-color: #ff1a1a;}")

        valve_label.setStyleSheet("QLabel {font-size:14px; background-color: #aef3ae}")
        conveyor_label.setStyleSheet("QLabel {font-size:14px; background-color: #aef3ae}")
        serial_port_label.setStyleSheet("QLabel {font-size:14px; background-color: #aef3ae}")
        total_label.setStyleSheet("QLabel {font-size:14px;background-color: #aef3ae}")
        count_label.setStyleSheet("QLabel {font-size:14px; background-color: #aef3ae}")
        machine_response_label.setStyleSheet("QLabel {font-size:14px; background-color: #aef3ae}")
        
        self.machine_response_value.setStyleSheet("border-radius: 6px;background-color:white")
        self.total_value.setStyleSheet("border-radius: 6px;background-color:white")
        self.serial_port_value.setStyleSheet("border-radius: 6px;background-color:white")
        self.count_value.setStyleSheet("border-radius: 6px;background-color:white")
        
        self.table.setStyleSheet(" border-radius: 8px;background-color:wheat")
   
        
    # Start process function
    def startProcess(self):
        confirm = Confirm(icon=QMessageBox.Warning, 
                          title="Confirm start detection",
                          text="Are you sure you want start detection?")
        answer = confirm.exec()
        if answer == QMessageBox.Yes:
            self.camera_view.setDetectionStatus('ON')
            self.detection.isActive = True
            # try:
            #     self.ser_com.write((2).to_bytes(1, 'little')) # Send integer data 0x02 to Arduino
            # except serial.PortNotOpenError:
            #     logging.error("Failed to send data. Not port detected.")
            # except AttributeError:
            #     logging.error("Failed to send data. Not port detected.")
            # except serial.SerialException:
            #     logging.error("Failed to send data. Not port detected.")

    # Stop process function
    def stopProcess(self):
        confirm = Confirm(icon=QMessageBox.Warning, 
                          title="Confirm stop detection",
                          text="Are you sure you want stop detection?")
        answer = confirm.exec()
        if answer == QMessageBox.Yes:
            self.camera_view.setDetectionStatus('OFF')
            self.detection.isActive = False
            self.resetCount(initial=0)
            # try:
            #     self.ser_com.write((2).to_bytes(1, 'little')) # Send integer data 0x02 to Arduino
            # except serial.PortNotOpenError:
            #     logging.error("Failed to send data. Not port detected.")
            # except AttributeError:
            #     logging.error("Failed to send data. Not port detected.")
            # except serial.SerialException:
            #     logging.error("Failed to send data. Not port detected.")

    # Send data one through serial function
    def sendDataOne(self):
        try:
            self.ser_com.write((1).to_bytes(1, 'little')) # Send integer data 0x01 to Arduino
        except serial.PortNotOpenError:
            logging.error("Failed to send data. Not port detected.")
        except AttributeError:
            logging.error("Failed to send data. Not port detected.")
        except serial.SerialException:
            logging.error("Failed to send data. Not port detected.")

    # Send data two through serial function (on conveyor)
    def sendDataTwo(self):
        try:
            self.ser_com.write((2).to_bytes(1, 'little')) # Send integer data 0x02 to Arduino
        except serial.PortNotOpenError:
            logging.error("Failed to send data. Not port detected.")
        except AttributeError:
            logging.error("Failed to send data. Not port detected.")
        except serial.SerialException:
            logging.error("Failed to send data. Not port detected.")

    # Send data three through serial function (off conveyor)
    def sendDataThree(self):
        try:
            self.ser_com.write((3).to_bytes(1, 'little')) # Send integer data 0x03 to Arduino
        except serial.PortNotOpenError:
            logging.error("Failed to send data. Not port detected.")
        except AttributeError:
            logging.error("Failed to send data. Not port detected.")
        except serial.SerialException:
            logging.error("Failed to send data. Not port detected.")

    # Refresh table function
    def refreshTable(self):
        detected_nodes = self.db.getall()
        total = self.db.total()
        self.table.setRowCount(total)
        for nrow in range(total):
            node = detected_nodes[nrow]
            data = str(node.data)
            date = node.date_time.strftime('%b %d, %Y')
            time = node.date_time.strftime('%H:%M:%S')
            count_thresh = str(node.count_thresh)
            data_tableitem = QTableWidgetItem(data)
            data_tableitem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            date_tableitem = QTableWidgetItem(date)
            date_tableitem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            time_tableitem = QTableWidgetItem(time)
            time_tableitem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            count_thresh_tableitem = QTableWidgetItem(count_thresh)
            count_thresh_tableitem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(nrow, 0, data_tableitem)
            self.table.setItem(nrow, 1, date_tableitem)
            self.table.setItem(nrow, 2, time_tableitem)
            self.table.setItem(nrow, 3, count_thresh_tableitem)
        self.updateTotal()

    # Update label value for the total number of rows in the database
    def updateTotal(self):
        total = self.db.total() # Get the total number of rows in the database
        self.total_value.setText(str(total)) # Update total_value label
        
    def getCount(self, count):
        if count > 0:
            if self.conveyor_init == False:
                self.sendDataTwo()
                self.conveyor_init = True
        else:
            if self.conveyor_init == True:
                self.sendDataThree()
            self.conveyor_init = False
        # If the number of detected nodes reaches its conditions
        if count % (self.config.getint("DETECTION", "COUNT_THRESH")+1) == 0 and count != 0:
            if self.saved_once == False:
                try:
                    self.ser_com.write((1).to_bytes(1, 'little')) # Send integer data 0x01 to Arduino
                except AttributeError:
                    logging.error("Failed to send data. Not port detected.")
                data = self.db.total() + 1 # Overall total
                date_time = datetime.now() # Record date and time
                self.db.add(data=data, date_time=date_time, count_thresh=self.config.getint("DETECTION", "COUNT_THRESH")) # Add new row in the database
                self.refreshTable() # Refresh the table
                self.saved_once = True # Set saved_once to True to perform tasks once
                self.resetCount(initial=1)
        else:
            if self.saved_once == True:
                self.saved_once = False 
        self.count_value.setValue((count/(self.config.getint("DETECTION", "COUNT_THRESH")))*100)
        self.count_value.setFormat("{}/{}".format(count, self.config.getint("DETECTION", "COUNT_THRESH")))
        # self.count_value.setText(str(count))

    # Reset the count value
    def resetCount(self, initial=0):
        self.detection.detector.count = initial
        self.count_value.setValue((self.detection.detector.count/(self.config.getint("DETECTION", "COUNT_THRESH")))*100)
        self.count_value.setFormat("{}/{}".format(self.detection.detector.count, self.config.getint("DETECTION", "COUNT_THRESH")))
        # self.count_value.setText(str(self.detection.detector.count))
