import time
import cv2
import numpy as np

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

def getDrawing(input):
    gray = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _,thresh = cv2.threshold(gray, 150, 255, \
            cv2.THRESH_BINARY_INV)
    return thresh
    
image = cv2.imread("circle.jpg")
thresh = getDrawing(image)
close_times = 1
for i in range(close_times):
    thresh = close(thresh)
contour = getDrawingContour(thresh)
#drawContour(image, contour, (0, 0, 255))
for pt in contour:
    print(pt)
    cv2.circle(image, (pt[0][0], pt[0][1]), 3, (0, 0, 255))
cv2.namedWindow("image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("image", 1000, 1000)
cv2.imshow("image", image)
print(contour.shape)

cv2.waitKey(0)
