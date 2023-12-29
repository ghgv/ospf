#!/usr/bin/env python3

# Usage: ethsend.py eth0 ff:ff:ff:ff:ff:ff 'Hello everybody!'
#        ethsend.py eth0 06:e5:f0:20:af:7a 'Hello 06:e5:f0:20:af:7a!'
#
#
import fcntl
import socket
import struct
import sys
from ipv4 import *
from ospf_ import *

def send_frame(ifname, dstmac, eth_type, payload):
    
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind((ifname, 0))

    # Get source interface's MAC address.
    info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
    
    srcmac = ':'.join('%02x' % b for b in info[18:24])

    # Build Ethernet frame
    payload_bytes = payload.encode('utf-8')
    assert len(payload_bytes) <= 1500  # Ethernet MTU

    source_ip = "192.168.0.1"
    mask="255.255.255.0"
    dest_ip   = "224.0.0.5"
    ip_proto  = 89
    
    
    ospf_header_ = ospf_header(source_ip)
    ospf_packet = ospf_hello(ospf_header_,mask)
    
    framesize = 20+ len(ospf_packet) 			#IP header size is hard coded
    print("Frame size ",framesize)
    
    ip_header_=ip_header( source_ip, dest_ip, ip_proto, framesize )
    frame = human_mac_to_bytes(dstmac) + human_mac_to_bytes(srcmac) + eth_type + ip_header_ + ospf_packet
    
    
    
    # Send Ethernet frame
    return s.send(frame)
    
 

def human_mac_to_bytes(addr):
    return bytes.fromhex(addr.replace(':', ''))

def main():
  ifname = sys.argv[1]
  dstmac = "01:00:5E:00:00:05" #sys.argv[2]
  payload = sys.argv[3]
  ethtype = b'\x08\x00'  # arbitrary, non-reserved
  send_frame(ifname, dstmac, ethtype, payload)

if __name__ == "__main__":
    main()
