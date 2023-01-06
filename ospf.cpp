
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/wait.h>
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

#include "ospf.h"
#include "neighbors.h"
#include "transmitter.h"

static const char * const states_num[] = { "Down", "Init", "ST_Two_Way" ,"ExStart", "Exch"};

extern bool DEBUG;
extern char input[50];
extern char *argumento1;
extern char *argumento2;//Interface name
extern transmitter *TX;
vector<neighbor_t> Neighbor;
neighbor_t NB;
unsigned char *head;
ospfheader 	header2;
ospfhello	hello2;
ospfdatabasedescription dd2;



struct ifreq ifr;
//struct sockaddr_in source,dest;
//struct iphdr *ip = (struct iphdr*)(buffer + sizeof(struct ethhdr));
struct sockaddr_ll   sll2;

enum {
        ST_Down,
        ST_Init,
        ST_Two_Way,
        ST_ExStart,
        ST_Exchange,
        ST_Loading,
        ST_Full
} STATES;

typedef enum {
        EVT_MODE,
        EVT_NEXT
} EVENTS;





ospf_f::ospf_f(){
	header.version=2; 
	header.type=1; //1 Hello 2, database description DD, LSR, LSU ,LSACV
	header.packetlenght=htons(48);
	header.router_id=(inet_addr("192.168.0.2"));
	header.area_id=inet_addr("0.0.0.0");
	header.checksum=htons(0);
	header.Autype=htons(0);
	header.auth1=htonl(0);
	DEBUG=false;
	hello();
	checksum((ospfheader )header, (ospfhello) hellof,12);
	head= malloc(1500);
	memcpy(head,&header,48);
	//printf("CS  %04X\n", header.checksum);
	std::thread t(ospf_f::SM);
	t.detach();
	
}

int ospf_f::*encode()
{
	
	
	return NULL;

}


void ospf_f::checksum(ospfheader header1, ospfhello header2,int limit){
	
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
	for(int i = 0; i < limit; i++)  //fix me
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


static int ospf_f::ReceiverOSPFv22(struct iphdr *ip,int interface_number, unsigned char *buffer)
{
 		
	 	
	 	ospfheader *ospff = (ospfheader*)(buffer + sizeof(struct ethhdr)+ sizeof(struct iphdr));
	 	struct sockaddr_in routerid;
	 	memset(&routerid, 0, sizeof(routerid));
	 	routerid.sin_addr.s_addr = ospff->router_id;
	 	if(DEBUG==true)
			{
	 		printf("OSPF header:* \n");
		 	printf("\t|-Version : %i\n",(unsigned char)ospff->version);
		 	printf("\t|-Type : %i \n",(unsigned char)ospff->type);
			printf("\t|-Length : %i\n",(unsigned short)ntohs(ospff->packetlenght));
		 	printf("\t|-Router ID : %s \n",inet_ntoa(routerid.sin_addr));//Waring for DR_ID
		 	printf("\t|-Area ID: %i\n",ntohs(ospff->area_id));
		 	printf("\t|-Checksum : %i\n",(unsigned short)ospff->checksum);
		 	printf("\t|-Autype : %i\n",(unsigned short)ospff->Autype);
		 	printf("\t|-Auth  : %l\n", (unsigned long)ospff->auth1);
			}
		if((unsigned char)ospff->type==1)
		{			
	 		ospfhello *ospfh = (ospfhello*)(buffer + sizeof(struct ethhdr)+ sizeof(struct iphdr)+sizeof(ospfheader));
	 		struct sockaddr_in mask, designated, backupdesignated; //network mask
	 		memset(&mask, 0, sizeof(mask));
			mask.sin_addr.s_addr = ospfh->network_mask;
	 		memset(&designated, 0, sizeof(designated));
			designated.sin_addr.s_addr = ospfh->DesignatedRouter;
			memset(&backupdesignated, 0, sizeof(backupdesignated));
			backupdesignated.sin_addr.s_addr = ospfh->BackupDesignatedRouter;
			
			if(DEBUG==true)
				{
				printf("OSPF hello: \n");
				printf("\t|-Network Mask : %s\n",inet_ntoa(mask.sin_addr));
				printf("\t|-Hello interval : %i\n",(unsigned short)ntohs(ospfh->HelloInterval));
			 	printf("\t|-Options : %x \n",(unsigned char)ospfh->Options);
			 	printf("\t|-Priority: %d\n",(unsigned char)ospfh->Priority);
			 	printf("\t|-RouterDeadInterval : %i\n",ntohl((unsigned int)ospfh->RouterDeadInterval));
			 	printf("\t|-DesignatedRouter : %s\n",inet_ntoa(designated.sin_addr));
				printf("\t|-Backup Designated Router : %s\n",inet_ntoa(backupdesignated.sin_addr));
				}
		
			int total=ntohs(ip->tot_len)-(sizeof(struct iphdr)+sizeof(ospfheader)+sizeof(ospfhello));
	 		//int total=(unsigned short)ntohs(ospff->packetlenght)-(sizeof(ospfheader)+sizeof(ospfhello)-sizeof(unsigned int));
			if(total >= 0)
				{
				int num_neighbors=total/4+1;
				
		 		//printf("Total ospf: %i eth: %i ip: %i  ospfh %i ospfhe %i Tail: %i",(unsigned short)ntohs(ospff->packetlenght),sizeof(struct ethhdr),sizeof(struct iphdr),sizeof(ospfheader),sizeof(ospfhello),total);
			 	struct sockaddr_in neighbor[num_neighbors];
			 	printf("Num neighbors:%i\n",num_neighbors);
			 	for (int k=0;k<num_neighbors;k++)
			 		{

			 		memset(&neighbor[k], 0, sizeof(neighbor));
					neighbor[k].sin_addr.s_addr = (ospfh->Neighbor)++;
				 	//for(int k=0;k<num_neighbors;k++)
				 		{
				 		if(DEBUG==true)
							{		
				 			printf("\t|-Neighbor[%i] : %s\n",k,inet_ntoa(neighbor[k].sin_addr));
				 			}
printf("Size: %i\n",Neighbor.size());
				 		
				 		if (neighbor[k].sin_addr.s_addr ==0x0200a8c0)//Router ID
				 			{
				 			//printf("Self %x \n",neighbor[k].sin_addr.s_addr);
				 			//NB.state=(int)ST_Init;
				 			for (auto i = Neighbor.begin(); i != Neighbor.end(); ++i)
				 				{
				 			//	printf("ite %x \n",i->Neighbor_ID);
				 				if(i->Neighbor_ID==ospff->router_id)//0x0200a8c0
				 					{
				 					i->State=2;
				 					printf("Self2 %x %s\n",i->Neighbor_ID,states_num[i->State]);
				 					}
				 				}	
				 			}
					 	if(Neighbor.size()==0)
							{
							NB.Neighbor_ID=ospff->router_id;//neighbor[k].sin_addr.s_addr;
					 		NB.Priority=ospfh->Priority;
					 		NB.dead_time=4*ospfh->HelloInterval;
					 		NB.addr1=ip->saddr;
					 		NB.State=(int)ST_Init;
					 		NB.interface_number=1;
					 		//printf("\t|Pushed -Neighbor[%i] : %x %x\n",k,(NB.Neighbor_ID),(NB.addr1));
							Neighbor.push_back(NB);  
							}
						}
		 			}
		 		
	 		 	}
	 		 
		} 
		if((unsigned char)ospff->type==2)
		{
			
			ospfdatabasedescription *ospfdd = (ospfdatabasedescription*)(buffer + sizeof(struct ethhdr)+ sizeof(struct iphdr)+sizeof(ospfheader));
	 		if(DEBUG==true)
				{
				printf("OSPF DD: \n");
				printf("\t|-MTU : %i\n",ntohs(ospfdd->mtu));
				//
				printf("\t|-Options: %i\n",ospfdd->options);
			 	printf("\t|-DD : %x \n",(unsigned char)ospfdd->dd);
			 	printf("\t|-Sequence : %i\n",ntohl((unsigned int)ospfdd->sequence));
			 	
				}
			int total=ntohs(ip->tot_len)-(sizeof(struct iphdr)+sizeof(ospfheader)+sizeof(ospfdatabasedescription));
			if(total >= 0)
				{
				int num_lsa=total/4+1;
				ospflsaheader *ospflsa =(ospflsaheader *)(buffer + sizeof(struct ethhdr)+ sizeof(struct iphdr)+sizeof(ospfheader)+sizeof(ospfdatabasedescription));
				if(DEBUG==true)
					{
					printf("\t|-LSA[0] : %i\n",ntohl((unsigned int)ospfdd->lsa_header));
					printf("\t|-Age    : %i\n",ntohs((unsigned short)ospflsa->lsa_age));
					}
				}
			for (auto i = Neighbor.begin(); i != Neighbor.end(); ++i)
				{
				if(i->Neighbor_ID==ospff->router_id)
					{
					i->sequence=ntohl((unsigned int)ospfdd->sequence);
					}
				}
		
		}
	 		 
	return 0;
}


int ospf_f::decode()
{
	return 0;
}




static int ospf_f::SM(void)
{ 
	while(TX==NULL);
	printf("\nINF: SM started");
	unsigned char buffer[48];
	memcpy(buffer, head, 48); 
	TX->transmit(0x59,"192.168.0.2","224.0.0.5", 48, buffer);//OJO
	sleep(10);
	
	while (1)
	{  
		for (auto i = Neighbor.begin(); i != Neighbor.end(); ++i)
		{	  
		int State=i->State;
		    	{
			switch (State)
		    		{
		    		case ST_Down:
		    			//i->State=1;
					transmit_hello();
					sleep(5);
					break;
				case ST_Init:
					struct in_addr destination;
					destination.s_addr=i->Neighbor_ID;
						{
						//i->State=2;
						printf("Hello2:\n");
	 			      		transmit_hello2(i->Neighbor_ID,i->addr1);
	 			      		//sleep(5);
						}		      			
			      		break;
				case ST_Two_Way:
			      		i->State=3;
			      		printf("TW:\n");
			      		transmit_dd(i->Neighbor_ID,i->addr1,i->sequence);
			      		sleep(5);
			      		break;
			      	case ST_ExStart:
			      		i->State=4;
			      		//transmit_hello();
			      		break;

				}
		     	break;
		    	}
		}
		if(Neighbor.size()==0)
			{
			TX->transmit(0x59,"192.168.0.2","224.0.0.5", 48, buffer);//OJO		
			sleep(10);
			}
	}
return 0;
}


int checksum2(ospfheader header1, ospfhello header22,int limit){
	
	unsigned int check=0;
	unsigned short *head = NULL;
	unsigned char *head2, *head4 = NULL;
	unsigned short *head3  = NULL;
	head = (unsigned short *)&header1;
	head2 = (unsigned char *)&header1;
	head3 = (unsigned short *)&header22;
	head4 = (unsigned char *)&header22;
	
	for(int i = 0; i < 12; i++)  //Omiting the Autentication byes
    	{
        	check += (head[i]);
	        check = (check & 0xFFFF) + (check >> 16);
    	}
	for(int i = 0; i < limit; i++)  //fix me
    	{
        	check += (head3[i]);
	        check = (check & 0xFFFF) + (check >> 16);
    	}
	header2.checksum=(~check &  0xFFFF);
	return 0;
}

int checksum3(ospfheader header1, ospfdatabasedescription header22,int limit){
	
	unsigned int check=0;
	unsigned short *head = NULL;
	unsigned char *head2, *head4 = NULL;
	unsigned short *head3  = NULL;
	head = (unsigned short *)&header1;
	head2 = (unsigned char *)&header1;
	head3 = (unsigned short *)&header22;
	head4 = (unsigned char *)&header22;
	
	for(int i = 0; i < 12; i++)  //Omiting the Autentication byes
    	{
        	check += (head[i]);
	        check = (check & 0xFFFF) + (check >> 16);
    	}
	for(int i = 0; i < limit; i++)  //fix me
    	{
        	check += (head3[i]);
	        check = (check & 0xFFFF) + (check >> 16);
    	}
	header2.checksum=(~check &  0xFFFF);
	return 0;
}

int transmit_hello(){
	printf("Hello multicast");
	header2.version=2; 
	header2.type=1; //1 Hello 2, database description DD, LSR, LSU ,LSACV
	header2.packetlenght=htons(44);
	header2.router_id=(inet_addr("192.168.0.2"));
	header2.area_id=inet_addr("0.0.0.0");
	header2.checksum=htons(0);
	header2.Autype=htons(0);
	header2.auth1=htonl(0);
	hello2.network_mask=inet_addr("255.255.255.0");
	hello2.HelloInterval=htons(10); //30 seconds
	hello2.Options=0x2;
	hello2.Priority=1;
	hello2.RouterDeadInterval=htonl(40);
	hello2.DesignatedRouter=inet_addr("192.168.0.1");
	hello2.BackupDesignatedRouter=inet_addr("0.0.0.0");
	hello2.Neighbor=inet_addr("0.0.0.0");
	checksum2((ospfheader )header2, (ospfhello) hello2,12);
	unsigned char buffer2[44];
	memcpy(buffer2, &header2, 24);
	memcpy((buffer2+24), &hello2, 20); 
	TX->transmit(0x59,"192.168.0.2","224.0.0.5", 44, buffer2);//OJO
	
return 0;
	
}
int transmit_hello2(unsigned int neigh,unsigned int dest){
	struct in_addr destination,neighbor_1;
	destination.s_addr=dest;
	neighbor_1.s_addr=neigh;
	printf("Hello2: %s",inet_ntoa(destination));
	header2.version=2; 
	header2.type=1; //1 Hello 2, database description DD, LSR, LSU ,LSACV
	header2.packetlenght=htons(48);
	header2.router_id=(inet_addr("192.168.0.2"));
	header2.area_id=inet_addr("0.0.0.0");
	header2.checksum=htons(0);
	header2.Autype=htons(0);
	header2.auth1=htonl(0);
	hello2.network_mask=inet_addr("255.255.255.0");
	hello2.HelloInterval=htons(10); //30 seconds
	hello2.Options=0x2;
	hello2.Priority=1;
	hello2.RouterDeadInterval=htonl(40);
	hello2.DesignatedRouter=inet_addr("192.168.0.1");
	hello2.BackupDesignatedRouter=inet_addr("0.0.0.0");
	hello2.Neighbor=inet_addr((const char *)inet_ntoa(neighbor_1));
	checksum2((ospfheader )header2, (ospfhello) hello2,12);// 12 sin uso!
	
	unsigned char buffer2[48];
	memcpy(buffer2, &header2, 24);
	memcpy((buffer2+24), &hello2, 24); 
	TX->transmit(0x59,"192.168.0.2",(const char *)inet_ntoa(destination), 48, buffer2);//OJO
	sleep(5);
return 0;
	
}

int transmit_dd(unsigned int neigh,unsigned int dest,unsigned int sequence){
	struct in_addr destination,neighbor_1;
	destination.s_addr=dest;
	neighbor_1.s_addr=neigh;
	printf("DD: %s ",inet_ntoa(destination));
	printf("Sizedof dd %d\n",sizeof(ospfdatabasedescription));
	header2.version=2; 
	header2.type=2; //1 Hello 2, database description DD, LSR, LSU ,LSACV
	header2.packetlenght=htons(32);
	header2.router_id=(inet_addr("192.168.0.2"));
	header2.area_id=inet_addr("0.0.0.0");
	header2.checksum=htons(0);
	header2.Autype=htons(0);
	header2.auth1=htonl(0);
	dd2.mtu=htons(1500);
	dd2.options=0x02;
	dd2.dd=0;
	dd2.sequence=htonl(sequence);
	checksum3((ospfheader )header2, (ospfdatabasedescription) dd2,4);
	unsigned char buffer2[48];
	memcpy(buffer2, &header2, 24);
	memcpy((buffer2+24), &dd2, 8); 
	TX->transmit(0x59,"192.168.0.2",(const char *)inet_ntoa(destination), 32, buffer2);//OJO
	sleep(5);
return 0;
	
}
