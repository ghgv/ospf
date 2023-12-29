# some imports
import socket, sys, time
import array
import socket
import struct
from struct import *

# checksum functions needed for calculation checksum
def checksum2(msg):
	s = 0
	
	# loop taking 2 characters at a time
	for i in range(0, len(msg), 2):
		w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
		s = s + w
	
	s = (s>>16) + (s & 0xffff);
	s = s + (s >> 16);
	
	#complement and mask to 4 byte short
	s = ~s & 0xffff
	
	return s
    
def checksum(packet: bytes) -> int:
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff

# the main function
def main():
    HOST = socket.gethostbyname(socket.gethostname())
    print(HOST)
    
    try:
        OSPF_ = socket.IPPROTO_TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, 89)
        #s.bind((HOST, 20))
    except: # socket.error , msg:
        print ('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    # tell kernel not to put in headers, since we are providing it, when using IPPROTO_RAW this is not necessary
    # s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    #s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    #s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL,205)
    #s.ioctl(s.SIO_RCVALL, s.RCVALL_ON)
    #s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        
    # now start constructing the packet
    packet = '';

    source_ip = '192.168.0.1'
    dest_ip = '192.168.0.3'	# or socket.gethostbyname('www.google.com')
    
    ###############OSPF Packet header #############
    
    opsf_ver       = 2
    ospf_type      = 1
    ospf_lenght    = 24
    ospf_router_id = socket.inet_aton ( source_ip )
    ospf_area_id   = socket.inet_aton ( "0.0.0.0" )
    ospf_checksum  = 0
    ospf_AuType    = 0
    ospf_Authentication1 = socket.inet_aton ( "0.0.0.0" )
    ospf_Authentication2 = socket.inet_aton ( "0.0.0.0" )
    
    ospf_header = pack('!BBH4s4sHH4s4s' , opsf_ver, ospf_type, ospf_lenght, ospf_router_id, ospf_area_id, ospf_checksum, ospf_AuType, ospf_Authentication1,ospf_Authentication2)
    
    ################# OSPF Hello #######################
    
    ospf_network_mask             = socket.inet_aton ( "255.255.255.0" )
    ospf_hello_interval           = 30
    ospf_hello_options            = 0 
    ospf_router_prio              =  0
    ospf_router_dead_interval     = socket.inet_aton ( "0.0.0.34" ) #cambiar
    ospf_designated_router        = socket.inet_aton ( "0.0.0.0" )
    ospf_backup_designated_router = socket.inet_aton ( "0.0.0.0" )
    ospf_neighbor = []
    ospf_neighbor.append(socket.inet_aton ( "0.0.0.0" ))
    
    
    
    ospf_hello= pack('!4sHBB4s4s4s' , ospf_network_mask, ospf_hello_interval, ospf_hello_options, ospf_router_prio, ospf_router_dead_interval, ospf_designated_router, ospf_backup_designated_router)
    for i in range(1):
        ospf_hello = ospf_hello + socket.inet_aton ( "0.0.0.0" )
    
    ospf_frame = ospf_header + ospf_hello
    
    ospf_checksum = checksum(ospf_header)
    
    ospf_header = ospf_frame[:12]+ pack('H',ospf_checksum)+ ospf_frame[14:]
    
    ###################### IP header #########################
    
    # ip header fields
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 0	# kernel will fill the correct total length
    ip_id = 0	#Id of this packet
    ip_frag_off = 0
    ip_ttl = 250
    ip_proto = socket.IPPROTO_TCP
    ip_check = 0	# kernel will fill the correct checksum
    ip_saddr = socket.inet_aton ( source_ip )	#Spoof the source ip address if you want to
    ip_daddr = socket.inet_aton ( dest_ip )

    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    # the ! in the pack format string means network order
    ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
    
    result = ' '.join(hex((char)) for char in ip_header)
    print("ip header:" ,result)

    # tcp header fields
    tcp_source = 1234	# source port
    tcp_dest = 2	# destination port
    tcp_seq = 454
    tcp_ack_seq = 20
    tcp_doff = 5	#4 bit field, size of tcp header, 5 * 4 = 20 bytes
    #tcp flags
    tcp_fin = 0
    tcp_syn = 1
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 0
    tcp_urg = 0
    tcp_window = socket.htons (5840)	#	maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
    print("TCP Flags:", tcp_flags)

    # the ! in the pack format string means network order
    
    tcp_header = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
    
    result = ' '.join(hex((char)) for char in tcp_header)
    print("TCP header: ",result)
    
    user_data = 'Hello, how are you..'

    # pseudo header fields
    source_address = socket.inet_aton( source_ip )
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(user_data)

    psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
    
    print(type(psh))
    
    psh = psh +tcp_header + bytes(user_data, "utf-8" )
    result = ' '.join(hex((char)) for char in psh)
    
    print("psh ",result)
    
    tcp_check  = checksum(psh)
    
    ip_tot_len = len(ip_header)+len(tcp_header)+len(user_data)
    print("Tot len:",ip_tot_len)
    ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
    
    ip_check   = checksum(ip_header)
           
    ip_header = ip_header[:10] + struct.pack('H', ip_check) + ip_header[12:]
    
    
    print("IP hdr checksumk: ",result)
    
    
    
    #ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
    
    #print tcp_checksum

    # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
    tcp_header = pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('H' , tcp_check) + pack('!H' , tcp_urg_ptr)

    # final full packet - syn packets dont have any data
    #packet = ip_header + tcp_header + bytes(user_data, "utf-8" )
    packet = ip_header + tcp_header + bytes(user_data, "utf-8" )
    packet = ospf_header 
    
    result = ' '.join(hex((char)) for char in packet)
    print("Packet: ",result)
    
    # increase count to send more packets
    count = 3
    
    for i in range(count):
        print ('sending packet...')
        # Send the packet finally - the port specified has no effect
        #s.bind(("ethenet" , ))
        m_cast ="224.0.0.5"
        s.sendto(packet, (m_cast , 0 ))	# put this in a loop if you want to flood the target 
        #s.send(packet)	# put this in a loop if you want to flood the target 
        print ('send')
        time.sleep(1)
        
    print ('all packets send');

main()
