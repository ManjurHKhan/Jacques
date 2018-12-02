from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import socket               # Import socket module
from drawing import DrawingExtractor
from robot_tracker import RobotTracker
from scale_contour import Transformer

camera = PiCamera()
ROBOT_RES = (640, 640)

def monitor_robot(path):
    tracker = RobotTracker(ROBOT_RES)
    camera.resolution = ROBOT_RES
    rawCapture = PiRGBArray(camera, size=ROBOT_RES)
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    cx, cy = tracker.track(image)
    scale = 2
    path = Transformer().transform(path, (cx, cy), scale)
    rawCapture.truncate(0)
    print(len(path))
    for frame in camera.capture_continuous(rawCapture, format="bgr", \
        use_video_port=True):
        image = frame.array
        cx, cy = tracker.track(image)

        # Calculate angle.
        width = np.size(image, 0)
        height = np.size(image, 1)
        # Draw stuff
        cv2.circle(image, (cx, cy), 4, (255, 255, 0), 2)
        cv2.line(image, (cx, cy), (width/2, height), (0, 255, 0), 4)
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("frame", (500, 500))
        cv2.imshow("frame", image)
        key = cv2.waitKey(1) & 0xFF

        # Clear the stream for the next frame.
        rawCapture.truncate(0)

        if key == ord("q"):
            break

def create_conn(path):
   port = 9001
   host = "172.26.13.84"
   s = socket.socket()
   s.connect((host, port))
   s.send("START")
   data = s.recv(1024).decode()
   if data == "OK":
       print(data)
       exit(0)

def send_data(s, comm, x="", y=""):
    s.send("{} {} {} {}".format(comm, str(x), str(y), str(camera.framerate)).encode()) 


extractor = DrawingExtractor(camera)
path = extractor.extract(ROBOT_RES)
#for pt in path:
#    print("{}\t{}".format(pt[0], pt[1]))
time.sleep(5.0)
create_conn(path)
