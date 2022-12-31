#ifndef TRANSMITTER_H
#define TRANSMITTER_H

#define ETHSIZE         14
#define IPHSIZE         20
#define TCPHSIZE        20

typedef unsigned char  BYTE;             /* 8-bit   */
typedef unsigned short BYTEx2;           /* 16-bit  */
typedef unsigned long  BYTEx4;           /* 32-bit  */

class transmitter{
	public:
		transmitter(char *);
		transmitter();
		int c_socket(char *);
		static int tx();
		
		int transmit(int lenght, unsigned char *buffer);


};

unsigned short in_cksum(unsigned short *ptr, int nbytes);

#endif
