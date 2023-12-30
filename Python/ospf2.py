#!/usr/bin/env python
# coding: utf-8

# In[20]:


import getopt
import os,sys
import time
import select
import struct, socket, sys, math, getopt, string, os.path, time, select, traceback
from mutils import *
import threading, time, signal
from datetime import timedelta


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

INDENT          = "    "
VERSION         = "2.9"

RECV_BUF_SZ      = 8192
OSPF_LISTEN_PORT = 89



IP_HDR     = "> BBH HH BBH LL"
IP_HDR_LEN = struct.calcsize(IP_HDR)

OSPF_HDR     = "> BBH L L HH L L"
OSPF_HDR_LEN = struct.calcsize(OSPF_HDR)

OSPF_HELLO     = "> L HBB L L L"
OSPF_HELLO_LEN = struct.calcsize(OSPF_HELLO)

########################

DLIST = []

ADDRS = { str2id("224.0.0.5"): "AllSPFRouters",
          str2id("224.0.0.6"): "AllDRouters",
          }
DLIST += [ADDRS]

AFI_TYPES = { 1: "IP",
              2: "IP6",
              }
DLIST += [AFI_TYPES]

MSG_TYPES = { 1: "HELLO",
              2: "DBDESC",
              3: "LSREQ",
              4: "LSUPD",
              5: "LSACK",
              }
              
AU_TYPES = { 0: "NULL",
             1: "PASSWD",
             2: "CRYPTO",
             }

DLIST += [AU_TYPES]

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
    
def parseOspfHdr(msg, verbose=1, level=0):
    print("In parse OSPF Header")
    if verbose > 1: 
        print(msg[:OSPF_HDR_LEN])
    (ver, typ, leng, rid, aid, cksum, autype, auth1, auth2) = struct.unpack(OSPF_HDR, msg)
    if verbose > 0:
        print("OSPF: ver:%s, type:%s, len:%s, rtr id:%s, area id:%s, cksum:%x, autype:%s" % (ver, MSG_TYPES[typ], len, id2str(rid), id2str(aid), cksum, AU_TYPES[autype],))
    #print("OSPF: ver:%s, type:%s, len:%s, rtr id:%s, area id:%s, cksum:%x, autype:%s" % (ver, MSG_TYPES[typ], leng, id2str(rid), id2str(aid), cksum, AU_TYPES[autype],))
    return { "VER"    : ver,
             "TYPE"   : typ,
             "LEN"    : leng,
             "RID"    : rid,
             "AID"    : aid,
             "CKSUM"  : cksum,
             "AUTYPE" : autype,
             "AUTH1"  : auth1,
             "AUTH2"  : auth2,
             }
def parseOspfOpts(opts, verbose=1, level=0):

    if verbose > 1: 
        print (int2bin(opts))

    qbit  = (opts & 0x01)           ## RFC 2676; reclaim original "T"-bit for TOS routing cap.
    ebit  = (opts & 0x02) >> 1
    mcbit = (opts & 0x04) >> 2
    npbit = (opts & 0x08) >> 3
    eabit = (opts & 0x10) >> 4
    dcbit = (opts & 0x20) >> 5
    obit  = (opts & 0x40) >> 6

    if verbose > 0:
        print("options: %s %s %s %s %s %s %s" %( qbit*"Q", ebit*"E", mcbit*"MC", npbit*"NP", eabit*"EA", dcbit*"DC", obit*"O"))

    return { "Q"  : qbit,
             "E"  : ebit,
             "MC" : mcbit,
             "NP" : npbit,
             "EA" : eabit,
             "DC" : dcbit,
             "O"  : obit,
             }

def parseOspfHello(msg, verbose=1, level=0):
    
    if verbose > 1: 
        print ( msg)
    (netmask, hello, opts, prio, dead, desig, bdesig) = struct.unpack(OSPF_HELLO, msg[:OSPF_HELLO_LEN])
    
    if verbose > 0:
        print ("HELLO: netmask:%s, hello intvl:%s, opts:%s, prio:%s, dead intvl:%s" % (id2str(netmask), hello, opts, prio, dead))
        print ("designated rtr:%s, backup designated rtr:%s" % (id2str(desig), id2str(bdesig)))

    msg = msg[OSPF_HELLO_LEN:]
    nbor_len = struct.calcsize(">L") 
    nbors = []
    while len(msg) > 0:
        if verbose > 1: 
            print (msg[:nbor_len])
        (nbor,) = struct.unpack(">L", msg[:nbor_len])
        if verbose > 0:
            print ("neighbour: %s" % (id2str(nbor),))
        nbors.append(nbor)
        msg = msg[nbor_len:]

    
    return { "NETMASK" : netmask,
             "HELLO"   : hello,
             "OPTS"    : parseOspfOpts(opts, verbose, level),
             "PRIO"    : prio,
             "DEAD"    : dead,
             "DESIG"   : desig,
             "BDESIG"  : bdesig,
             "NBORS"   : nbors
             }

          
             
def parseOspfMsg(msg, verbose=1, level=0):
    #print("In OSPF Mesg")
    iph   = parseIpHdr(msg[:IP_HDR_LEN], verbose, level)
    msg   = msg[IP_HDR_LEN:]
    ospfh = parseOspfHdr(msg[:OSPF_HDR_LEN], verbose, level+1)
    rv = { "T": ospfh["TYPE"],
           "L": len(msg),
           "H": iph,
           "V": ospfh,
           }

    if MSG_TYPES[ospfh["TYPE"]] == "HELLO":
        print("In Hello")
        rv["V"] = parseOspfHello(msg[OSPF_HDR_LEN:], verbose, level+2)
        return rv

    elif MSG_TYPES[ospfh["TYPE"]] == "DBDESC":
        rv["V"]["V"] = parseOspfDesc(msg[OSPF_HDR_LEN:], verbose, level+2)

    elif MSG_TYPES[ospfh["TYPE"]] == "LSREQ":
        rv["V"]["V"] = parseOspfLsReq(msg[OSPF_HDR_LEN:], verbose, level+1)

    elif MSG_TYPES[ospfh["TYPE"]] == "LSUPD":
        rv["V"]["V"] = parseOspfLsUpd(msg[OSPF_HDR_LEN:], verbose, level+2)

    elif MSG_TYPES[ospfh["TYPE"]] == "LSACK":
        rv["V"]["V"] = parseOspfLsAck(msg[OSPF_HDR_LEN:], verbose, level+2)
    print("returning")
    return rv
############################################################

class OspfExc(Exception): 
    pass

class Ospf:

    _version   = 2
    _holdtimer = 30

    #---------------------------------------------------------------------------

    class Adj:

        def __init__(self):
            pass
        def __repr__(self):
            pass
        

    #---------------------------------------------------------------------------

    def __init__(self):

                #if linux
        #self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_RAW, socket.IPPROTO_IP)
        #if windows
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        #socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self._sock =  socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        #self._sock = socket(socket.AF_INET, socket.SOCK_RAW, socket.ETH_P_ALL)

        self._addr = (ADDRESS,0)
        self._sock.bind(self._addr)
        self._name = self._sock.getsockname()
        
        #self._sock.setsockopt(socket.IPPROTO_IP, socket.SO_REUSEADDR,socket.IP_HDRINCL, 1)
        #self._sock.ioctl(socket.SIO_RCVALL, 1)
        self._sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)
        self._adjs = {}
        self._rcvd = ""
        self._mrtd = None

    def __repr__(self):

        rs = """OSPF listener, version %s:
	%s
	socket:  %s
	address: %s, name: %s""" %\
	(self._version, self._mrtd, self._sock, self._addr, self._name)

        return rs


    def close(self):
        self._sock.close()
        self._mrtd.close()
        
    def foo(self):
        print(time.ctime())
        

    #---------------------------------------------------------------------------

    def parseMsg(self, verbose=1, level=0):

        try:
            (msg_len, msg) = self.recvMsg(verbose, level)
            
        except:
            Exception()
            OspfExc()
            if verbose > 1:
                print("[ *** Non OSPF packet received *** ]")
                return
            
        iph = parseIpHdr(msg[:IP_HDR_LEN], 0)
        if iph["PROTO"] == OSPF_LISTEN_PORT:
            print("In OSPF")
            parseIpHdr(msg[:IP_HDR_LEN], 0)
            ospfh = parseOspfHdr(msg[IP_HDR_LEN:IP_HDR_LEN+OSPF_HDR_LEN], 0)
            if DUMP_MRTD == 1:
                self._mrtd.writeOspfMsg(ospfh["TYPE"], msg_len, msg)
            if verbose > 2:
                print("parseMsg: len=%d%s" % (msg_len, print( msg)))
            try:
               rv = parseOspfMsg(msg, verbose, level)
               print(rv)
            except:
                Exception()
                stk = traceback.extract_stack(limit=1)
                tb = stk[0]
                error("[ *** exception parsing OSPF packet ***]\n")
                #error("### File: %s, Line: %s, Exc: %s " % (tb[0], tb[1], exc ))
            return rv

    def recvMsg(self, verbose=1, level=0):
        self._rcvd = self._sock.recv(RECV_BUF_SZ)
        
        if verbose > 1:
            pass
            #print("->",prthex((level+1)*INDENT, self._rcvd))
            #print("%srecvMsg: recv: len=%d %s" % (level*INDENT,len(self._rcvd),prthex2((level+1)*INDENT, self._rcvd)))
            #print("%srecvMsg: recv: len=%d%s" % (level*INDENT,len(self._rcvd),prthex((level+1)*INDENT, self._rcvd)))
        return (len(self._rcvd), self._rcvd)


    def sendMsg(self, verbose=1, level=0):
        pass



if __name__ == "__main__":


    global VERBOSE, DUMP_MRTD, ADDRESS

    VERBOSE   = 1
    DUMP_MRTD = 0
    ADDRESS   = None
    
    DEFAULT_FILE = "mrtd.mrtd"
    DEFAULT_SIZE = 50*1024*1024
    MIN_FILE_SZ  = 50*1024

    file_pfx  = DEFAULT_FILE
    file_sz   = DEFAULT_SIZE
    mrtd_type = None

    #---------------------------------------------------------------------------

    def usage():

        print("""Usage: %s [ options ] ([*] options required):
        -h|--help     : Help
        -q|--quiet    : Be quiet
        -v|--verbose  : Be verbose
        -V|--VERBOSE  : Be very verbose

        -d|--dump     : Dump protocol MRTD file
        -f|--file     : Set file prefix for MRTd dump [def: %s]
        -z|--size     : Size of output file(s) [min: %d]
        -b|--bind <ipaddr> : local IP address for bind """ %  (os.path.basename(sys.argv[0]),
             DEFAULT_FILE,
             MIN_FILE_SZ))
        sys.exit(0)

    #---------------------------------------------------------------------------

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hqvVdfb:z:",
                                   ("help", "quiet", "verbose", "VERBOSE",
                                    "dump", "file=", "size=","bind" ))
    except (getopt.error):
        usage()

    for (x, y) in opts:
        if x in ('-h', '--help'):
            usage()

        elif x in ('-q', '--quiet'):
            VERBOSE = 0

        elif x in ('-v', '--verbose'):
            VERBOSE = 2

        elif x in ('-V', '--VERBOSE'):
            VERBOSE = 3

        elif x in ('-d', '--dump'):
            DUMP_MRTD = 1
            mrtd_type = mrtd.MSG_TYPES["PROTOCOL_OSPF2"]

        elif x in ('-f', '--file-pfx'):
            file_pfx = y

        elif x in ('-z', '--file-size'):
            file_sz = max(string.atof(y), mrtd.MIN_FILE_SZ)

        elif x in ('-b', '--bind'):
            ADDRESS = y

        else:
            usage()

    if (ADDRESS==None):
    	print(ADDRESS)
    	usage()

    #---------------------------------------------------------------------------

    ospf       = Ospf()
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=ospf.foo)
    job.start()
    

    if VERBOSE > 0: 
        print(ospf)

    try:
        timeout = Ospf._holdtimer

        rv = None
        while 1:
            before = time.time()
            rfds, _, _ = select.select([ospf._sock], [], [], timeout)
            after = time.time()
            elapsed = after - before

            if len(rfds) > 0: 
                rv = ospf.parseMsg(VERBOSE, 0)
            else:
                ## tx some pkts to form adjacency
                pass

    except ProgramKilled:
        print ("Program killed: running cleanup code")
        job.stop()
        
    except (KeyboardInterrupt):
        ospf.close()
        job.stop()
        sys.exit(1)
        





