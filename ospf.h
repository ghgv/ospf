#ifndef OSPF_H
#define OSPF_H


#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netinet/ip.h>
#include <netpacket/packet.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <getopt.h>
#include <string.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <malloc.h>
#include <net/ethernet.h>
#include <sys/ioctl.h>
#include <net/if.h>

#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <iostream>
#include <chrono>
#include <thread>

typedef struct  OSPFHEADER
	{
		unsigned char version;
		unsigned char type;
		unsigned short packetlenght;
		unsigned int router_id;
		unsigned int area_id;
		unsigned short checksum;
		unsigned short Autype;
		unsigned long auth1;	
	}  __attribute__((packed)) ospfheader;


typedef struct  OSPFHELLO
	{
		unsigned int network_mask;
		unsigned short HelloInterval;
		unsigned char Options;
		unsigned char Priority;
		unsigned int RouterDeadInterval;
		unsigned int DesignatedRouter;
		unsigned int BackupDesignatedRouter;
		//unsigned int Neighbor;
	}  __attribute__((packed)) ospfhello;

extern unsigned char *buffer;

		
class ospf_f{
	
	public:

		ospfheader header;
		ospfhello hellof;
		void checksum(ospfheader , ospfhello );
		static int ReceiverOSPF2();
		void hello();
		int *encode();
		ospf_f();
};

#endif
