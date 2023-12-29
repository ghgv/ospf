#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <readline/readline.h>
#include <readline/history.h>
#include <thread>
#include <vector> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
using namespace std;  

#include "neighbors.h"
#include "tokenizer.h"
#include "interfaces.h"
#include "ospf.h"

extern bool DEBUG;
extern char input[50];

extern vector<neighbor_t> Neighbor;
extern vector< ospflsaheader>Lsaheader;


static const char * const states_num[] = { "Down", "Init", "ST_Two_Way" ,"ExStart", "Exch"};

int cli()
{
	char* input, shell_prompt[100];
	
	rl_bind_key('\t', rl_complete);
	tokenizer *tokens= new tokenizer();

    	for(;;) {
        
        	snprintf(shell_prompt, sizeof(shell_prompt), "%s# ","configuration" );
		input = readline(shell_prompt);
	
        
        	if (!input)
        	    break;
        	    
        	if(strcmp(input,"clear") == 0)
		{
       	printf("\e[1;1H\e[2J");
      		}
		else if(strcmp(input,"priority")== 0)
     		{
     			char str[50];
    			scanf("%[^\n]+", str);
			printf(" %s", str);
     		
     		}
     		else if(strcmp(input,"debug")== 0)
     		{
		DEBUG=true;
     		}
     		else if(strcmp(input,"undebug")== 0)
     		{
     		
		DEBUG=false;
		
     		}
     		else if(strcmp(input,"exit")== 0)
     		{
     		break;
     		}
     		else if(strcmp(input,"neighbors")== 0)
     		{
	     		printf("Neighbor ID \tPri \tState \tDead time \tAddress \tInt\n");
	     		for (auto i = Neighbor.begin(); i != Neighbor.end(); ++i) 
				{
				struct sockaddr_in neighbor,out_address;
				memset(&neighbor, 0, sizeof(neighbor));
				neighbor.sin_addr.s_addr = (unsigned int)i->Neighbor_ID;
				memset(&out_address, 0, sizeof(out_address));
				out_address.sin_addr.s_addr = (unsigned int)i->addr1;

				printf("%s \t%i \t%s \t%i \t\t ",inet_ntoa(neighbor.sin_addr), i->Priority ,states_num[i->State] ,i->dead_time);//why it does not work
				printf(" %s \t%i \n",inet_ntoa(out_address.sin_addr), i->interface_number);
				}
     		}
     		else if(strcmp(input,"lsa")== 0)
     		{

				unsigned short lsa_age;
		unsigned char options;
		unsigned char lsa_type;
		unsigned int link_state_id;
		unsigned int adv_router;
		unsigned int lsa_sequence;
		unsigned short lsa_checksum;
		unsigned short length;
	     		printf("Age \tOptions Type \tID \t\tadv router \tsequence \tlength\n");
	     		for (auto i = Lsaheader.begin(); i != Lsaheader.end(); ++i) 
				{
				struct sockaddr_in advertiser,Link_state_id;
				memset(&advertiser, 0, sizeof(advertiser));
				advertiser.sin_addr.s_addr = (unsigned int)i->adv_router;
				memset(&Link_state_id, 0, sizeof(Link_state_id));
				Link_state_id.sin_addr.s_addr = (unsigned int)i->link_state_id;

				printf("%i \t%x \t%i \t%s \t%s \t%x \t%i \n",ntohs(i->lsa_age),i->options,i->lsa_type ,inet_ntoa(Link_state_id.sin_addr), inet_ntoa(advertiser.sin_addr),ntohl(i->lsa_sequence),ntohs(i->length));//why it does not work
				
				}
     		}
     		else if(strstr(input, "ping")!=NULL)  			
     			{
     			vector<string> out;
     			string in= input;
     			tokens->tokenize(in,out);
     			for (auto &s: out) 
     				{
				cout << s<<"\n";
				}
			out.clear();
     			}
     		else if(strstr(input, "interfaces")!=NULL)  			
     			{
     			vector<string> out;
     			string in= input;
     			tokens->tokenize(in,out);
     			for (auto &s: out) 
     				{
				cout << s<<"\n";
				}
			interfaces();
			out.clear();
     			}	
        	// Add input to history.
        	add_history(input);
	free(input);
    }
    return 0;
		
 }
 
void startCLI() 
{

    std::thread t(cli);
    t.detach();
}
