import socket, sys, time
import array
import socket
import struct
from struct import *

def checksum(packet: bytes) -> int:
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff

def ip_header(source_ip,dest_ip, ip_proto,framesize)-> bytes:
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = framesize	# kernel will fill the correct total length
    ip_id = 0	#Id of this packet
    ip_frag_off = 0
    ip_ttl = 1   #For a packet in the lan port
    ip_proto = ip_proto
    ip_check = 0	# kernel will fill the correct checksum
    ip_saddr = socket.inet_aton ( source_ip )	#Spoof the source ip address if you want to
    ip_daddr = socket.inet_aton ( dest_ip )

    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    # the ! in the pack format string means network order
    ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
    ip_check   = checksum(ip_header)
           
    ip_header = ip_header[:10] + struct.pack('H', ip_check) + ip_header[12:]
    
    return ip_header
	
	

