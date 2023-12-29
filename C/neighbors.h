#ifndef NEIGHBORS_H
#define NEIGHBORS_H

typedef struct Neighbor{
	unsigned int Neighbor_ID;
	unsigned char Priority;
	unsigned char *state="NULL";
	unsigned int dead_time;
	unsigned int addr1;//outgoing IP
	int State;
	int	interface_number;
	unsigned int sequence;
} neighbor_t;


#endif
