from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

camera = PiCamera()
res_y = 640
res_x = 480
camera.resolution = (res_y,res_x)
camera.framerate = 15
camera.hflip = True
camera.vflip = True
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)

def getLargestContour(input):
    _,contours, hierarchy = cv2.findContours(input, cv2.RETR_EXTERNAL, \
            cv2.CHAIN_APPROX_SIMPLE)
    # Get largest contour (by area)
    maxIndex = 0
    maxArea = 0
    return contours
    #if (len(contours) > 0):
     #   return max(contours, key = cv2.contourArea)
    #else:
     #   return None

def getRobotContour(input):
    AMAZON_MIN = np.array([10, 50, 50], np.uint8)
    AMAZON_MAX = np.array([20, 255, 255], np.uint8) # HSV
    hsv_img = cv2.cvtColor(input,cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(hsv_img, AMAZON_MIN, AMAZON_MAX)
    return thresh

def drawContour(img, contour, color, thickness=8):
    cv2.drawContours(img, [contour], -1, color, thickness)

def close(img):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

for frame in camera.capture_continuous(rawCapture, format="bgr", \
        use_video_port=True):
    image = frame.array
    crop_y = 25
    crop_lx = 70
    crop_rx = 10
    image = image[crop_y:res_y-crop_y, crop_lx:res_x-crop_rx]
    frame_thresh = getRobotContour(image)
    image = close(frame_thresh)
    contours = getLargestContour(image)
    cv2.imshow("Frame", frame_thresh)
    key = cv2.waitKey(1) & 0xFF

    # Clear the stream for the next frame.
    rawCapture.truncate(0)

    if key == ord("q"):
        break
