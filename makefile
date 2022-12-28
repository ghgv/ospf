# Makefile for Writing Make Files Example
 
# *****************************************************
# Variables to control Makefile operation
 
CC = g++
CFLAGS = -Wall -g -fpermissive  -fconcepts -O
 
ospfd: main.o ospf.o cli.o
	$(CC) $(CFLAGS) main.o ospf.o cli.o -o ospfd -lpthread -lreadline

main.o: main.cpp
	$(CC) $(CFLAGS) -c main.cpp

ospf.o: ospf.cpp 
	$(CC) $(CFLAGS) -c ospf.cpp
	

cli.o: cli.cpp
	$(CC) $(CFLAGS) -c cli.cpp 

clean:
	rm *.o ospfd
	
#//gcc  -O -o testne2000 testne2000.c  arp.c nic.c ip.c icmp.c tcp.c commands.c timer.c ./sys/socket.c ./sys/mbuf.c -w -Wincompatible-pointer-types -lpthread
