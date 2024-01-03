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
    "local":"192.168.0.1",
    "state":"",
    "source_ip": "192.168.0.1",
    "dest_ip":"224.0.0.5",
    "mask":"255.255.255.0",
    "seen":"No",
    "area_id":"0.0.0.0"
    }

buffer =[]
buffer.append(ospf_packet1)

data={}


def encode(ospf_packet1):
    print("in encode")
    ip_proto = 89
    if ospf_packet1["status"]=="Init":
        print("init")
        ospf_header_ = ospf_header(ospf_packet1,1)
        ospf_packet2 = ospf_hello(ospf_header_,ospf_packet1)   
        framesize = 20+ len(ospf_packet2) 			#IP header size is hard coded
        print("Frame size ",framesize)
        print("State:",ospf_packet1["state"])
        ospf_packet1["dest_ip"]=="224.0.0.5"
        dstmac = "01:00:5E:00:00:05"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( ospf_packet1["source_ip"], ospf_packet1["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        print("Frame sent length:",len(frame)-14,"neig",)
        conn2.sendall(frame)

    if ospf_packet1["status"]=="2-way":
        print("2-way")
        ospf_header_ = ospf_header(ospf_packet1,1)
        ospf_packet2 = ospf_hello(ospf_header_,ospf_packet1)   
        framesize = 20 + len(ospf_packet2) 			#IP header size is hard coded
        print("Frame size ",framesize)
        print("State:",ospf_packet1["state"])
        framesize = 20 + len(ospf_packet2)
        ospf_packet1["dest_ip"]=="224.0.0.5"
        dstmac = "01:00:5E:00:00:05"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( ospf_packet1["source_ip"], ospf_packet1["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        print("Frame sent length:",len(frame)-14,"neig",)
        conn2.sendall(frame)

    if ospf_packet1["status"]=="DB_DESC":
        print("DB_DESC")
        dstmac = "00:0f:e2:dd:9e:2c"  
        ospf_packet1["dest_ip"]="192.168.0.3"
        srcmac = "7c:c2:c6:45:3d:1f"
    

    


def decode(pkt):
    
    try:
        ip_header = ip_header_decoded(pkt[0:20])
        print(ip_header["SRC"])
        header=parseOspfHdr(pkt[20:44])
        print("OSPF version: ",header["VER"],"Type: ",header["TYPE"],"LEN: ",header["LEN"])
        if int(header["TYPE"])==1 and int(header["LEN"])==44:
            ospf_packet1["Router_ID"]=id2str(header["RID"])
            ospf_packet1["state"]="Init"
            ospf_packet1["neighbor"]=""
            print("RID, Hello, No seen")
            classify(ospf_packet1)
        if int(header["TYPE"])==1 and int(header["LEN"])>44:
            print("RID, Hello, Seen")
            ospf_packet1["Router_ID"]=id2str(header["RID"])
            neig=struct.unpack("> L",(pkt[64:]))
            ospf_packet1["neighbor"]= id2str(neig[0])
            classify(ospf_packet1)
        if int(header["TYPE"])==2 :
            print("DDESC")
        
    except Exception as e: 
        traceback.print_exc()
        print("Errored packet")
    



def classify(ospf_packet1):
    print("In clasify")
    a=0
    #print("Buffer:",buffer)
    print("ospf_packet1: ",ospf_packet1)
    for parts in buffer:
        if parts["Router_ID"]==ospf_packet1["Router_ID"]:
            a=1
        else:
            a=0
    if a==0:
        buffer.append(ospf_packet1)
        print(buffer)


    for parts in buffer:    
        if parts["Router_ID"]==ospf_packet1["Router_ID"] and ospf_packet1["neighbor"]=="":
            parts["status"]="Init"
            encode(parts)
        if parts["Router_ID"]==ospf_packet1["Router_ID"] and ospf_packet1["neighbor"]==ospf_packet1["local"]:
            parts["status"]="2-way"
            
            encode(parts)
        
    
        else:
            pass
            
    
    pass

 
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
