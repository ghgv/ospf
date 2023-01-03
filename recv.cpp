#include "recv.h"
#include "ospf.h"
#include <iostream>
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
#include <vector> 

using namespace std;


extern bool DEBUG;
extern char input[50];

using namespace std;


receiver::receiver()
{
std::thread t(receiver::rx);
t.detach();
cout<<"Receiver process started\n";


}

static int receiver::rx()
{
	int sock_r;
	int buflen=0;
	sock_r=socket(AF_PACKET,SOCK_RAW,htons(ETH_P_ALL));
	//sock_r=socket(AF_INET,SOCK_RAW,0x59);
	  	
		
	if(sock_r<0)
	{
		printf("error in raw incoming socket\n");
	return -1;
	}
	
	unsigned char *buffer = (unsigned char *) malloc(65536); //to receive data
	memset(buffer,0,65536);
	struct sockaddr saddr;
	
	memset(&saddr, 0, sizeof(saddr));         /* Zero out structure */
	int saddr_len = sizeof (saddr);
	
	struct sockaddr_ll   sll3;
	memset(&sll3, 0x0, sizeof(struct sockaddr_ll));
	sll3.sll_family    = AF_PACKET;
	sll3.sll_ifindex   =  if_nametoindex("ens3f1");//fix me
	sll3.sll_protocol  = htons(ETH_P_ALL);
	bind(sock_r, (struct sockaddr *)&sll3, sizeof(sll3));//make sure about the interface number
	while(1)
	{
		
		buflen=recvfrom(sock_r,buffer,65536,0,&saddr,(socklen_t *)&saddr_len);
		
		if(buflen<0)
		{
			printf("error in reading recvfrom function\n");
		}
	
	struct ethhdr *eth = (struct ethhdr *)(buffer);
	if(DEBUG==true)
		{
		printf("\nEthernet Header[%i]\n",buflen);
		printf("\t|-Source Address : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X\n", 
		eth->h_source[0],eth->h_source[1],eth->h_source[2],eth->h_source[3],eth->h_source[4],eth->h_source[5]);
		printf("\t|-Destination Address : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X\n",
		eth->h_dest[0],eth->h_dest[1],eth->h_dest[2],eth->h_dest[3],eth->h_dest[4],eth->h_dest[5]);
		printf("\t|-Protocol : %d\n",(eth->h_proto));	//fix me
		}
		struct sockaddr_in source,dest;
		struct iphdr *ip = (struct iphdr*)(buffer + sizeof(struct ethhdr));
		
		memset(&source, 0, sizeof(source));
		source.sin_addr.s_addr = ip->saddr;
		memset(&dest, 0, sizeof(dest));
		dest.sin_addr.s_addr = ip->daddr;
	if(DEBUG==true)
		{
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
	 	}
	 if(((unsigned int)ip->protocol)==89)
	 	{	
	 	
	 	ospf_f::ReceiverOSPFv22(ip,sll3.sll_ifindex,buffer );
	 	}
	 		
	}
}





