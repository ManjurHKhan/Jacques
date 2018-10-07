import socket

host = ""
port = 9001

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.bind((host, port))
connection.listen()
conn, addr = connection.accept()
print(conn, addr)
keep_going = True
try:
    while True:
        # establish a connection
        data = conn.recv(40000)
        data = data.strip()
        data = str(data.decode())
        print("recievedj data --- ", data)
        if data == 'START':
            conn.send('OK'.encode())
        if not keep_going:
            break;
        # print(keep_going)
except:
    print("something went wrong")

conn.close()
