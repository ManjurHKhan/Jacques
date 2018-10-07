#!/usr/bin/python3

#author: Manjur Khan 110430915
#author: Huiying Song 110589105

# Use Python3
# Program ran with Python 3.6.4 on Linux Mate


ALL_OK = "200 OK"
UNSUPPORTED = "220 UNSUPPORTED"
BAD_REQUEST = "400 BAD_REQUEST"
NOT_FOUND = "404 NOT FOUND"

keep_going = True

table = {}

def handle_get(body):
    # print("in body")
    global table
    if body == "":
        return BAD_REQUEST
    if body in table:
        return ALL_OK + " " + table[body]
    return NOT_FOUND

def handle_clear():
    # print("in clear")
    global table
    table.clear()
    return ALL_OK

def handle_delete(body):
    # print("in delete")
    global table
    if body == "":
        return BAD_REQUEST
    if body in table:
        table.pop(body)
    return ALL_OK

def handle_put(body):
    # print("in put")
    global table
    if body == "":
        return BAD_REQUEST
    try:
        key, value = body.split(' ', 1)
    except:
        return BAD_REQUEST
    table[key] = value
    return ALL_OK

def parse_requests(req):
    global table, keep_going
    try:
        command, body = req.split(' ', 1)
        command = command.strip()
        body = body.strip()
        # print(command, " -- ", body)
        if command == "GET":
            return handle_get(body)
        elif command == "PUT":
            return handle_put(body)
        elif command == "DELETE":
            return handle_delete(body)
        elif command == "CLEAR":
            return handle_clear()
        elif command == "QUIT":
            keep_going = False
            return ALL_OK
        else:
            # print("life is hard")
            return UNSUPPORTED
    except:
        if req == "QUIT":
            keep_going = False
            return ALL_OK
        elif req == "CLEAR":
            return handle_clear()
        return UNSUPPORTED



import socket

host = ""
port = 9001

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.bind((host, port))
connection.listen()
conn, addr = connection.accept()
keey_going = True
try:
    while True:
        # establish a connection
        data = conn.recv(40000)
        data = data.strip()
        data = str(data.decode())
        conn.send((parse_requests(data) + '\r\n').encode())
        if not keep_going:
            break;
        # print(keep_going)
except:
    print("something went wrong")

conn.close()

