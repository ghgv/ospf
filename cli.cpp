#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <readline/readline.h>
#include <readline/history.h>
#include <thread>

extern bool DEBUG;
extern char input[50];

int cli()
{
	char* input, shell_prompt[100];
	// Configure readline to auto-complete paths when the tab key is hit.
	rl_bind_key('\t', rl_complete);

    	for(;;) {
        	// Create prompt string from user name and current working directory.
        	snprintf(shell_prompt, sizeof(shell_prompt), "%s# ","configuration" );
		//shell_prompt="configuration";
        	// Display prompt and read input (NB: input must be freed after use)...
        	input = readline(shell_prompt);
	
        	// Check for EOF.
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
     		
        	// Add input to history.
        	add_history(input);

        	// Do stuff...

        	// Free input.
        	free(input);
    }
    return 0;
		
 }
 
void startCLI() 
{

    std::thread t(cli);
    t.detach();
}
