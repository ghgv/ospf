
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

#include "ospf.h"

extern bool DEBUG;
extern char input[50];
extern char *argumento1;
extern char *argumento2;//Interface name

struct ifreq ifr;
//struct sockaddr_in source,dest;
//struct iphdr *ip = (struct iphdr*)(buffer + sizeof(struct ethhdr));
struct sockaddr_ll   sll2;


ospf_f::ospf_f(){
	header.version=2; 
	header.type=1; //1 Hello 2, database description DD, LSR, LSU ,LSACV
	header.packetlenght=htons(48);
	header.router_id=(inet_addr("192.168.1.2"));
	header.area_id=inet_addr("0.0.0.0");
	header.checksum=htons(0);
	header.Autype=htons(0);
	header.auth1=htonl(0);
	hello();
	checksum((ospfheader )header, (ospfhello) hellof);
	//printf("CS  %04X\n", header.checksum);
	std::thread t(ospf_f::ReceiverOSPF2);
	t.detach();
	
}

int ospf_f::*encode()
{
	
	
	return NULL;

}


void ospf_f::checksum(ospfheader header1, ospfhello header2){
	
	unsigned int check=0;
	unsigned short *head = NULL;
	unsigned char *head2, *head4 = NULL;
	unsigned short *head3  = NULL;
	head = (unsigned short *)&header1;
	head2 = (unsigned char *)&header1;
	head3 = (unsigned short *)&header2;
	head4 = (unsigned char *)&header2;
	
	for(int i = 0; i < 12; i++)  //Omiting the Autentication byes
    	{
        	check += (head[i]);
	        check = (check & 0xFFFF) + (check >> 16);
    	}
	for(int i = 0; i < 12; i++)  //fix me
    	{
        	check += (head3[i]);
	        check = (check & 0xFFFF) + (check >> 16);
    	}
    	
    	
	header.checksum=(~check &  0xFFFF);
}

void ospf_f::hello()
{
	hellof.network_mask=inet_addr("255.255.255.0");
	hellof.HelloInterval=htons(10); //30 seconds
	hellof.Options=0x2;
	hellof.Priority=1;
	hellof.RouterDeadInterval=htonl(40);
	hellof.DesignatedRouter=inet_addr("192.168.0.1");
	hellof.BackupDesignatedRouter=inet_addr("0.0.0.0");
	hellof.Neighbor=inet_addr("192.168.2.12");
}

static int ospf_f::ReceiverOSPF2()
{
	int sock_r;
	int buflen=0;
	int SRC_PORT=0x59;
	
	sock_r=socket(AF_PACKET,SOCK_RAW,htons(ETH_P_ALL));
	//sock_r=socket(AF_INET,SOCK_RAW,0x59);
	
  	
  	// Get to know the network interfaces
  	
  	char interfaceName[IFNAMSIZ];
  	for (int j =1;j<5;j++)
  	{
		char *interface = if_indextoname(j, (char *)&interfaceName); /* retrieve the name of interface 1 */
		if (interface == NULL)
		{
	     		printf("if_indextoname() failed with errno =  %d %s \n",   errno,strerror(errno));
	     		return;
	  	}
	  	printf("%i %s\n",j, interfaceName);
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
	
	unsigned char *buffer = (unsigned char *) malloc(65536); //to receive data
	memset(buffer,0,65536);
	struct sockaddr saddr;
	
	//addrlen = sizeof(from); /* must be initialized */
	
	memset(&saddr, 0, sizeof(saddr));         /* Zero out structure */
	int saddr_len = sizeof (saddr);
	//Receive a network packet and copy in to buffer

	int32_t ret;
	memset(&sll2, 0x0, sizeof(struct sockaddr_ll));
	sll2.sll_family    = AF_PACKET;
	
	sll2.sll_ifindex   =  if_nametoindex("ens3f1");//fix me
	sll2.sll_protocol  = htons(ETH_P_ALL);
	
	int rc = bind(sock_r, (struct sockaddr *)&sll2, sizeof(sll2));
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
		printf("\t|-Source Address : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X\n",eth->h_source[0],eth->h_source[1],eth->h_source[2],eth->h_source[3],eth->h_source[4],eth->h_source[5]);
		printf("\t|-Destination Address : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X\n",eth->h_dest[0],eth->h_dest[1],eth->h_dest[2],eth->h_dest[3],eth->h_dest[4],eth->h_dest[5]);
		printf("\t|-Protocol : %d\n",(eth->h_proto));	//fix me
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
	 	if(((unsigned int)ip->protocol)==89)
	 		{
		 	ospfheader *ospff = (ospfheader*)(buffer + sizeof(struct ethhdr)+ sizeof(struct iphdr));
		 	struct sockaddr_in routerid;
		 	memset(&routerid, 0, sizeof(routerid));
		 	routerid.sin_addr.s_addr = ospff->router_id;
		 	printf("OSPF header: \n");
		 	printf("\t|-Version : %i\n",(unsigned char)ospff->version);
		 	printf("\t|-Type : %i \n",(unsigned char)ospff->type);
			printf("\t|-Length : %i\n",(unsigned short)ntohs(ospff->packetlenght));
		 	printf("\t|-Router ID : %s \n",inet_ntoa(routerid.sin_addr));//Waring for DR_ID
		 	printf("\t|-Area ID: %i\n",ntohs(ospff->area_id));
		 	printf("\t|-Checksum : %i\n",(unsigned short)ospff->checksum);
		 	printf("\t|-Autype : %i\n",(unsigned short)ospff->Autype);
		 	printf("\t|-Auth  : %l\n", (unsigned long)ospff->auth1);
			
	 		ospfhello *ospfh = (ospfhello*)(buffer + sizeof(struct ethhdr)+ sizeof(struct iphdr)+sizeof(ospfheader));
	 		struct sockaddr_in mask, designated, backupdesignated; //network mask
	 		memset(&mask, 0, sizeof(mask));
			mask.sin_addr.s_addr = ospfh->network_mask;
	 		memset(&designated, 0, sizeof(designated));
			designated.sin_addr.s_addr = ospfh->DesignatedRouter;
			memset(&backupdesignated, 0, sizeof(backupdesignated));
			backupdesignated.sin_addr.s_addr = ospfh->BackupDesignatedRouter;
			printf("\t|-Type : %i \n",(unsigned char)ospff->type);
			printf("\t|-Network Mask : %s\n",inet_ntoa(mask.sin_addr));
			printf("\t|-Hello interval : %i\n",(unsigned short)ntohs(ospfh->HelloInterval));
		 	printf("\t|-Options : %x \n",(unsigned char)ospfh->Options);
		 	printf("\t|-Priority: %d\n",(unsigned char)ospfh->Priority);
		 	printf("\t|-RouterDeadInterval : %i\n",ntohl((unsigned int)ospfh->RouterDeadInterval));
		 	printf("\t|-DesignatedRouter : %s\n",inet_ntoa(designated.sin_addr));
			printf("\t|-Backup Designated Router : %s\n",inet_ntoa(backupdesignated.sin_addr));

	 		
		 	int total=ntohs(ip->tot_len)-(sizeof(struct iphdr)+sizeof(ospfheader)+sizeof(ospfhello));
		 	//printf("Trail: %i\n",total);
		 	//printf("Total. %i eth: %i ip: %i  ospfh %i ospfhe %i Tail: %i",ntohs(ip->tot_len),sizeof(struct ethhdr),sizeof(struct iphdr),sizeof(ospfheader),sizeof(ospfhello),total);
		 	/*if(total==0)
		 		{
		 		struct sockaddr_in neighbor0;
		 		memset(&neighbor0, 0, sizeof(neighbor0));
				neighbor0.sin_addr.s_addr = ospfh->Neighbor;
		 		printf("\t|-Neighbor[0] : %s\n",inet_ntoa(neighbor0.sin_addr));	 	
			 	}
		 	*/
			if(total>=0)
				{
				int num_neighbors=total/4+1;
//		 		printf("Total. %i eth: %i ip: %i  ospfh %i ospfhe %i Tail: %i",ntohs(ip->tot_len),sizeof(struct ethhdr),sizeof(struct iphdr),sizeof(ospfheader),sizeof(ospfhello),total);
			 	struct sockaddr_in neighbor[num_neighbors];
			 	for (int k=0;k<num_neighbors;k++)
			 		{
			 		memset(&neighbor[k], 0, sizeof(neighbor));
					neighbor[k].sin_addr.s_addr = ospfh->Neighbor+k;
				 	for(int k=0;k<num_neighbors;k++)
				 		{
				 		printf("\t|-Neighbor[%i] : %s\n",k,inet_ntoa(neighbor[k].sin_addr));
				 		}
		 			}
	 		 	}
	 		 }
	}
}
}



