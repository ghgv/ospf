#!/usr/bin/env python3

# Usage: ethsend.py eth0 ff:ff:ff:ff:ff:ff 'Hello everybody!'
#        ethsend.py eth0 06:e5:f0:20:af:7a 'Hello 06:e5:f0:20:af:7a!'
#
#
import fcntl
import socket
import struct
import sys
import os
from ipv4 import *
from ospf import *
import threading, time, signal
from datetime import timedelta
import select



ETHSEND_CLASSIFIER = "/tmp/ethsend-classifier.socket"



#####################################

WAIT_TIME_SECONDS = 3

class ProgramKilled(Exception):
    pass

def foo():
    print(time.ctime())
    
def signal_handler(signum, frame):
    raise ProgramKilled
    
class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs
        
    def stop(self):
                self.stopped.set()
                self.join()
    def run(self):
            while not self.stopped.wait(self.interval.total_seconds()):
                self.execute(*self.args, **self.kwargs)



################################################


def human_mac_to_bytes(addr):
    return bytes.fromhex(addr.replace(':', ''))


##########################

class SEND_FRAME:

    _version   = 2
    _holdtimer = 30.0

    def __init__(self,ifname, dstmac, eth_type):

        ######### Interface part ##########

        self.sender = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        self.sender.bind((ifname, 0))
        
        # Get source interface's MAC address.
        info = fcntl.ioctl(self.sender.fileno(), 0x8927, struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
        self.srcmac    = ':'.join('%02x' % b for b in info[18:24])
        self.dstmac    = dstmac
        self.eth_type  = eth_type

        ########## IPC part ###############
        
    
        # Init socket object
        if not os.path.exists(ETHSEND_CLASSIFIER):
            print("File ",ETHSEND_CLASSIFIER,"doesn't exists")
            sys.exit(-1)
        
        self.from_classifier = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.from_classifier.settimeout(30.0)
        self.from_classifier.connect(ETHSEND_CLASSIFIER)


    def send_default(self,payload):
    
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
        frame = human_mac_to_bytes(self.dstmac) + human_mac_to_bytes(self.srcmac) + self.eth_type + ip_header_ + ospf_packet
        
        
        
        self.sender.send(frame)
        return 

    


    def foo(self):
        print(time.ctime())
    
 



def main():

    
    ifname = sys.argv[1]
    dstmac = "01:00:5E:00:00:05" #sys.argv[2]
    payload = sys.argv[3]
    eth_type = b'\x08\x00'  # arbitrary, non-reserved
    send_frame  =   SEND_FRAME(ifname, dstmac, eth_type)
    

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=send_frame.foo)
    job.start()


    try:

        timeout     =   SEND_FRAME._holdtimer 
        

        rv = None
        while 1:
            before = time.time()
            rfds, _, _ = select.select([send_frame.from_classifier], [], [], timeout)
            after = time.time()
            elapsed = after - before

            if len(rfds) > 0: 
                for sock in rfds:
                    #incoming message from remote server
                    if sock == send_frame.from_classifier:
                        data = sock.recv(2048)
                        send_frame.sender.send(data)

            else:
                ## tx some pkts to form adjacency
                print("Time out1")
                #send_frame.send_default("hola")
                pass

    except ProgramKilled:
        print ("Program killed: running cleanup code")
        job.stop()



    except (KeyboardInterrupt):
        ospf.close()
        job.stop()
        sys.exit(1)



if __name__ == "__main__":
    main()
