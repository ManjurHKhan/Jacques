from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

camera = PiCamera()
res_y = 640
res_x = 480
camera.resolution = (640,480)
camera.framerate = 15
camera.hflip = True
camera.vflip = True
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)

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

def drawContour(img, contour, color, thickness=8):
    cv2.drawContours(img, [contour], -1, color, thickness)

def close(img):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

def getDrawing(input):
    gray = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _,thresh = cv2.threshold(gray, 100, 255, \
            cv2.THRESH_BINARY_INV)
    return thresh

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
    cv2.imshow("Frame", image)
    break

print(contour)
cv2.waitKey(0)
