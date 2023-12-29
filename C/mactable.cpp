#include "mactable.h"
#include <stdio.h>
#include <string>
#include <vector>
#include <cstring>

char line[500]; // Read with fgets().
char ip_address[500]; // Obviously more space than necessary, just illustrating here.
int hw_type;
int flags;
char mac_address[500];
char mask[500];
char device[500];

uint8_t hexdigit( char hex )
{
    return (hex <= '9') ? hex - '0' : toupper(hex) - 'A' + 10 ;
}

uint8_t hexbyte( const char* hex )
{
    return (hexdigit(*hex) << 4) | hexdigit(*(hex+1)) ;
}

unsigned char * scanner(char* ip, unsigned char * MAC )
{
    FILE *fp = fopen("/proc/net/arp", "r");
    unsigned char a[6]={0};
    fgets(line, sizeof(line), fp);    // Skip the first line (column headers).
    while(fgets(line, sizeof(line), fp))
    {
        
        sscanf(line, "%s 0x%x 0x%x %s %s %s\n",
            ip_address,
            &hw_type,
            &flags,
            mac_address,
            mask,
            device);
    //Mactable.MAC=mac_address;
    //Mactable.IP =ip_address
    //mactable.push_back(Mactable);
    //printf("%s %s \n",ip ,ip_address);
    if(strcmp(ip,ip_address)==0)
        {
            
            std::string linia(mac_address);
            unsigned char z,x,c,v,b,n;
            sscanf(linia.c_str(), "%02x:%02x:%02x:%02x:%02x:%02x", &z, &x, &c, &v, &b, &n);
            //printf("%02x:%02x:%02x:%02x:%02x:%02x\n",z,x,c,v,b,n);
            MAC[0]=z;
            MAC[1]=x;
            MAC[2]=c;
            MAC[3]=v;
            MAC[4]=b;
            MAC[5]=n;
            //00:0f:e2:dd:9e:2c
        //    memcpy(MAC,a,6);
        
        }    
    }

fclose(fp);
return 0; //(unsigned char *)&a;
}