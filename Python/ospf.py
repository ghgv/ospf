import socket, sys, time
import array
import copy
import socket
import struct
from struct import *
from tcb import *
from mutils import *




def checksum(packet: bytes) -> int:
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff

def ospf_header(ospf_packet1,type_=1)->bytes:
    opsf_ver       = 2
    ospf_type      = type_
    ospf_lenght    = 24
    ospf_router_id = socket.inet_aton ( ospf_packet1["own_router_id"]) #make sure is the highest ID
    ospf_area_id   = socket.inet_aton ( ospf_packet1["area_id"] )
    ospf_checksum  = 0
    ospf_AuType    = 0
    ospf_Authentication1 = socket.inet_aton ( "0.0.0.0" )
    ospf_Authentication2 = socket.inet_aton ( "0.0.0.0" )
    
    ospf_header = pack('!BBH4s4sHH4s4s' , opsf_ver, ospf_type, ospf_lenght, ospf_router_id, ospf_area_id, ospf_checksum, ospf_AuType, ospf_Authentication1,ospf_Authentication2)	
    return ospf_header


def ospf_header_json(source_ip)->bytes:
    opsf_ver       = 2
    ospf_type      = 1
    ospf_lenght    = 24
    ospf_router_id = socket.inet_aton ( source_ip)
    ospf_area_id   = socket.inet_aton ( "0.0.0.0" )
    ospf_checksum  = 0
    ospf_AuType    = 0
    ospf_Authentication1 = socket.inet_aton ( "0.0.0.0" )
    ospf_Authentication2 = socket.inet_aton ( "0.0.0.0" )
    
    ospf_header = pack('!BBH4s4sHH4s4s' , opsf_ver, ospf_type, ospf_lenght, ospf_router_id, ospf_area_id, ospf_checksum, ospf_AuType, ospf_Authentication1,ospf_Authentication2)	

    return ospf_header

def ospf_hello(ospf_header,ospf_packet1)->bytes:

    ospf_network_mask             = socket.inet_aton ( ospf_packet1["mask"] )
    ospf_hello_interval           = 10
    ospf_hello_options            = 2 
    ospf_router_prio              = 1
    ospf_router_dead_interval     = socket.inet_aton ( "0.0.0.40" ) #cambiar
    ospf_designated_router        = socket.inet_aton ( "192.168.0.1") #ospf_packet1["desinated_router"] )
    ospf_backup_designated_router = socket.inet_aton ( "0.0.0.0" )
    ospf_neighbor = []
    ospf_neighbor.append(socket.inet_aton ( "0.0.0.0" ))
   
    ospf_hello= pack('!4sHBB4s4s4s' , ospf_network_mask, ospf_hello_interval, ospf_hello_options, ospf_router_prio, ospf_router_dead_interval, ospf_designated_router, ospf_backup_designated_router)
    
    
    #if ospf_packet1["neighbor"]!="":
    ospf_hello = ospf_hello + socket.inet_aton (ospf_packet1["Router_ID"])
    
    ospf_frame = ospf_header + ospf_hello
    packet_lenght = len(ospf_frame)
    #print("ospf_lenght: ", packet_lenght)
    ospf_frame = ospf_frame[:2]+ pack('!H',packet_lenght)+ ospf_frame[4:]
    ospf_checksum = checksum(ospf_frame)
    
    ospf_header = ospf_frame[:12]+ pack('H',ospf_checksum)+ ospf_frame[14:]
    
    
    return ospf_header

def ospf_dd(ospf_header,ospf_packet1)-> bytes:
    ospf_interface_MTU = 1500
    ospf_options = 2
    ospf_flags   = 7 & ospf_packet1["master"]
    ospf_lsa_header =[]
    ospf_sequence_number =ospf_packet1["peer_sequence_number"]
    ospf_dd = pack('!HBBL' , ospf_interface_MTU, ospf_options, ospf_flags, ospf_sequence_number)
    #ospf_dd = ospf_dd + socket.inet_aton (ospf_packet1["Router_ID"])
    
    ospf_frame = ospf_header + ospf_dd
    packet_lenght = len(ospf_frame)
    ospf_frame = ospf_frame[:2]+ pack('!H',packet_lenght)+ ospf_frame[4:]
    ospf_checksum = checksum(ospf_frame)
    ospf_frame2 = ospf_frame[:12]+ pack('H',ospf_checksum)+ ospf_frame[14:]
    return ospf_frame2

def ospf_lsack(ospf_header,ospf_packet1)-> bytes:
    ospf_lsa_header =[]
    
    #ospf_lsack = pack('!HBBL' , ospf_interface_MTU, ospf_options, ospf_flags, ospf_sequence_number)
    #ospf_dd = ospf_dd + socket.inet_aton (ospf_packet1["Router_ID"])
    
    ospf_frame = ospf_header 
    packet_lenght = len(ospf_frame)
    ospf_frame = ospf_frame[:2]+ pack('!H',packet_lenght)+ ospf_frame[4:]
    ospf_checksum = checksum(ospf_frame)
    ospf_frame2 = ospf_frame[:12]+ pack('H',ospf_checksum)+ ospf_frame[14:]
    return ospf_frame2

def ospf_lsreq(ospf_header,ospf_packet1)-> bytes:
    for i in ospf_packet1["LSA_headers"]:
        print("headers: ",i)
        LS_type         = i["LS_type"]
        Link_state_id   = i["Link_state_id"]
        Adv_router      = i["Adv_router"]
        print(LS_type,socket.inet_aton(Link_state_id),socket.inet_aton(Adv_router))
        ospf_lsreq = pack('! L4s4s' , LS_type, socket.inet_aton(Link_state_id),socket.inet_aton(Adv_router)) 
    #ospf_dd = ospf_dd + socket.inet_aton (ospf_packet1["Router_ID"])
    
    ospf_frame = ospf_header + ospf_lsreq
    packet_lenght = len(ospf_frame)
    ospf_frame = ospf_frame[:2]+ pack('!H',packet_lenght)+ ospf_frame[4:]
    ospf_checksum = checksum(ospf_frame)
    ospf_frame2 = ospf_frame[:12]+ pack('H',ospf_checksum)+ ospf_frame[14:]
    return ospf_frame2


def decode_lsa_headers(ospf_packet1,lsa_pkt,len):
    
    OSPF_LSAHDR     = "! HBB L L L HH"
    OSPF_LSAHDR_LEN = struct.calcsize(OSPF_LSAHDR)
    lsa_header={"LS_age":0,
                 "LS_type": 0,
                 "Link_state_id": "0.0.0.0",
                 "Adv_router": "0.0.0.0",
                 "LS_sequence": 0,
                 "Length":0, 
                }
    
    i=0
    while  (i < (int(len))-32):     
        (LS_age, Options, LS_type, Link_state_id, Advertising_router, LS_sequence_number, LS_checksum, Length) = struct.unpack(OSPF_LSAHDR, lsa_pkt[i:i+5*4])
        print("LS age: ",LS_age)
        print("LS type: ",LS_type)
        print("Link state ID: ",id2str(Link_state_id))
        print("Adv router: ",id2str(Advertising_router))
        print("LS sequence: 0x",int2hex(LS_sequence_number))
        print("LS checksum: 0x",int2hex(LS_checksum))
        Length1=copy.copy(swap_bytes(Length))
        print("Length: ",Length,"\n\n")
        i=i+20
        lsa_header["LS_age"]=           LS_age
        lsa_header["LS_type"]=          LS_type
        lsa_header["Link_state_id"]=    id2str(Link_state_id)
        lsa_header["Adv_router"]=       id2str(Advertising_router)
        lsa_header["LS_sequence"]=      int2hex(LS_sequence_number)
        lsa_header["Length"]=           Length1

    ospf_packet1["LSA_headers"].append(copy.copy(lsa_header))
        
    return     
    



