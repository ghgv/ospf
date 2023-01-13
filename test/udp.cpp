
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netdb.h>
#include <stdio.h>
#include <unistd.h>
#include <arpa/inet.h>
#define TFTP_PORT       8081      /* tftp's well-known port number */
#define BSIZE           10     /* size of our data buffer */


int main(int argc, char *argv[])
{
    int    sock;                        /* Socket descriptor */
    struct sockaddr_in server,client_addr;          /* Server's address  */
    struct hostent *host;               /* Server host info  */
    char   buffer[BSIZE], *p;
    int    count, server_len;
    int    client_struct_len=sizeof(client_addr); 

/*    if (argc != 3) 
        {
        fprintf(stderr, "usage: %s hostname filename\n", argv[0]);
        exit(1);
        }*/
    struct timeval timeout;
    timeout.tv_sec = 10;
    timeout.tv_usec = 0;
/*    if (setsockopt (sockfd, SOL_SOCKET, SO_SNDTIMEO, &timeout,
                sizeof timeout) < 0)
        error("setsockopt failed\n");*/
    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if(sock<0)
        {
        printf("Error while creating socket\n");
        return -1;
        }
    printf("Socket created successfully\n");
    if (setsockopt (sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof timeout))
        printf("setsockopt failed\n");
   /* host = gethostbyname(argv[1]);
       if (host == NULL) {
        fprintf(stderr, "unknown host: %s\n", argv[1]);
       exit(2);
    }*/
    server.sin_family      = AF_INET;
    server.sin_port        = htons(TFTP_PORT);
    server.sin_addr.s_addr = inet_addr("192.168.2.131");

    client_addr.sin_family      = AF_INET;
    client_addr.sin_port        = htons(TFTP_PORT);
    client_addr.sin_addr.s_addr = inet_addr("192.168.2.22");
   // client_addr.sin_addr.s_addr = inet_addr("186.155.39.42");


    char message="M";
    *(char *)buffer = message;
    if(bind(sock, (struct sockaddr*)&server, sizeof(server)) < 0)
        {
        printf("Couldn't bind to the port\n");
        return -1;
        }
    printf("Binding done!\n");

//    count = sendto(sock, buffer,1 , 0,(struct sockaddr *)&client_addr, sizeof client_addr);
int    k=0x48;

    do {
        server_len = sizeof server;
        count = recvfrom(sock, buffer, BSIZE, 0, (struct sockaddr *)&client_addr, &client_struct_len);
        if(count==-1)
		{
                printf("No received\n");
		}
        else  {
                printf("Received message from IP: %s and port: %i: ", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));
                putc(*buffer,stdout);
                printf("\n");
                }
        printf("Message to send:\n");
	//scanf("%d",buffer);
    fgets(buffer, sizeof buffer, stdin);
//        message=getc(stdin);
    //    *(char *)buffer = message;
	//buffer[0]=k++;
//        write(1, buffer+4, count-4);
        sendto(sock, buffer, 1, 0, (struct sockaddr *)&client_addr, sizeof client_addr);
	
    } while (1);

        return 0;
}


