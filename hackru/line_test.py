import time
import math
import numpy as np
import pid
import sys
#from MotorHatLibrary.examples import Robot
import Robot
import socket

# open a socket connection
host = ""
port = 9001

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
connection.bind((host, port))
#while True:
connection.listen(1)
conn, addr = connection.accept()
keep_going = True

#turn_p = 0.5
#turn_d = 0.01
#turn_i = 0.005
#turn_s = 0.005
#maxSpeed = 75
turn_d = 0.01
turn_i = 0.005
turn_s = 0.005
turn_p = 0.9
maxSpeed = 75.0
turnControl = pid.PIDController(turn_p, turn_i, turn_d, turn_s)
speedControl = pid.PIDController(0, 0, 0, turn_s)
robot = Robot.Robot()
move = True
i = 0
max_tries = 5
current_try = 1
prev_speed = maxSpeed
prev_steer = 0
break_cnt = 0
def move_robot(xDist, yDist, framerate):
    
    global prev_speed, maxSpeed
    print("move robot", xDist, yDist, framerate)
    MAX_ABS_SPEED = 255.0
    #MIN_SPEED = 5.0
    turn_p = maxSpeed / MAX_ABS_SPEED#0.5
    turn_d = maxSpeed / (MAX_ABS_SPEED * 50)#0.01
    turn_i = maxSpeed / (MAX_ABS_SPEED * 100)#0.005
    turn_s = maxSpeed / (MAX_ABS_SPEED * 25)
    turnControl.setGains(turn_p, turn_i, turn_d, 0)
    speedControl.setGains(0, 0, 0, turn_s)
    steer = turnControl.pid(xDist, yDist, 1/framerate)
    speedDiff = speedControl.pid(xDist, yDist, 1/framerate)
    #print("Steer: " + str(steer))
    #print("SpeedDiff: " + str(speedDiff)) 
    
    speed = maxSpeed + speedDiff
    if speed < 0 or speed > 255:
        speed = prev_speed

    print('Speed is ', speed)
    prev_speed = speed
    prev_steer = steer
    print('Steer is ', steer)
    duration = 1/framerate
    errorThresh = 5.0
    if (move and abs(xDist) > errorThresh):
        absSteer = abs(steer)
        robot.smooth_turn(int(speed), int(steer))

# Accept connection
def parse_data(conn, data):
    global break_cnt
    if data == 'START':
        conn.send('OK'.encode())
        return
    elif data == 'STOP':
        robot.stop()
        return
    elif data == '':
        break_cnt+=1
        if break_cnt > 6:
            robot.stop()
        print("no data here sigh")
        return
    try:
        command, x, y, framerate = data.split(' ')
        if command  == 'GO':
            print("uh go?")
            move_robot(float(x), float(y), float(framerate))
        else:
            print("I am here for x.x %s" % (data))
    except:
        print("keep going")
#try:
while True:
    # establish a connection
    data = conn.recv(1024)
    data = data.strip()
    data = str(data.decode())
    print("recieved data --- ", data)
    #conn.send('Do you know the meaning of life?\r\n'.encode())
    #keep_going = False
    parse_data(conn, data)
    if not keep_going:
        break;
    # print(keep_going)
#except:
print("something went wrong")

conn.close()



