#include <winsock2.h>
#include <windows.h>
#include "FLProgModbusBridge.h"
#include "BridgeModbusRuntime.h"
#include <deque>
#include <cstdio>
#include <cassert>
#include <cstring>
struct Uart {std::deque<uint8_t> rx;Uart*other=nullptr;int available(){return rx.size();}int read(){int n=rx.front();rx.pop_front();return n;}int availableForWrite(){return 7;}size_t write(const uint8_t*p,size_t n){if(n>3)n=3;for(size_t i=0;i<n;i++)other->rx.push_back(p[i]);return n;}};
struct Tcp {SOCKET s=INVALID_SOCKET;uint32_t epoch=0;uint32_t generation(){return epoch;}bool connected(){if(s==INVALID_SOCKET)return false;char c;int n=recv(s,&c,1,MSG_PEEK);if(n==0||(n<0&&WSAGetLastError()!=WSAEWOULDBLOCK)){stop();return false;}return true;}int available(){u_long n=0;if(s!=INVALID_SOCKET)ioctlsocket(s,FIONREAD,&n);return n;}int read(){char c;return recv(s,&c,1,0)==1?(uint8_t)c:-1;}int availableForWrite(){return connected()?7:0;}size_t write(const uint8_t*p,size_t n){if(n>3)n=3;int done=send(s,(const char*)p,(int)n,0);return done>0?done:0;}void stop(){if(s!=INVALID_SOCKET)closesocket(s);s=INVALID_SOCKET;++epoch;}};
static bool writes=false;static unsigned commands=0;
static bool policy(uint8_t,uint16_t,uint16_t,const uint8_t*,uint16_t){if(!writes)return false;++commands;return true;}
int main(int argc,char**argv){
 WSADATA data;assert(!WSAStartup(MAKEWORD(2,2),&data));writes=argc>1&&!strcmp(argv[1],"--allow-writes");SOCKET listener=socket(AF_INET,SOCK_STREAM,0);assert(listener!=INVALID_SOCKET);sockaddr_in addr{};addr.sin_family=AF_INET;addr.sin_addr.s_addr=htonl(INADDR_LOOPBACK);assert(!bind(listener,(sockaddr*)&addr,sizeof(addr)));assert(!listen(listener,1));int len=sizeof(addr);getsockname(listener,(sockaddr*)&addr,&len);u_long nonblock=1;ioctlsocket(listener,FIONBIO,&nonblock);
 printf("{\"host\":\"127.0.0.1\",\"port\":%u,\"hardware\":false,\"writesEnabled\":%s}\n",ntohs(addr.sin_port),writes?"true":"false");fflush(stdout);
 uint8_t coils[250]{},discrete[250]{};uint16_t holding[125]{},input[125]{};holding[0]=1234;coils[0]=0x55;
 flprog_bridge::Server server("{\"model\":\"native-tcp-modbus\"}");FLProgModbusBridge service(1,{coils,2000,discrete,2000,holding,125,input,125},policy);assert(service.attach(server));
 Uart a,b;a.other=&b;b.other=&a;FLProgReadClient web;FLProgBridgeModbusRuntime runtime;Tcp tcp;uint64_t nonce=100;
 for(;;){uint32_t now=GetTickCount();input[124]=(uint16_t)commands;
  if(!tcp.connected()){runtime.stop();SOCKET s=accept(listener,nullptr,nullptr);if(s!=INVALID_SOCKET){ioctlsocket(s,FIONBIO,&nonblock);int noDelay=1;setsockopt(s,IPPROTO_TCP,TCP_NODELAY,(char*)&noDelay,sizeof(noDelay));tcp.s=s;++tcp.epoch;++nonce;}Sleep(0);continue;}
  runtime.pool(tcp,a,web,now,true,false,nonce);server.pool(b,now,7);Sleep(0);
 }
}
