#include <arpa/inet.h>
#include <assert.h>
#include <net/if.h>
#include <netinet/in.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <unistd.h>

int sockfd=-1;

void connect2(const char *const dst){

  sockfd=socket(AF_INET,SOCK_STREAM,0);
  assert(sockfd>=3);

  struct sockaddr_in sin={
    .sin_family=AF_INET,
    .sin_port=htons(80),
    .sin_addr={}
  };
  assert(1==inet_pton(AF_INET,dst,&(sin.sin_addr)));

  assert(0==connect(sockfd,(struct sockaddr*)(&sin),sizeof(struct sockaddr_in)));

}

void getsockname2(struct sockaddr_in *const sin){
  socklen_t addrlen=sizeof(struct sockaddr_in);
  assert(0==getsockname(sockfd,(struct sockaddr*)sin,&addrlen));
  assert(addrlen==sizeof(struct sockaddr_in));
}
void disconnect(){
  close(sockfd);
  sockfd=-1;
}

void addr2iface_ifconf(const struct in_addr *const sin_addr,int *const index,char *const name){

  struct ifconf ifc={
    ifc_len=0,
    ifc_req=NULL
  };

  int ioctlfd=socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP);
  assert(ioctlfd>=3);
  assert(0==ioctl(ioctlfd,SIOCGIFCONF,&ifc));

  const int sz=ifc.ifc_len;
  assert(sz%sizeof(struct ifreq)==0);
  const int n=sz/sizeof(struct ifreq);

  char buf[sz];
  bzero(buf,sz);
  ifc.ifc_buf=buf;
  assert(0==ioctl(ioctlfd,SIOCGIFCONF,&ifc));
  assert(
    ifc.ifc_len==sz &&
    (char*)ifc.ifc_req==buf
  );

  for(int i=0;i<n;++i)if(0==memcmp(
    &(((struct sockaddr_in*)(&(ifc.ifc_req[i].ifr_addr)))->sin_addr),
    sin_addr,
    sizeof(struct in_addr)
  )){
    *index=ifc.ifc_req[i].ifr_ifindex;
    assert(name==strncpy(name,ifc.ifc_req[i].ifr_name,IFNAMSIZ));
    return;
  }

  assert(0);

}

int main(int argc,const char *argv[]){

  assert(argc==2);
  assert(argv[1]&&strlen(argv[1]));
  //const char *const remoteaddr_s=argv[1];
   const char *const remoteaddr_s="192.168.0.1";

  connect2(remoteaddr_s);

  struct sockaddr_in ifaddr={};
  getsockname2(&ifaddr);

  disconnect();

  int index=0;
  char ifname[IFNAMSIZ]={};
  addr2iface_ifconf(&(ifaddr.sin_addr),&index,ifname);

  char ifaddr_s[INET_ADDRSTRLEN]={};
  assert(ifaddr_s==inet_ntop(AF_INET,&(ifaddr.sin_addr),ifaddr_s,INET_ADDRSTRLEN));

  printf("interface index   : %d\n",index);
  printf("interface name    : %s\n",ifname);
  printf("interface address : %s\n",ifaddr_s);
  printf("remote    address : %s\n",remoteaddr_s);
  // printf("#%d %s %s -> %s\n",
  //   index,
  //   ifname,
  //   ifaddr_s,
  //   remoteaddr_s
  // );

  return 0;

}
