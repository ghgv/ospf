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



extern char *argumento2;
extern char *argumento1;

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
return sock_fd;
}

int transmit(int protocol,unsigned char *sour_addr,unsigned char *dest_addr, int lenght, unsigned char *buffer)
{
	struct iphdr ip;
	memset(&ip, 0x0, IPHSIZE);
	ip.version    = 4;
	ip.ihl        = IPHSIZE >> 2;
	ip.tos        = 0;
	ip.tot_len    = htons(lenght+IPHSIZE);
	ip.id         = htons(rand()%65535);
	ip.frag_off   = 0;
	ip.ttl        = 1;//htons(1);
	ip.protocol   = protocol;
	ip.saddr      = inet_addr(*dest_addr);
	ip.daddr      = inet_addr(*dest_addr);
	ip.check      = (unsigned short)in_cksum((unsigned short *)&ip, IPHSIZE);
	BYTE buf[300];
	memcpy(buf, l2, ETHSIZE);
	memcpy(buf+ETHSIZE, &ip, IPHSIZE);
	memcpy(buf+ETHSIZE+IPHSIZE, buffer, lenght); 
	write(sock_fd, (BYTE *)buf, ETHSIZE+ntohs(ip.tot_len));


return 0;
}

