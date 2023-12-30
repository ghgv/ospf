import os
import socket
from ospf import *
 
# IPC parameters

SOCK_FILE = '/tmp/receiver-classifier.socket'
ETHSEND_CLASSIFIER = '/tmp/ethsend-classifier.socket'
 
########### To receiver ##############

if os.path.exists(SOCK_FILE):
    os.remove(SOCK_FILE)
 
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(SOCK_FILE)
s.listen(0)

########### To Senders ############
if os.path.exists(ETHSEND_CLASSIFIER):
    os.remove(ETHSEND_CLASSIFIER)
 
sender = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sender.bind(ETHSEND_CLASSIFIER)
sender.listen(0)



# Start listening loop
while True:
    # Accept 'request'
    conn, addr = s.accept()
    print('Connection by Ethernet receiver')
    conn2, addr2 = sender.accept()
    print("Connection by Sender's")
    # Process 'request'
    while True:
        data = conn.recv(2048)
        print("Length :" ,len(data))
        if not data:
            break
        # Send 'response'
        print("PROTO:",data)
        conn.sendall(data)
