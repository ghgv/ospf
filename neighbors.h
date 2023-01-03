#ifndef NEIGHBORS_H
#define NEIGHBORS_H

typedef struct Neighbor{
	unsigned int Neighbor_ID;
	unsigned char Priority;
	unsigned char *state="NULL";
	unsigned int dead_time;
	unsigned int addr;
	int State;
	int	interface_number;
} neighbor_t;


#endif
