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
import threading, time, signal
from datetime import timedelta


ETH_HEADER = "! 6s 6s H"
ETH_HEADER_LEN = struct.calcsize(ETH_HEADER)

def ether_header(msg)->bytes:
    print("in ether Header")
    (dest_mac, source_mac, ether_type ) = struct.unpack(ETH_HEADER, msg[0][0:14])
    #print(msg[:ETH_HEADER_LEN], dest_mac, source_mac,ether_type)
        
    #print("version: %s, hlen: %s, ipid: %s, proto: %s, source: %s, destination: %s"% (ver, hlen, ipid, proto,id2str(src),id2str(dst)))
    return { "DEST"  : dest_mac,
             "SOURCE" : source_mac,
             "TYPE"  : ether_type
            }