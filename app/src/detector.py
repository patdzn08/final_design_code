from datetime import datetime, date
from .constants import *
import numpy as np
import cv2, sqlite3
import logging
import time

logging.basicConfig(filename="app_log.log", level=logging.ERROR, format="%(asctime)s:%(levelname)s:%(message)s")

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    logging.error("Encountered importing tflite\nTrying to import tensorflow")
    try:
        from tensorflow import lite
    except ImportError:
        print("Encountered importing tensorflow")
        exit(1)

# Detector Class
class Detector:

    # Constructor
    def __init__(self, width, height, imW, imH):
    
        self.detected = False
        self.isCounted = False
        self.count = 0

        self.width = width
        self.height = height

        self.imW = imW
        self.imH = imH

        # Load the label map
        with open(PATH_TO_LABELS, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]

        # Initialize frame rate calculation
        self.frame_rate_calc = 1
        self.freq = cv2.getTickFrequency()

        self.nodes = 0
        self.nodes_list = []

        try:
            self.interpreter = Interpreter(model_path=PATH_TO_CKPT)
        except NameError:
            logging.error("Error encountered creating self.interpreter based on tflite.")
            try:
                self.interpreter = lite.Interpreter(model_path=PATH_TO_CKPT)
            except NameError:
                logging.error("Failed to create self.interpreter based on tensorflow.")
                exit(1)

        self.interpreter.allocate_tensors()

        self.roi1 = int(imW/2-50)
        self.roi2 = int(self.roi1 + 100)
        
        # Get model details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        height = self.input_details[0]['shape'][1]
        width = self.input_details[0]['shape'][2]

        self.floating_model = (self.input_details[0]['dtype'] == np.float32)

        self.conn = sqlite3.connect("Nodesb.db")
        self.c = self.conn.cursor()

        self.start_time = 0
        self.elapsed_time = 0
        self.end_time = time.time() # Get the initial time when the application started, it will be used for the computation during runtime detection
        self.runtime_fade = False # This boolean variable will control the flow of elapsed time for counting
        self.interval = 5 # Number in seconds before resetting the count to zero

    def detect(self, frame):

        # Get the current time
        self.start_time = time.time()
        
        # Start timer (for calculating frame rate)
        t1 = cv2.getTickCount()

        today = date.today()
        now = datetime.now()
        _date = today.strftime("%d/%m/%Y")
        current_time = now.strftime("%H:%M:%S")

        frame = frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
        input_data = np.expand_dims(frame_resized, axis=0)
        
        # Insert content for detection...
        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if self.floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        self.interpreter.set_tensor(self.input_details[0]['index'],input_data)
        self.interpreter.invoke()
        
        # Draw ROI line for counting.  
        cv2.line(frame, (self.roi1, 0), (self.roi1, self.imH), (0, 0xFF, 0), 5)
        cv2.line(frame, (self.roi2, 0), (self.roi2, self.imH), (0, 0xFF, 0), 5)
        
        # Retrieve detection results
        boxes = self.interpreter.get_tensor(self.output_details[1]['index'])[0] # Bounding box coordinates of detected objects
        classes = self.interpreter.get_tensor(self.output_details[3]['index'])[0] # Class index of detected objects
        scores = self.interpreter.get_tensor(self.output_details[0]['index'])[0] # Confidence of detected object
        
        detected_total = 0
        
        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
                
                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * self.imH)))
                xmin = int(max(1,(boxes[i][1] * self.imW)))
                ymax = int(min(self.imH,(boxes[i][2] * self.imH)))
                xmax = int(min(self.imW,(boxes[i][3] * self.imW)))
                
                # In between ROI (Region of Interest)
                if ((xmin > self.roi1) and (xmin < self.roi2)):
                    detected_total += 1
                    
                    cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
                    
                    # Draw label
                    object_name = self.labels[int(classes[i])] # Look up object name from "labels" array using class index
                    label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                    label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                    cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                    cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
                else:
                    continue
        
        # Set the runtime_fade to true by default
        self.runtime_fade = True

        if detected_total == 1:
            self.runtime_fade = False # If there's a detected node, it will not run the elapsed_time
            self.detected = True
            cv2.putText(frame,'{}'.format("NODE  DETECTED"), (30,450), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255,255,110), 4, cv2.LINE_AA)
            if self.isCounted == False:
                self.count += 1
                self.isCounted = True
        else:
            self.detected = False
            cv2.putText(frame,'{}'.format("INVALID!  NOT NODE"), (30,450), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0,0,255), 4, cv2.LINE_AA)
            if self.isCounted == True:
                self.isCounted = False

        # If the runtime_fade is true, then the elapsed_time is running.
        # Otherwise, setting it to zero, which means the elapsed_time is not running
        if self.runtime_fade == True:
            self.elapsed_time += self.start_time - self.end_time # Add the difference of start_time and end_time to the elapsed_time
        else:
            self.elapsed_time = 0 # Set the elapsed_time to zero

        # If the elapsed_time reaches the interval (which means the elapsed_time's threshold), then
        # reset the count and elapsed_time to zero
        if self.elapsed_time >= self.interval:
            self.count = 0
            self.elapsed_time = 0
            self.runtime_fade = False

        # Draw framerate in corner of frame
        #cv2.putText(frame,'FPS: {0:.2f}'.format(self.frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

        #cv2.putText(frame,'Date: {0:.8s}'.format(_date),(30,190),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,0),2,cv2.LINE_AA)
        #cv2.putText(frame,'Time: {0:.8s}'.format(current_time),(30,210),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,0),2,cv2.LINE_AA)

        # Calculate framerate
        t2 = cv2.getTickCount()
        time1 = (t2-t1)/self.freq
        self.frame_rate_calc= 1/time1

        # Set the old time
        self.end_time = self.start_time

        return frame

