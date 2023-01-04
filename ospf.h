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
		unsigned int Neighbor;
	}  __attribute__((packed)) ospfhello;
	
typedef struct  OSPFDD
	{
		unsigned short mtu;
		unsigned char options;
		unsigned char dd;
		unsigned int sequence;
		unsigned int lsa_header;
	}  __attribute__((packed)) ospfdatabasedescription;

typedef struct  OSPFLSAHEADER
	{
		unsigned short lsa_age;
		unsigned char options;
		unsigned char lsa_type;
		unsigned int link_state_id;
		unsigned int adv_router;
		unsigned int lsa_sequence;
		unsigned short lsa_checksum;
		unsigned short length;
	}  __attribute__((packed)) ospflsaheader;

extern unsigned char *buffer;

		
class ospf_f{
	
	public:

		ospfheader header;
		ospfhello hellof;
		void checksum(ospfheader , ospfhello,int );
		
		static int ReceiverOSPFv22(struct iphdr *,int , unsigned char *);
		void hello();
		int *encode();
		int decode();
		static int ospf_f::SM(void);
		
		ospf_f();
};

int transmit_hello();
int transmit_hello2(unsigned int dest);

#endif
