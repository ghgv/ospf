#!/usr/bin/env python
# coding: utf-8

# In[20]:


import getopt
import os,sys


# In[21]:


class OspfExc(Exception): 
    pass

class Ospf:

	_version   = 2
	_holdtimer = 30

    #---------------------------------------------------------------------------

	class Adj:

    		def __init__(self): pass
    		def __repr__(self): pass

    #---------------------------------------------------------------------------

	def __init__(self):

		## XXX raw sockets are broken in Windows Python (some madness
		## about linking against winsock1, etc); applied "patch" from
		## https://sourceforge.net/tracker/?func=detail&atid=355470&aid=889544&group_id=5470,
		## http://www.rs.fromadia.com/newsread.php?newsid=254,
		## http://www.rs.fromadia.com/files/pyraw.exe to fix this

		self._sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)

		self._addr = (ADDRESS, 0)
		self._sock.bind(self._addr)
		self._name = self._sock.getsockname()

		self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
		self._sock.ioctl(socket.SIO_RCVALL, 1)

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

    #---------------------------------------------------------------------------

	def parseMsg(self, verbose=1, level=0):

        	try:
			(msg_len, msg) = self.recvMsg(verbose, level)

	        except: 
			OspfExc()
			if verbose > 1: 
        			print("[ *** Non OSPF packet received *** ]")
	return

        iph = parseIpHdr(msg[:IP_HDR_LEN], 0)
        if iph["PROTO"] == OSPF_LISTEN_PORT:
            parseIpHdr(msg[:IP_HDR_LEN], 0)
            ospfh = parseOspfHdr(msg[IP_HDR_LEN:IP_HDR_LEN+OSPF_HDR_LEN], 0)
            if DUMP_MRTD == 1: self._mrtd.writeOspfMsg(ospfh["TYPE"], msg_len, msg)

            if verbose > 2:
                print("%sparseMsg: len=%d%s" %                      (level*INDENT, msg_len, prthex((level+1)*INDENT, msg)))

            try:
                rv = parseOspfMsg(msg, verbose, level)
            except:
                Exception()
                stk = traceback.extract_stack(limit=1)
                tb = stk[0]
                error("[ *** exception parsing OSPF packet ***]\n")
                error("### File: %s, Line: %s, Exc: %s " % (tb[0], tb[1], exc ))

            return rv

    def recvMsg(self, verbose=1, level=0):

        self._rcvd = self._sock.recv(RECV_BUF_SZ)

        if verbose > 2:
            print ("%srecvMsg: recv: len=%d%s" %                  (level*INDENT,
                   len(self._rcvd), prthex((level+1)*INDENT, self._rcvd)))

        return (len(self._rcvd), self._rcvd)


    def sendMsg(self, verbose=1, level=0):

        pass

    #---------------------------------------------------------------------------


# In[24]:


if __name__ == "__main__":

    #import mrtd

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
                                   "hqvVdf:z:",
                                   ("help", "quiet", "verbose", "VERBOSE",
                                    "dump", "file=", "size=", ))
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

    if not ADDRESS: usage()

    #---------------------------------------------------------------------------

    ospf       = Ospf()
    #ospf._mrtd = mrtd.Mrtd(file_pfx, "w+b", file_sz, mrtd.MSG_TYPES["PROTOCOL_OSPF2"], ospf)

    if VERBOSE > 0: print("ospf")

    try:
        timeout = Ospf._holdtimer

        rv = None
        while 1:
            before = time.time()
            rfds, _, _ = select.select([ospf._sock], [], [], timeout)
            after = time.time()
            elapsed = after - before

            if len(rfds) > 0: rv = ospf.parseMsg(VERBOSE, 0)
            else:
                ## tx some pkts to form adjacency
                pass

    except (KeyboardInterrupt):
        ospf.close()
        sys.exit(1)

################################################################################
################################################################################


# In[ ]:





# In[ ]:




