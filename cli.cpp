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

extern bool DEBUG;
extern char input[50];

extern vector<neighbor_t> Neighbor;


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
	     		printf("Neighbor ID \tPri \tState \tDead time \tAddress \tInterface\n");
	     		for (auto i = Neighbor.begin(); i != Neighbor.end(); ++i) 
				{
				struct sockaddr_in neighbor,address;
				memset(&neighbor, 0, sizeof(neighbor));
				neighbor.sin_addr.s_addr = (unsigned int)i->Neighbor_ID;
				memset(&address, 0, sizeof(address));
				address.sin_addr.s_addr = (unsigned int)i->addr;

				printf("%s \t%i \t%s \t%i \t\t%s \t%i \n",inet_ntoa(neighbor.sin_addr), i->Priority ,states_num[i->State] ,i->dead_time,inet_ntoa(address.sin_addr),i->interface_number);
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
