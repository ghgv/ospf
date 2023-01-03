#include "transmitter.h"

#include <stdio.h>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <netinet/tcp.h>
#include <netinet/ip.h>
#include <net/ethernet.h>
#include <linux/if_packet.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <cstdlib>

#include <stdlib.h>
#include <unistd.h> //write


extern char *argumento2;
extern char *argumento1;
extern int sock_fd;

BYTE l3[14] = { 0x01, 0x00, 0x5e, 0x00, 0x00, 0x05, 0x6c, 0xb3, 0x11, 0x1c, 0x90, 0x81, 0x08, 0x00};

transmitter::transmitter(){
}

transmitter::transmitter(char *device)
{
transmitter::c_socket(device);
}

unsigned short in_cksum(unsigned short *ptr, int nbytes)
{
  register long sum=0;
  unsigned short oddbyte;
  register unsigned short answer;

  while(nbytes>1) 
  	{ 
  		sum += *ptr++; nbytes -= 2; 
  	}
  if(nbytes == 1) { oddbyte = 0; *((unsigned char *) &oddbyte) = *(unsigned char *)ptr; sum += oddbyte; }
  sum  = (sum >> 16)+(sum & 0xffff); sum+=(sum >> 16); answer = ~sum;
  return(answer);
}


int transmitter::c_socket(char *device) //create socket
{
	int sock_fd;
	struct ifreq ifr;
	struct sockaddr_ll sll;
	memset(&ifr, 0, sizeof(ifr));
	memset(&sll, 0, sizeof(sll));
	printf("INF: socket creation for device: %s\n", device);
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
	this->socket_fd=sock_fd;
	printf("fd: %i %i\n",this->socket_fd, sock_fd);
	return sock_fd;
}

int transmitter::transmit(int protocol,unsigned char *sour_addr,unsigned char *dest_addr, int buffer_length, unsigned char *buffer)
{
	struct iphdr ip;
	printf("\nINF TX: Source %s ",sour_addr);
	printf("Dest %s ",dest_addr);
	printf("Protocol: %x\n",protocol);
	printf("%s \n",buffer);
	printf("%i \n",buffer_length);
	
	memset(&ip, 0x0, IPHSIZE);
	
	ip.version    = 4;
	ip.ihl        = IPHSIZE >> 2;
	ip.tos        = 0;
	ip.tot_len    = htons(buffer_length+IPHSIZE);
	ip.id         = htons(rand()%65535);
	ip.frag_off   = 0;
	ip.ttl        = 1;//htons(1);
	ip.protocol   = protocol;
	ip.saddr      = inet_addr((const char *)sour_addr);
	ip.daddr      = inet_addr((const char *)dest_addr);
	ip.check      = (unsigned short)in_cksum((unsigned short *)&ip, IPHSIZE);
	BYTE buf[300];
	
	memcpy(buf, l3, ETHSIZE);
	memcpy(buf+ETHSIZE, &ip, IPHSIZE);
	memcpy(buf+ETHSIZE+IPHSIZE, buffer, buffer_length); 
	write(this->socket_fd, (BYTE *)buf, ETHSIZE+ntohs(ip.tot_len));
	

return 0;
}

