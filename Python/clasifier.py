import os
import socket
from ospf import *
from ospf2 import *
from ipv4 import *
from state_machine import *
from ethsend import human_mac_to_bytes
import traceback
from tcb import *
from mutils import *


ospf_packet1={
    "Router_ID":"",
    "neighbor":"",
    "type":0,
    "local":"192.168.0.1",
    "state":"",
    "source_ip": "192.168.0.1",
    "dest_ip":"224.0.0.5",
    "mask":"255.255.255.0",
    "seen":"No",
    "area_id":"0.0.0.0",
    "sequence_number":0,
    }

buffer =[]
buffer.append(ospf_packet1)

data={}


def encode(ospf_packet1):
    if ospf_packet1["state"]=="DB_DESC":
        print("DB_DESC")
        dstmac = "00:0f:e2:dd:9e:2c"  
        ospf_packet1["dest_ip"]="192.168.0.3"
        srcmac = "7c:c2:c6:45:3d:1f"
    
def send_dd(ospf_packet1):
    print("In DB Des")
    ip_proto = 89
    ospf_header_ = ospf_header(ospf_packet1,2) #type 2 packet
    ospf_packet2 = ospf_dd(ospf_header_,ospf_packet1)
    framesize = 20 + len(ospf_packet2)
    ospf_packet1["dest_ip"]="192.168.0.3"  #ospf_packet1["neighbor"] #ojo aqui con este cambio!
    dstmac = "01:00:5E:00:00:05"
    srcmac = "7c:c2:c6:45:3d:1f"
    ip_header_=ip_header( ospf_packet1["source_ip"], ospf_packet1["dest_ip"], ip_proto, framesize )
    eth_type = b'\x08\x00'
    frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
    #print("Frame sent length:",len(frame)-14,"neig",)
    conn2.sendall(frame)   



def send_hello(ospf_packet1):
    print("In send hello.")
    ip_proto = 89
    if ospf_packet1["state"]=="":
        print(" '' ")
        ospf_header_ = ospf_header(ospf_packet1,1)
        ospf_packet2 = ospf_hello(ospf_header_,ospf_packet1)   
        framesize = 20+ len(ospf_packet2) 			#IP header size is hard coded
        #print("Frame size ",framesize)
        #print("State:",ospf_packet1["state"])
        ospf_packet1["dest_ip"]=="224.0.0.5"
        dstmac = "01:00:5E:00:00:05"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( ospf_packet1["source_ip"], ospf_packet1["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        #print("Frame sent length:",len(frame)-14,"neig",)
        conn2.sendall(frame)

    if ospf_packet1["state"]=="Init":
        print("--> init")
        ospf_header_ = ospf_header(ospf_packet1,1)
        ospf_packet2 = ospf_hello(ospf_header_,ospf_packet1)   
        framesize = 20+ len(ospf_packet2) 			#IP header size is hard coded
        #print("Frame size ",framesize)
        #print("State:",ospf_packet1["state"])
        ospf_packet1["dest_ip"]=="224.0.0.5"
        dstmac = "01:00:5E:00:00:05"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( ospf_packet1["source_ip"], ospf_packet1["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        print("Frame sent length:",len(frame)-14,"neig",)
        conn2.sendall(frame)

    if ospf_packet1["state"]=="2-way":
        print("--> 2-way")
        ospf_header_ = ospf_header(ospf_packet1,1)
        ospf_packet2 = ospf_hello(ospf_header_,ospf_packet1)   
        framesize = 20 + len(ospf_packet2) 			#IP header size is hard coded
        #print("Frame size ",framesize)
        #print("State:",ospf_packet1["state"])
        framesize = 20 + len(ospf_packet2)
        ospf_packet1["dest_ip"]=="224.0.0.5"
        dstmac = "01:00:5E:00:00:05"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( ospf_packet1["source_ip"], ospf_packet1["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        #print("Frame sent length:",len(frame)-14,"neig",)
        conn2.sendall(frame)



def decode(pkt):
    # New packet to decode
    try:
        ip_header = ip_header_decoded(pkt[0:20])
        print("\nNew packet from:",id2str(ip_header["SRC"]))
        header=parseOspfHdr(pkt[20:44])
        
        
        if int(header["TYPE"])==1 and int(header["LEN"])==44:
            ospf_packet1["Router_ID"]=id2str(header["RID"])
            ospf_packet1["state"]="Init"
            ospf_packet1["neighbor"]=""
            ospf_packet1["type"]=int(header["TYPE"])
            classify(ospf_packet1)
        if int(header["TYPE"])==1 and int(header["LEN"])>44:
            ospf_packet1["Router_ID"]=id2str(header["RID"])
            ospf_packet1["type"]=int(header["TYPE"])
            neig=struct.unpack("> L",(pkt[64:]))
            ospf_packet1["neighbor"]= id2str(neig[0])
            classify(ospf_packet1)
        if int(header["TYPE"])==2 :
            ospf_packet1["Router_ID"]=id2str(header["RID"])
            ospf_packet1["type"]=int(header["TYPE"])
            classify(ospf_packet1)
        
            
    except Exception as e: 
        traceback.print_exc()
        print("Errored packet")
    
def rid_exist(ospf_packet1):
    a=0
    print("RID exists?")

    for parts in buffer:
        if parts["Router_ID"]==ospf_packet1["Router_ID"]:
            print(" yes.")
            return parts
    print(" No.")
    return 0

def classify(ospf_packet1):
    print("In clasify")
    print("RID: ",ospf_packet1["Router_ID"])
    print("Neighbor: ",ospf_packet1["neighbor"])
    print("Type: ",ospf_packet1["type"])
    parts= rid_exist(ospf_packet1)
    if parts!=0:
        pass
    else:
        print("No.")
        print("Create TCB.")
        ospf_packet1["state"]="Init"
        buffer.append(ospf_packet1)
        send_hello(ospf_packet1)
        return 
    print("Is Hello?")
    if ospf_packet1["type"]== 1:
        print("Yes.")
        print("Own RID?")
        if ospf_packet1["neighbor"]==parts["local"]:
            print(" Yes")
            parts["state"]="2-way"
            send_hello(parts)
            return 
        else:
            print(" No")
            parts["state"]="Init"
            send_hello(parts)
            return
    print("Is BDDES?")
    if ospf_packet1["type"]== 2:
        print(" Yes.")
        send_dd(parts)



 
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

conn, addr = s.accept()
print('Connection by Ethernet receiver')
conn2, addr2 = sender.accept()
print("Connection by Sender's")
# Process 'request'

# Start listening loop
while True:
    
    while True:
        data = conn.recv(2048)
        print("Length :" ,len(data))
        if not data:
            break
        decode(data)
        # Send 'response'

        #print("Packet: ",data)
        conn.sendall(data)
