import os
import socket
import sys
import getopt
import os,sys
import time
import select
import fcntl
import struct
import sys
import struct, socket, sys, math, getopt, string, os.path, time, select, traceback
from mutils import *
import threading, time, signal
from datetime import timedelta
from ethernet import *
from ipv4 import *
 


IP_HDR     = "> BBH HH BBH LL"
IP_HDR_LEN = struct.calcsize(IP_HDR)


#################### Parse IP Header #################

IP_HDR     = "> BBH HH BBH LL"
IP_HDR_LEN = struct.calcsize(IP_HDR)

def parseIpHdr(msg, verbose =1 , level=0):
    #print("in IP Header")
    (verhlen, tos, iplen, ipid, frag, ttl, proto, cksum, src, dst) = struct.unpack(IP_HDR, msg)
    if (verbose>1):
        print(msg[:IP_HDR_LEN], verhlen, tos, iplen, ipid, frag, ttl, proto, cksum, src, dst)
    
    
    ver  = (verhlen & 0xf0) >> 4
    hlen = (verhlen & 0x0f) * 4
    #print("in IP Header2:",verbose)
    if (verbose>0):
        #print("IP (len=%d)" % len(msg))
        #print("ver:%s, hlen:%s, tos:%s, len:%s, id:%s, frag:%s, ttl:%s, prot:%s, cksm:%x" % (ver, hlen, int2bin(tos), iplen, ipid, frag, ttl, proto, cksum))
        print ("src:%s, dst:%s" % (id2str(src), id2str(dst)))
    
    #print("version: %s, hlen: %s, ipid: %s, proto: %s, source: %s, destination: %s"% (ver, hlen, ipid, proto,id2str(src),id2str(dst)))
    return { "VER"  : ver,
             "HLEN" : hlen,
             "TOS"  : tos,
             "IPLEN": iplen,
             "IPID" : ipid,
             "FRAG" : frag,
             "TTL"  : ttl,
             "PROTO": proto,
             "CKSUM": cksum,
             "SRC"  : src,
             "DST"  : dst} 
##############################################################

###################### packet socket ########################
class OSPF:

    _version   = 2
    _holdtimer = 30

    def __init__(self,ifname, dstmac, eth_type):

        print("listening on: ",ifname)
        self._sock =  socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
        self._sock.bind((ifname, 0))
        
        
        # Get source interface's MAC address.
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
        srcmac = ':'.join('%02x' % b for b in info[18:24])
    
    def close(self):
        self._sock.close()


if __name__ == "__main__":
    print("Init")
    # IPC parameters
    SOCK_FILE = '/tmp/simple-ipc.socket'
 
    # Init socket object
    if not os.path.exists(SOCK_FILE):
        print(f"File {SOCK_FILE} doesn't exists")
        sys.exit(-1)
    
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(SOCK_FILE)
    

    s.sendall(b'Hello, world')
    
    data = s.recv(1024)
    print(f'Received bytes: {repr(data)}')

    ifname = "enx7cc2c6453d1f"
    dstmac = "01:00:5E:00:00:05"
    ethtype = b'\x08\x00'

    ospf =OSPF(ifname,dstmac,ethtype)

    try:
        timeout = OSPF._holdtimer

        rv = None
        while 1:
            before = time.time()
            #rfds, _, _ = select.select([ospf._sock], [], [], timeout)
            pkt = ospf._sock.recvfrom(1500)
            after = time.time()
            elapsed = after - before

            if len(pkt) > 0: 
                
                #head =ether_header(pkt)
                #print("ethernet:" ,(head["DEST"]))
                print("len: ", len(pkt[0]))
                head =ip_header_decoded(pkt[0][14:34])
                print("Protocol:" ,(head["PROTO"]))
                s.sendall(pkt[0][14:])
            else:
                ## tx some pkts to form adjacency
                pass


        
    except (KeyboardInterrupt):
        ospf.close()
        sys.exit(1)

