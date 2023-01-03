#include "interfaces.h"
#include <stdio.h>
#include <net/if.h>
#include <cerrno>
#include <string.h>

void interfaces()
{
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
	
}
