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



#define ETHSIZE         14
#define IPHSIZE         20
#define TCPHSIZE        20

typedef unsigned char  BYTE;             /* 8-bit   */
typedef unsigned short BYTEx2;           /* 16-bit  */
typedef unsigned long  BYTEx4;           /* 32-bit  */

typedef uint64_t u64;
typedef uint32_t u32;
typedef uint16_t u16;

char *argumento1=NULL; // IP address
char *argumento2=NULL; // Interface
bool DEBUG=false;
char input[50] = " ";
unsigned char *buffer = (unsigned char *) malloc(65536); //to receive data

ospf_f ospf_header;

enum _Boolean_  { FALSE=0, TRUE=1 };

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
		printf("ERR: socket creation for device: %s\n", device); return FALSE; 
		}
	strncpy(ifr.ifr_name, device, sizeof(ifr.ifr_name));
	if(ioctl(sock_fd, SIOCGIFINDEX, &ifr) == -1) 
		{
		printf(" ERR: ioctl failed for device: %s\n", device); return FALSE; 
		}

	sll.sll_family      = AF_PACKET;
	sll.sll_ifindex     = ifr.ifr_ifindex;
	sll.sll_protocol    = htons(ETH_P_ALL);
	if(bind(sock_fd, (struct sockaddr *) &sll, sizeof(sll)) == -1) 
		{ 
		printf("ERR: bind failed for device: %s\n", device); return FALSE; 
		}
return sock_fd;
}

unsigned short in_cksum(u16 *ptr, int nbytes)
{
  register long sum=0;
  u16 oddbyte;
  register u16 answer;

  while(nbytes>1) { sum += *ptr++; nbytes -= 2; }
  if(nbytes == 1) { oddbyte = 0; *((unsigned char *) &oddbyte) = *(unsigned char *)ptr; sum += oddbyte; }
  sum  = (sum >> 16)+(sum & 0xffff); sum+=(sum >> 16); answer = ~sum;
  return(answer);
}

int independentThread() 
{
	
    	std::cout << "Starting process ospf.\n";
    	int sock_fd = create_socket(argumento1);
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
		ip.tot_len    = htons(44+IPHSIZE);
		ip.id         = htons(rand()%65535);
		ip.frag_off   = 0;
		ip.ttl        = 1;//htons(1);
		ip.protocol   = 0x59;
		ip.saddr      = inet_addr(argumento2);
		ip.daddr	     = inet_addr("224.0.0.5");
		ip.check      = (unsigned short)in_cksum((unsigned short *)&ip, IPHSIZE);
		BYTE buf[300];
		memcpy(buf, l2, ETHSIZE);
		memcpy(buf+ETHSIZE, &ip, IPHSIZE);
		memcpy(buf+ETHSIZE+IPHSIZE, &ospf_header.header, 44); 
		
		write(sock_fd, (BYTE *)buf, ETHSIZE+ntohs(ip.tot_len));

	}
		   
}

int ReceiverOSPF()
{
	int sock_r;
	int buflen=0;
	int SRC_PORT=0x59;
	struct ifreq ifr;
	sock_r=socket(AF_PACKET,SOCK_RAW,htons(ETH_P_ALL));
	//sock_r=socket(AF_INET,SOCK_RAW,0x59);
	
  	char interfaceName[IFNAMSIZ];
  	for (int j =1;j<5;j++)
  	{
		char *interface = if_indextoname(j, (char *)&interfaceName); /* retrieve the name of interface 1 */
		if (interface == NULL)
		{
	     		printf("if_indextoname() failed with errno =  %d %s \n",   errno,strerror(errno));
	     		return;
	  	}
	  	printf("%s\n",interfaceName);
  	}
	
	memset(&ifr, 0, sizeof(ifr));
	printf("%s\n",argumento1);
	snprintf(ifr.ifr_name, sizeof(ifr.ifr_name), "ens3f1");
	printf("---- %s\n",ifr.ifr_name);
	if (( setsockopt(sock_r, SOL_SOCKET, SO_BINDTODEVICE, (void *)&ifr, sizeof(ifr))) < 0)
	{
	    perror("Server-setsockopt() error for SO_BINDTODEVICE");
	    printf("%s\n", strerror(errno));
	    close(sock_r);
	    exit(-1);
	}
	
	
	memset(&ifr, 0, sizeof(struct ifreq));
	snprintf(ifr.ifr_name, sizeof(ifr.ifr_name), "ens3f1");
	ioctl(sock_r, SIOCGIFINDEX, &ifr);
	setsockopt(sock_r, SOL_SOCKET, SO_BINDTODEVICE,  (void*)&ifr, sizeof(struct ifreq));
	
	if(sock_r<0)
	{
		printf("error in raw incoming socket\n");
	return -1;
	}
	
	
	memset(buffer,0,65536);
	struct sockaddr saddr;
	
	//addrlen = sizeof(from); /* must be initialized */
	
	memset(&saddr, 0, sizeof(saddr));         /* Zero out structure */
	int saddr_len = sizeof (saddr);
	//Receive a network packet and copy in to buffer
	struct sockaddr_ll   sll;
	int32_t ret;
	memset(&sll, 0x0, sizeof(struct sockaddr_ll));
	sll.sll_family    = AF_PACKET;
	sll.sll_ifindex   = 5;//ifindex;
	sll.sll_protocol  = htons(ETH_P_ALL);
	
	int rc = bind(sock_r, (struct sockaddr *)&sll, sizeof(sll));
	while(1)
	{
		
		buflen=recvfrom(sock_r,buffer,65536,0,&saddr,(socklen_t *)&saddr_len);
//		byflen=recvfrom(sock_r,buffer,65536,0,&saddr,(socklen_t *)&saddr_len);
		if(buflen<0)
		{
			printf("error in reading recvfrom function\n");
			//return -1;
		}
	
	struct ethhdr *eth = (struct ethhdr *)(buffer);
	if(DEBUG==TRUE)
	{
		printf("\nEthernet Header\n");
		printf("\t|-Source Address : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X\n",eth->h_source[0],eth->h_source[1],eth->h_source[2],eth->h_source[3],eth->h_source[4],eth->h_source[5]);
		printf("\t|-Destination Address : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X\n",eth->h_dest[0],eth->h_dest[1],eth->h_dest[2],eth->h_dest[3],eth->h_dest[4],eth->h_dest[5]);
		printf("\t|-Protocol : %x\n",ntohs(eth->h_proto));	
		
		struct sockaddr_in source,dest;
		struct iphdr *ip = (struct iphdr*)(buffer + sizeof(struct ethhdr));
		memset(&source, 0, sizeof(source));
		source.sin_addr.s_addr = ip->saddr;
		memset(&dest, 0, sizeof(dest));
		dest.sin_addr.s_addr = ip->daddr;
	 	printf("\t|-Version : %d\n",(unsigned int)ip->version);
	 	printf("\t|-Internet Header Length : %d DWORDS or %d Bytes\n",(unsigned int)ip->ihl,((unsigned int)(ip->ihl))*4);
		printf("\t|-Type Of Service : %d\n",(unsigned int)ip->tos);
	 	printf("\t|-Total Length : %d Bytes\n",ntohs(ip->tot_len));
	 	printf("\t|-Identification : %d\n",ntohs(ip->id));
	 	printf("\t|-Time To Live : %d\n",(unsigned int)ip->ttl);
	 	printf("\t|-Protocol : %d\n",(unsigned int)ip->protocol);
	 	printf("\t|-Header Checksum : %d\n",ntohs(ip->check));
	 	printf("\t|-Source IP : %s\n", inet_ntoa(source.sin_addr));
	 	printf("\t|-Destination IP : %s\n",inet_ntoa(dest.sin_addr));
	 	//if (strcmp(inet_ntoa(source.sin_addr),"192.168.0.1")==0)
	 	// 	return 0;
	 	sprintf(input, " \n");
	 	
 	}
	}
}
 
void threadCaller() 
{

    std::thread t(independentThread);
    t.detach();
}

void startRx() 
{

    std::thread t(ReceiverOSPF);
    t.detach();
}

int main(int argc, char ** argv)
{
	startCLI();
	//threadCaller();
	//startRx();
	argumento1=argv[1]; // IP address
	argumento2=argv[2]; // Interface
	while(1){}
	
	return 0;
}
