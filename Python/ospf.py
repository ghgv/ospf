import socket, sys, time
import array
import socket
import struct
from struct import *
from tcb import *


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
    ospf_router_id = socket.inet_aton ( ospf_packet1["source_ip"]) 
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
    ospf_router_prio              =  1
    ospf_router_dead_interval     = socket.inet_aton ( "0.0.0.40" ) #cambiar
    ospf_designated_router        = socket.inet_aton ( "0.0.0.0" )
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
    ospf_options = 0
    ospf_flags   = 0
    ospf_lsa_header =[]
    ospf_sequence_number =ospf_packet1["sequence_number"]
    ospf_dd = pack('!HBBL' , ospf_interface_MTU, ospf_options, ospf_flags, ospf_sequence_number)
    #ospf_dd = ospf_dd + socket.inet_aton (ospf_packet1["Router_ID"])
    
    ospf_frame = ospf_header + ospf_dd
    packet_lenght = len(ospf_frame)
    ospf_frame = ospf_frame[:2]+ pack('!H',packet_lenght)+ ospf_frame[4:]
    ospf_checksum = checksum(ospf_frame)
    ospf_header = ospf_frame[:12]+ pack('H',ospf_checksum)+ ospf_frame[14:]
    return ospf_header


