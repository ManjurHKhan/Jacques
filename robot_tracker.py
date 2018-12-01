from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

class RobotTracker:

    def __init__(self, camera):
        self.camera = camera
        res_x = 1280
        res_y = 1280
        self.camera.resolution = (res_x,res_y)
        self.camera.framerate = 30
        self.camera.hflip = False
        self.camera.vflip = False
        self.rawCapture = PiRGBArray(self.camera, size=(res_x, res_y))

    def getLargestContour(self, input): 
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

    def drawContour(self, img, contour, color, thickness=8):
        cv2.drawContours(img, [contour], -1, color, thickness)

    def close(self, img):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    def track(self):
        time.sleep(0.1)
        
        #for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", \
         #       use_video_port=True):
        self.camera.capture(self.rawCapture, format="bgr")
        image = self.rawCapture.array
        crop_y = 0
        crop_lx = 30
        crop_rx = 70
        res_x = self.camera.resolution[0]
        res_y = self.camera.resolution[1]
        image = image[crop_y:res_y-crop_y, crop_lx:res_x-crop_rx]
        image = self.close(image)
        contour = self.getLargestContour(image)
        moment = cv2.moments(contour)
        if (moment["m00"] != 0):
            cx = int(moment["m10"]/moment["m00"]) + crop_lx
            cy = int(moment["m01"]/moment["m00"]) + crop_y
        else:
            cx, cy = 0, 0
        # Calculate angle.
        width = np.size(image, 0)
        height = np.size(image, 1)
        #xDist = cx - width/2
        #yDist = cy - height
        #angle = np.arctan2(xDist, yDist) * (180 / np.pi)
        #print("Angle: " + str(angle))
        # + angle = left, - angle = right
        
        # Draw stuff
        cv2.circle(image, (cx, cy), 4, (255, 255, 0), 2)
        self.drawContour(image, contour, (0, 0, 255), 4)
        cv2.line(image, (cx, cy), (width/2, height), (0, 255, 0), 4)
        cv2.imwrite("robot.jpg", image)
        return (cx, cy)

        # Clear the stream for the next frame.
        #self.rawCapture.truncate(0)

        #if key == ord("q"):
        #    break
#camera = PiCamera()
#tracker = RobotTracker(camera)
#tracker.track()
