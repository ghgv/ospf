
/*---------- The Linux Channel ------------*/

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
#include "macs.h"
#include "ospf.h"
#include "cli.h"
#include "recv.h"
#include "transmitter.h"



#define ETHSIZE         14
#define IPHSIZE         20
#define TCPHSIZE        20



typedef uint64_t u64;
typedef uint32_t u32;
typedef uint16_t u16;

int sock_fd;
char *argumento1=NULL; // Interface
char *argumento2=NULL; // IP
bool DEBUG=1;
char input[50] = " ";
unsigned char *buffer = (unsigned char *) malloc(65536); //to receive data

ospf_f *ospf_header;
receiver RX;
transmitter *TX;

//enum _Boolean_  { FALSE=0, TRUE=1 };

int create_socket(char *device)
{
	int sock_fd;
	struct ifreq ifr;
	struct sockaddr_ll sll;
	memset(&ifr, 0, sizeof(ifr));
	memset(&sll, 0, sizeof(sll));
	
	sock_fd = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
   	if(sock_fd == 0)
		{
		printf("ERR: socket creation for device: %s\n", device); return false; 
		}
	strncpy(ifr.ifr_name, device, sizeof(ifr.ifr_name));
	if(ioctl(sock_fd, SIOCGIFINDEX, &ifr) == -1) 
		{
		printf(" ERR: ioctl failed for device: %s\n", device); return false; 
		}

	sll.sll_family      = AF_PACKET;
	sll.sll_ifindex     = ifr.ifr_ifindex;
	sll.sll_protocol    = htons(ETH_P_ALL);
	if(bind(sock_fd, (struct sockaddr *) &sll, sizeof(sll)) == -1) 
		{ 
		printf("ERR: bind failed for device: %s\n", device); return false; 
		}
return sock_fd;
}

unsigned short in_cksum1(u16 *ptr, int nbytes)
{
  register long sum=0;
  u16 oddbyte;
  register u16 answer;

  while(nbytes>1) 
  	{ 
  		sum += *ptr++; nbytes -= 2; 
  	}
  if(nbytes == 1) { oddbyte = 0; *((unsigned char *) &oddbyte) = *(unsigned char *)ptr; sum += oddbyte; }
  sum  = (sum >> 16)+(sum & 0xffff); sum+=(sum >> 16); answer = ~sum;
  return(answer);
}
int independentThread() 

{
	
    	std::cout << "Starting process ospf.\n";
    	sock_fd = create_socket(argumento1);
		if(!(sock_fd) ) 
		{
			printf("no sock_fd found\n"); return 0; 
		}
	
	while(1)
		{
    		std::this_thread::sleep_for(std::chrono::seconds(30));
		std::cout << "Sending hello packet.\n";
		sprintf(input, "\n");
		struct iphdr ip;
		memset(&ip, 0x0, IPHSIZE);
		ip.version    = 4;
	   	ip.ihl        = IPHSIZE >> 2;
		ip.tos        = 0;
		ip.tot_len    = htons(48+IPHSIZE);
		ip.id         = htons(rand()%65535);
		ip.frag_off   = 0;
		ip.ttl        = 1;//htons(1);
		ip.protocol   = 0x59;
		ip.saddr      = inet_addr(argumento2);
		ip.daddr	= inet_addr("224.0.0.5");
		ip.check      = (unsigned short)in_cksum1((unsigned short *)&ip, IPHSIZE);
		BYTE buf[300];
		memcpy(buf, l2, ETHSIZE);
		memcpy(buf+ETHSIZE, &ip, IPHSIZE);
		//memcpy(buf+ETHSIZE+IPHSIZE, (const void *)ospf_header->header, 48); 
		
		write(sock_fd, (BYTE *)buf, ETHSIZE+ntohs(ip.tot_len));

	}
		   
}

 
void threadCaller() 
{

    //std::thread t(independentThread);
    //t.detach();
}


int main(int argc, char ** argv)
{
	startCLI();
	//threadCaller();
	
	argumento1=argv[1]; // Interface
	argumento2=argv[2]; // IP
	TX= new transmitter(argumento1);
	ospf_header = new ospf_f();
	while(1){}
	
	return 0;
}
