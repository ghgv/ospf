import os
import socket
 
# IPC parameters
SOCK_FILE = '/tmp/simple-ipc.socket'
 
# Setup socket
if os.path.exists(SOCK_FILE):
    os.remove(SOCK_FILE)
 
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(SOCK_FILE)
s.listen(0)
 
# Start listening loop
while True:
    # Accept 'request'
    conn, addr = s.accept()
    print('Connection by Ethernet receiver')
    # Process 'request'
    while True:
        data = conn.recv(2048)
        print("Length :" ,len(data))
        if not data:
            break
        # Send 'response'
        print("PROTO:",data)
        conn.sendall(data)
