import os
ESCAPE_KEY = 27
CWD_PATH = os.getcwd()
MODEL_NAME = "nodes"
GRAPH_NAME = "detect.tflite"
LABELMAP_NAME = "labelmap.txt"
CONFIG_NAME = "config.ini"
min_conf_threshold = float(0.5)
# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)
# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)
input_mean = 127.5
input_std = 127.5