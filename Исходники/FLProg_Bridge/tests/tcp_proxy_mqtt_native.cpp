#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include "FLProgBridgeTcpClient.h"
#include "BridgeTcpProxy.h"
#include <deque>
#include <vector>
#include <cassert>
#include <cstdio>
struct Port {std::deque<uint8_t>rx;Port*other=nullptr;int available(){return rx.size();}int read(){int b=rx.front();rx.pop_front();return b;}int availableForWrite(){return 11;}size_t write(const uint8_t*p,size_t n){if(n>7)n=7;for(size_t i=0;i<n;++i)other->rx.push_back(p[i]);return n;}};
struct Socket {
 SOCKET fd=INVALID_SOCKET;bool connecting=false,error=false;size_t writes=0;
 void stop(){if(fd!=INVALID_SOCKET)closesocket(fd);fd=INVALID_SOCKET;connecting=false;error=false;}
 void open(const char*h,uint16_t port){stop();addrinfo hints{},*info=nullptr;hints.ai_family=AF_INET;hints.ai_socktype=SOCK_STREAM;char p[8];snprintf(p,sizeof(p),"%u",port);if(getaddrinfo(h,p,&hints,&info)){error=true;return;}fd=socket(AF_INET,SOCK_STREAM,0);u_long mode=1;ioctlsocket(fd,FIONBIO,&mode);int r=::connect(fd,info->ai_addr,(int)info->ai_addrlen);connecting=r!=0;if(connecting&&WSAGetLastError()!=WSAEWOULDBLOCK)error=true;freeaddrinfo(info);}
 bool connected(){if(fd==INVALID_SOCKET||error)return false;if(connecting){fd_set w,e;FD_ZERO(&w);FD_ZERO(&e);FD_SET(fd,&w);FD_SET(fd,&e);timeval t{};select(0,nullptr,&w,&e,&t);if(FD_ISSET(fd,&e)){error=true;return false;}if(!FD_ISSET(fd,&w))return false;int status=0,n=sizeof(status);getsockopt(fd,SOL_SOCKET,SO_ERROR,(char*)&status,&n);if(status){error=true;return false;}connecting=false;}return true;}
 bool failed(){return error;}
 int available(){u_long n=0;if(fd!=INVALID_SOCKET)ioctlsocket(fd,FIONREAD,&n);return n;}
 int read(){uint8_t b;return recv(fd,(char*)&b,1,0)==1?b:-1;}
 size_t write(const uint8_t*p,size_t n){if(n>7)n=7;int sent=send(fd,(const char*)p,(int)n,0);if(sent<0){error=WSAGetLastError()!=WSAEWOULDBLOCK;return 0;}writes+=sent;return sent;}
};
static void str(std::vector<uint8_t>&v,const char*s){size_t n=strlen(s);v.push_back(n>>8);v.push_back(n);v.insert(v.end(),s,s+n);}
static std::vector<uint8_t> packet(uint8_t type,const std::vector<uint8_t>&data){std::vector<uint8_t>v{type};size_t n=data.size();do{uint8_t b=n%128;n/=128;v.push_back(b|(n?128:0));}while(n);v.insert(v.end(),data.begin(),data.end());return v;}
int main(int argc,char**argv){assert(argc==3);WSADATA data;assert(!WSAStartup(MAKEWORD(2,2),&data));
 flprog_bridge::Server server("{\"model\":\"PLC software stand\"}");FLProgTcpBridge plc;assert(plc.attach(server));FLProgBridgeTcpClient stream(plc);Port a,b;a.other=&b;b.other=&a;Socket socket;FLProgReadClient web;FLProgBridgeTcpProxy esp;
 auto tick=[&](){uint32_t now=GetTickCount();esp.pool(socket,a,web,now,true,false,123456);server.pool(b,now,11);stream.pool(now);Sleep(0);};
 stream.pool(GetTickCount());assert(stream.connect(argv[1],(uint16_t)atoi(argv[2])));uint32_t started=GetTickCount();while(!stream.connected()&&GetTickCount()-started<11000)tick();assert(stream.connected());
 auto send=[&](const std::vector<uint8_t>&v){size_t at=0;uint32_t start=GetTickCount();while(at<v.size()&&GetTickCount()-start<10000){at+=stream.write(v.data()+at,v.size()-at);tick();}assert(at==v.size());};
 auto receive=[&](size_t count){std::vector<uint8_t>v;uint32_t start=GetTickCount();while(v.size()<count&&GetTickCount()-start<10000){tick();while(stream.available()&&v.size()<count)v.push_back(stream.read());}assert(v.size()==count);return v;};
 // All MQTT configuration and framing here belong to the PLC side of the stand.
 std::vector<uint8_t>connect;str(connect,"MQTT");connect.insert(connect.end(),{4,0xc2,0,30});str(connect,"PLC-client");str(connect,"plc-user");str(connect,"test-only-password");send(packet(0x10,connect));assert(receive(4)==std::vector<uint8_t>({0x20,2,0,0}));
 std::vector<uint8_t>sub{0,7};str(sub,"plc/command");sub.push_back(0);send(packet(0x82,sub));assert(receive(5)==std::vector<uint8_t>({0x90,3,0,7,0}));
 std::vector<uint8_t>pub;str(pub,"plc/value");pub.insert(pub.end(),400,'A');send(packet(0x30,pub));auto incoming=receive(20);assert(incoming==packet(0x30,std::vector<uint8_t>{0,11,'p','l','c','/','c','o','m','m','a','n','d','o','n','!','!','!'}));
 stream.stop();for(int i=0;i<1000;++i)tick();assert(!stream.connected());printf("PASS real localhost MQTT CONNECT/auth/SUBSCRIBE/SUBACK/PUBLISH400/incoming/close via PLC service5 and actual ESP proxy; PLC=%zu ESP=%zu written=%zu\n",sizeof(plc),sizeof(esp),socket.writes);
}
