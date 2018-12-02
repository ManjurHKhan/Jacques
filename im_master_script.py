from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import sys
import cv2
import numpy as np
import socket
import math
from drawing import DrawingExtractor
from robot_tracker import RobotTracker
from scale_contour import Transformer

camera = PiCamera()
camera.framerate = 40
ROBOT_RES = (240, 240)
heading_buffer = []
buffer_len = 5

def pause():
    print("PAUSE")
    send_data(s, "PAUSE")
    raw_input("Press any key to resume...")
    print("Key pressed")

def min_dist_index(path, cx, cy, start, end):
    min_dist = sys.maxint
    opt_i = -1
    for i in range(start, end):
        curr_pt = path[i]
        dist = math.sqrt((cx - curr_pt[0]) ** 2 + (cy - curr_pt[1]) ** 2)
        if dist < min_dist:
            min_dist = dist
            opt_i = i
    return opt_i

def calculate_heading(new_heading):
    if len(heading_buffer) == buffer_len:
        heading_buffer.pop(0)
    heading_buffer.append(new_heading)
    x, y = map(list, zip(*heading_buffer))
    avg_x = sum(x) / len(heading_buffer)
    avg_y = sum(y) / len(heading_buffer)
    return avg_x, avg_y

def normalized(heading):
    norm = math.sqrt((heading[0]) ** 2 + (heading[1]) ** 2)
    if (norm == 0):
        return (0, 0)
    return heading[0] / norm, heading[1] / norm
    

def monitor_robot(s, path):
    tracker = RobotTracker(ROBOT_RES)
    camera.resolution = ROBOT_RES
    rawCapture = PiRGBArray(camera, size=ROBOT_RES)
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    cx, cy = tracker.track(image)
    scale = 4
    path = Transformer().transform(path, (cx, cy), scale) # Scale path.
    path = [(int(i), int(j)) for i, j in path]
    rawCapture.truncate(0)
    index = 0
    p_iters = 500
    p_i = 0
    prev_time = time.time()
    prev_cx = prev_cy = -1
    for frame in camera.capture_continuous(rawCapture, format="bgr", \
        use_video_port=True):
        image = frame.array
        cx, cy = tracker.track(image)
        look_ahead = 25
        end = int(len(path) * 3/4)
        print(len(path))
        opt_index = min_dist_index(path, cx, cy, index, end)
        if opt_index == -1:
            print("LESS THAN -1")
            return
        opt_index += look_ahead
        print("opt_index:", opt_index)
        index = opt_index - look_ahead
        print("index:", index)
        #x_diff = cx - path[opt_index][0] # + -> left, - -> right
        #y_diff = cy - path[opt_index][1]
        #x_diff *= -1 # FOR NOW
        if prev_cx == -1: # first time
            prev_cx = cx
            prev_cy = cy
        heading = (cx - prev_cx, cy - prev_cy)
        avg_heading = calculate_heading(heading)
        command = "GO"
        #prev_s_time = time.time()
        #print("Socket time:", time.time() - prev_s_time)
        # Draw stuff
        opt_x = path[opt_index][0]
        opt_y = path[opt_index][1]
        ideal_heading = (opt_x - cx, opt_y - cy)
        print("ideal heading:", ideal_heading)
        n_i_heading = normalized(ideal_heading)
        n_a_heading = normalized(avg_heading)
        # Calculate angle.
        ideal_angle = np.arctan2(n_i_heading[0], n_i_heading[1]) \
                * (180 / np.pi)
        actual_angle = np.arctan2(n_a_heading[0], n_a_heading[1]) \
                * (180 / np.pi)
        print("ideal_angle:", ideal_angle)
        print("actual_angle:", actual_angle)
        send_data(s, command, actual_angle - ideal_angle)
        for pt in path:
            cv2.circle(image, (pt[0], pt[1]), 1, (0, 255,255), 2) # circle
        cv2.circle(image, (cx, cy), 2, (255, 255,0), 2) # center robot
        cv2.circle(image, (opt_x, opt_y), 2, (0, 0, 255), 2) # opt look ahead
        #cv2.circle(image, (path[opt_index-look_ahead][0], path[opt_index-look_ahead][1]), 8, (255, 0, 0), 2) # opt
        print("avg_heading:", avg_heading)
        cv2.line(image, (cx + (avg_heading[0] * 50), \
                cy + (avg_heading[1] * 50)), (cx, cy), (0, 255, 0), 4) # actual heading
        cv2.line(image, (cx, cy), (opt_x, opt_y) , (0, 0, 255), 4)
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("frame", (50, 50))
        cv2.imshow("frame", image)
        key = cv2.waitKey(1) & 0xFF
        if p_i == p_iters:
            print(str(index) + " of " + str(len(path)))
            pause()
            p_i = 0
        else:
            p_i += 1
        if key == ord("q"):
            break
        if key == ord("p"):
            pause()
        # Clear the stream for the next frame.
        rawCapture.truncate(0)
        post_time = time.time()
        print("Per frame:", post_time - prev_time)
        prev_time = post_time

def create_conn(s, path):
   port = 9001
   host = "172.26.13.84"
   s.connect((host, port))
   s.send("START")
   data = s.recv(1024).decode()
   if data == "OK":
       print(s)
       print("Starting to track...")
       monitor_robot(s, path)

def send_data(s, comm, angle_diff=""):
    str_to_send = "{} {} {}".format(comm, str(angle_diff), str(camera.framerate)).encode()
    print("sending: ", str_to_send)
    s.send(str_to_send) 

print("Processing contours...")
extractor = DrawingExtractor(camera)
path = extractor.extract(ROBOT_RES)
#for pt in path:
#    print("{}\t{}".format(pt[0], pt[1]))
sleep_duration = 4
for i in range(sleep_duration):
    print(str(sleep_duration - i) +  " seconds til go time")
    time.sleep(1)
s = socket.socket()
create_conn(s, path)
s.close()
