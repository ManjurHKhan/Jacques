from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import socket               # Import socket module

camera = PiCamera()
res_y = 640
res_x = 480
camera.resolution = (640,480)
camera.framerate = 15
camera.hflip = True
camera.vflip = True
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)

def getRobotContour(input): 
    AMAZON_MIN = np.array([10, 50, 50], np.uint8)
    AMAZON_MAX = np.array([20, 255, 255], np.uint8) # HSV
    hsv_img = cv2.cvtColor(input,cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(hsv_img, AMAZON_MIN, AMAZON_MAX)
    _,contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, \
            cv2.CHAIN_APPROX_SIMPLE)
    # Get largest contour (by area)
    maxIndex = 0
    maxArea = 0
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])
        if area > maxArea:
            maxArea = area
            maxIndex = i
    #return max(contours, key = cv2.contourArea)
    return contours[maxIndex]

def drawContour(img, contour, color, thickness=8):
    cv2.drawContours(img, [contour], -1, color, thickness)

def close(img):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

def getDrawingContour(drawing):
    _,contours, hierarchy = cv2.findContours(drawing, cv2.RETR_EXTERNAL, \
            cv2.CHAIN_APPROX_SIMPLE)
    # Get largest contour (by arc length)
    maxIndex = 0
    maxLength = 0
    for i in range(len(contours)):
        #arcLength = cv2.arcLength(contours[i], True)
        arcLength = cv2.contourArea(contours[i])
        if arcLength > maxLength:
            maxLength = arcLength
            maxIndex = i
    return contours[maxIndex]

def getDrawing(input):
    gray = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _,thresh = cv2.threshold(gray, 100, 255, \
            cv2.THRESH_BINARY_INV)
    return thresh

def extract_image_contour():
    for frame in camera.capture_continuous(rawCapture, format="bgr", \
            use_video_port=True):
        image = frame.array
        crop_y = 170
        crop_lx = 150
        crop_rx = 120
        image = image[crop_y:res_y-crop_y, crop_lx:res_x-crop_rx]
        thresh = getDrawing(image)
        thresh = close(thresh)
        contour = getDrawingContour(thresh)
        print(contour.shape)
        resized = cv2.resize(thresh, (640, 480))
        crop_y = 50
        crop_lx = 140
        crop_rx = 20
        resized = resized[crop_y:res_y-crop_y, crop_lx:res_x-crop_rx]
        drawContour(image, contour, (0, 0, 255))
        #cv2.imshow("Frame", image)
        cv2.imwrite("drawing.jpg", image)
        return contour


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



dc = extract_image_contour()
print(dc)
# Clear the stream for the next frame.
rawCapture.truncate(0)
time.sleep(5.0)
create_conn()
