from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

camera = PiCamera()
res_x = 1280
res_y = 1280
camera.resolution = (res_x,res_y)
camera.hflip = True
camera.vflip = True
print("contrast:", camera.contrast)
camera.saturation = 0
camera.brightness = 60
camera.contrast = 0 # default
rawCapture = PiRGBArray(camera, size=(res_x, res_y))

time.sleep(0.1)

def getDrawingContour(drawing):
    _,contours, hierarchy = cv2.findContours(drawing, cv2.RETR_EXTERNAL, \
            cv2.CHAIN_APPROX_NONE)
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
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

def getThresh(input):
    gray = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = 130
    _,thresh = cv2.threshold(gray, thresh, 255, \
            cv2.THRESH_BINARY_INV) 
    return thresh



camera.capture(rawCapture, format="bgr")
image = rawCapture.array

#crop_y = 170
#crop_lx = 150
#crop_rx = 120
crop_by = 80
crop_ty = 100
crop_lx = 120
crop_rx = 300
# x and y reversed bc of rows and columns in array.
#image = image[crop_ty:res_y - crop_by, crop_lx:res_x - crop_rx] 
drawing_frame = image[crop_ty:res_y - crop_by, crop_lx:res_x - crop_rx] 
thresh = getThresh(drawing_frame)
thresh = close(thresh)
contour = getDrawingContour(thresh)

for pt in contour:
    print(pt)
    cv2.circle(image, (pt[0][0] + (crop_lx), \
            pt[0][1] + crop_ty), 3, (0, 0, 255))
cv2.namedWindow("image", cv2.WINDOW_NORMAL)
cv2.namedWindow("thresh", cv2.WINDOW_NORMAL)
cv2.resizeWindow("image", (500, 500))
cv2.resizeWindow("thresh", (500, 500))
# lower res test
camera.resolution = (res_x/2, res_y/2)
rawCaptureLow = PiRGBArray(camera, size=(res_x/2, res_y/2))
rawCaptureLow.truncate(0)
camera.capture(rawCaptureLow, format="bgr")
low_res_img = rawCaptureLow.array
for pt in contour:
    print(pt)
    cv2.circle(low_res_img, ((pt[0][0] + (crop_lx))/2, \
            (pt[0][1] + crop_ty)/2), 3, (0, 0, 255))
cv2.imshow("image", image)
cv2.imshow("low_res", low_res_img)
cv2.imshow("thresh", thresh)

print(contour.shape)
cv2.waitKey(0)
