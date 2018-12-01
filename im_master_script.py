from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import socket               # Import socket module
from drawing import DrawingExtractor
from robot_tracker import RobotTracker

def monitor_robot(s):
    dc_i = 0
    init_x = -1
    init_y = -1
    prev_x, prev_y, prev_dc_x, prev_dc_y = -1, -1, -1, -1
    MAX_X_ERROR = 100
    MAX_Y_ERROR = 100
    for frame in camera.capture_continuous(rawCapture, format="bgr", \
        use_video_port=True):
        image = frame.array
        crop_y = 25
        crop_lx = 70
        crop_rx = 10
        image = image[crop_y:res_y-crop_y, crop_lx:res_x-crop_rx]
        image = close(image)
        contour = getRobotContour(image)
        moment = cv2.moments(contour)
        if (moment["m00"] != 0):
            cx = int(moment["m10"]/moment["m00"])
            cy = int(moment["m01"]/moment["m00"])
        else:
            cx, cy = 0, 0
        # Calculate angle.
        width = np.size(image, 0)
        height = np.size(image, 1)
        if dc_i >= dc.shape[0]:
            send_data(s, "STOP")
        x = dc[dc_i, 0, 0]
        y = dc[dc_i, 0, 1]
        if init_x < 0 and init_y < 0:
            init_x = cx
            init_y = cy
            prev_x = cx
            prev_y = cy
            prev_dc_x = x
            prev_dc_y = y
        print("dc_x", x, "dc_y", y)
        print("cx", cx, "cy", cy)
        xDist = (cx - prev_x) - \
        (x - prev_dc_x)
        yDist = (cy - prev_y) - \
        (y - prev_dc_y)
        print("xDist", xDist)
        print("yDist", yDist)
        if xDist < 0:
            xDist = max(xDist, -1* MAX_X_ERROR)
        else:
            xDist = max(xDist, MAX_X_ERROR)
        
        if yDist < 0:
            yDist = max(yDist, -1* MAX_Y_ERROR)
        else:
            yDist = max(yDist, MAX_Y_ERROR)

        prev_x = cx
        prev_y = cy
        prev_dc_x = x
        prev_dc_y = y
        send_data(s, "GO", xDist, yDist)
        dc_i += 2
        time.sleep(0.01) # Sleep 50 ms.

        # Draw stuff
        cv2.circle(image, (cx, cy), 4, (255, 255, 0), 2)
        drawContour(image, contour, (0, 0, 255), 4)
        cv2.line(image, (cx, cy), (width/2, height), (0, 255, 0), 4)
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        # Clear the stream for the next frame.
        rawCapture.truncate(0)

        if key == ord("q"):
            break

def create_conn():
   port = 9001
   host = "192.168.21.218"
   s = socket.socket()
   s.connect((host, port))
   s.send("START")
   data = s.recv(1024).decode()
   if data == "OK":
       monitor_robot(s)

def send_data(s, comm, x="", y=""):
    s.send("{} {} {} {}".format(comm, str(x), str(y), str(camera.framerate)).encode()) 


camera = PiCamera()
extractor = DrawingExtractor(camera)
robot_res_x = 1280
robot_res_y = 1280
dc = extractor.extract((robot_res_x, robot_res_y))
for pt in dc:
    print("{}\t{}".format(pt[0], pt[1]))
time.sleep(5.0)
tracker = RobotTracker(camera)
r_pos = tracker.track()
print("{}\t{}".format(r_pos[0], r_pos[1]))
'''
blank = np.zeros((robot_res_y, robot_res_x), np.uint8)
cv2.circle(blank, (r_pox[0], r_pox[1]), 4, (255, 255, 0), 2)
drawContour(blank, dc, (0, 0, 255), 4)
cv2.imwrite("master.jpg", blank)
'''

#create_conn()
