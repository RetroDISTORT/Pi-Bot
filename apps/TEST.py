# CLIENT
import socket

HEADERSIZE = 10

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432        # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    full_msg = ''
    new_msg = True
    while True
    msg = s.recv(16)
    if new_msg:
        print(f"new message length: {msg[:HEADERSIZE]}")
        msglen = int(msg[:HEADERSIZE])
        #s.sendall(b"Hello, world")
        msg = s.recv(1024)
    
print(msg.decode("utf-8"))
