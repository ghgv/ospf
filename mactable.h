#ifndef ARP_SCAN
#define ARP_SCAN
#include <vector>

typedef struct MACTABLE
{
    unsigned int MAC;
    unsigned int IP;
} mactable_t;

unsigned char * scanner(char* ip,unsigned char * );

#endif