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

def getLargestContour(input): 
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

for frame in camera.capture_continuous(rawCapture, format="bgr", \
        use_video_port=True):
    image = frame.array
    crop_y = 25
    crop_lx = 70
    crop_rx = 10
    image = image[crop_y:res_y-crop_y, crop_lx:res_x-crop_rx]
    image = close(image)
    contour = getLargestContour(image)
    moment = cv2.moments(contour)
    if (moment["m00"] != 0):
        cx = int(moment["m10"]/moment["m00"])
        cy = int(moment["m01"]/moment["m00"])
    else:
        cx, cy = 0, 0
    # Calculate angle.
    width = np.size(image, 0)
    height = np.size(image, 1)
    xDist = cx - width/2
    yDist = cy - height
    angle = np.arctan2(xDist, yDist) * (180 / np.pi)
    print("Angle: " + str(angle))
    # + angle = left, - angle = right

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
