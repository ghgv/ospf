import os
import time
import copy
import socket
from ospf import *
from ospf2 import *
from ipv4 import *
from state_machine import *
from ethsend import human_mac_to_bytes
import traceback
from tcb import *
from mutils import *



OSPF_LSA_ROUTER = "> HBB LLL HH BBH LL BBH "

ospf_packet1={
    "Router_ID":"",
    "neighbor":"",
    "desinated_router":"0.0.0.0",
    "type":0,
    "local":"192.168.0.1",
    "state":"down",
    "source_ip": "192.168.0.1",
    "dest_ip":"224.0.0.5",
    "mask":"255.255.255.0",
    "seen":"No",
    "area_id":"0.0.0.0",
    "own_sequence_number":1234,
    "peer_sequence_number":0,
    "peer_options":0,
    "master":7, #for the option bits
    "own_router_id": "192.168.5.1",
    "LSA_headers":[],
    }

buffer =[]
buffer.append(copy.deepcopy(ospf_packet1))

data={}


def encode(ospf_packet1):
    if ospf_packet1["state"]=="DB_DESC":
        print("DB_DESC")
        dstmac = "00:0f:e2:dd:9e:2c"  
        ospf_packet1["dest_ip"]="192.168.0.3"
        srcmac = "7c:c2:c6:45:3d:1f"
    
def send_dd(parts):
    print("In DB Description:")
    print("Option flags %x " % (parts["peer_options"] and 2))
    print("Peer Options: %x state: %s" % (parts["peer_options"],parts["state"]))
    ip_proto = 89  
    if parts["state"]=="2-way":
        print("     in 2-way")
        parts["master"]=7
        ospf_header_ = ospf_header(parts,2) #type 2 packet
        ospf_packet2 = ospf_dd(ospf_header_,parts)
        framesize = 20 + len(ospf_packet2)
        parts["dest_ip"]="192.168.0.3"  #parts["neighbor"] #ojo aqui con este cambio!
        dstmac = "00:0f:e2:dd:9e:2c"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( parts["source_ip"], parts["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        parts["state"]="Exstart"
        out=conn2.send(frame) 
        
        return

    if parts["state"]=="Exstart" and parts["peer_options"]==3:
        print("     Exstart")
        a=str2id(ospf_packet1["Router_ID"])
        b=str2id(ospf_packet1["own_router_id"])
        if (a>b):
            parts["master"]=6
        else:
            parts["master"]=7
        ospf_sequence_number =ospf_packet1["own_sequence_number"]
        ospf_header_ = ospf_header(parts,2) #type 2 packet
        ospf_packet2 = ospf_dd(ospf_header_,parts)
        framesize = 20 + len(ospf_packet2)
        parts["dest_ip"]="192.168.0.3"  #parts["neighbor"] #ojo aqui con este cambio!
        dstmac = "00:0f:e2:dd:9e:2c"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( parts["source_ip"], parts["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        out=conn2.send(frame) 
        return

    if parts["state"]=="Exstart" and parts["peer_options"]==2:
        print("     Exstart M set") #Not the last one
        ospf_sequence_number =ospf_packet1["own_sequence_number"]
        ospf_header_ = ospf_header(parts,2) #type 2 packet
        ospf_packet2 = ospf_dd(ospf_header_,parts)
        framesize = 20 + len(ospf_packet2)
        parts["dest_ip"]="192.168.0.3"  #parts["neighbor"] #ojo aqui con este cambio!
        dstmac = "00:0f:e2:dd:9e:2c"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( parts["source_ip"], parts["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        parts["state"]="Exchange"
        conn2.send(frame) 
        return

    if parts["state"]=="Exchange" and parts["peer_options"]==2:
        print("     Exstart M set") #Not the last one
        ospf_sequence_number =ospf_packet1["own_sequence_number"]
        ospf_header_ = ospf_header(parts,3) #type 2 packet
        ospf_packet2 = ospf_lsreq(ospf_header_,parts)
        framesize = 20 + len(ospf_packet2)
        parts["dest_ip"]="192.168.0.3"  #parts["neighbor"] #ojo aqui con este cambio!
        dstmac = "00:0f:e2:dd:9e:2c"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( parts["source_ip"], parts["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        parts["state"]="Exchange"
        conn2.send(frame) 
        return

    


    return


def send_lsack(parts):
    print("In lsack")
    ip_proto = 89
    ospf_header_ = ospf_header(parts,5) #type 5 LSACk
    ospf_packet2 = ospf_lsack(ospf_header_,parts)
    framesize = 20 + len(ospf_packet2)
    parts["dest_ip"]="192.168.0.3"  #parts["neighbor"] #ojo aqui con este cambio!
    dstmac = "00:0f:e2:dd:9e:2c"
    srcmac = "7c:c2:c6:45:3d:1f"
    ip_header_=ip_header( parts["source_ip"], parts["dest_ip"], ip_proto, framesize )
    eth_type = b'\x08\x00'
    frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
    #print("Frame sent length:",len(frame)-14,"neig",)
    parts["state"]="Exstart"
    conn2.sendall(frame) 
    return


def send_hello(parts):
    print("In send hello.")
    ip_proto = 89
    if parts["state"]=="":
        print(" '' ")
        ospf_header_ = ospf_header(parts,1)
        ospf_packet2 = ospf_hello(ospf_header_,parts)   
        framesize = 20+ len(ospf_packet2) 			#IP header size is hard coded
        #print("Frame size ",framesize)
        #print("State:",parts["state"])
        parts["dest_ip"]=="224.0.0.5"
        dstmac = "01:00:5E:00:00:05"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( parts["source_ip"], parts["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        conn2.sendall(frame)
        return

    if parts["state"]=="Init":
        print("--> init")

        ospf_header_ = ospf_header(parts,1)
        ospf_packet2 = ospf_hello(ospf_header_,parts)   
        framesize = 20+ len(ospf_packet2) 			#IP header size is hard coded
        #print("Frame size ",framesize)
        #print("State:",parts["state"])
        parts["dest_ip"]=="224.0.0.5"
        dstmac = "01:00:5E:00:00:05"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( parts["source_ip"], parts["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        conn2.sendall(frame)
        return

    if parts["state"]=="12-way":
        print("--> 2-way")
        ospf_header_ = ospf_header(parts,1)
        ospf_packet2 = ospf_hello(ospf_header_,parts)   
        framesize = 20 + len(ospf_packet2) 			#IP header size is hard coded
        #print("Frame size ",framesize)
        #print("State:",parts["state"])
        framesize = 20 + len(ospf_packet2)
        parts["dest_ip"]=="224.0.0.5"
        dstmac = "01:00:5E:00:00:05"
        srcmac = "7c:c2:c6:45:3d:1f"
        ip_header_=ip_header( parts["source_ip"], parts["dest_ip"], ip_proto, framesize )
        eth_type = b'\x08\x00'
        frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet2
        #print("Frame sent length:",len(frame)-14,"neig",)
        conn2.sendall(frame)
        return



def decode(pkt):
    # New packet to decode
    try:
        ip_header = ip_header_decoded(pkt[0:20])
        header=parseOspfHdr(pkt[20:44])
        print("\nNew packet from:",id2str(ip_header["SRC"]),"length: ",int(header["LEN"]))
        
        
        if int(header["TYPE"])==1 and int(header["LEN"])==44:
            ospf_packet1["Router_ID"]=id2str(header["RID"])
            ospf_packet1["state"]="Init"
            ospf_packet1["neighbor"]=""
            #ospf_packet1["desinated_router"]=id2str(ip_header["SRC"])
            ospf_packet1["type"]=int(header["TYPE"])
            classify(ospf_packet1)
        if int(header["TYPE"])==1 and int(header["LEN"])>44:
            ospf_packet1["Router_ID"]=id2str(header["RID"])
            ospf_packet1["type"]=int(header["TYPE"])
            leng = int(header["LEN"])+20
            neig=struct.unpack("> L",(pkt[leng-4:leng]))
            ospf_packet1["neighbor"]= id2str(neig[0])
            #ospf_packet1["desinated_router"]=id2str(ip_header["SRC"])
            classify(ospf_packet1)
        if int(header["TYPE"])==2 and int(header["LEN"])==32: #DB without LSAs
            print("***** DB  ******")
            ospf_packet1["Router_ID"]=id2str(header["RID"])
            ospf_packet1["type"]=int(header["TYPE"])
            ospf_packet1["neighbor"]=""
            options=struct.unpack("> B",(pkt[47:48]))
            ospf_packet1["peer_options"]=int(options[0])
            psq=struct.unpack("> L",(pkt[48:52]))
            ospf_packet1["peer_sequence_number"]=int((psq[0]))
            classify(ospf_packet1)
        
        if int(header["TYPE"])==2 and int(header["LEN"])>32: #DB with LSAs
            print("*****LSA summary *******")
            ospf_packet1["Router_ID"]=id2str(header["RID"])
            ospf_packet1["type"]=int(header["TYPE"])
            ospf_packet1["neighbor"]=""
            options=struct.unpack("> B",(pkt[47:48]))
            ospf_packet1["peer_options"]=int(options[0])
            psq=struct.unpack("> L",(pkt[48:52]))
            ospf_packet1["peer_sequence_number"]=int((psq[0]))
            #for k in range(int(header["LEN"])-32):
            #    ospf_packet1["LSA_headers"].append(pkt[])
            decode_lsa_headers(ospf_packet1,pkt[52:],int(header["LEN"]))
            classify(ospf_packet1)

            
    except Exception as e: 
        traceback.print_exc()
        print("Errored packet")
    
def rid_exist(ospf_packet1):
    a=0
    print("RID exists? ")
    for parts in buffer:
        if parts["Router_ID"]==ospf_packet1["Router_ID"]:
            print(" Yes. State: ",parts["state"])
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
        print("Own RID in neighbor?")
        if ospf_packet1["neighbor"]==parts["own_router_id"]:
            print(" Yes")
            if parts["state"]=="":
                send_hello(parts)
                parts["state"]="Init"
                return 
            if parts["state"]=="Init":
                send_hello(parts)
                parts["state"]="2-way"
                return 
            if parts["state"]=="2-way":
                send_dd(parts)
                return 
        else:
            print(" No")
            parts["state"]="Init"
            send_hello(parts)
            return
    print("Is DBD?"," state= ",parts["state"])
    if ospf_packet1["type"]== 2:
        print(" Yes.")
        parts["peer_sequence_number"]=ospf_packet1["peer_sequence_number"]          
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
