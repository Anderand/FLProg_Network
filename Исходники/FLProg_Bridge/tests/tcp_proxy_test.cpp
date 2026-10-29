#include "FLProgTcpBridge.h"
#include "BridgeTcpProxy.h"
#include <deque>
#include <cassert>
#include <cstdio>
struct Port{std::deque<uint8_t>rx;Port*other=nullptr;bool drop=false;int available(){return rx.size();}int read(){int b=rx.front();rx.pop_front();return b;}int availableForWrite(){return 64;}size_t write(const uint8_t*p,size_t n){if(n>5)n=5;if(!drop)for(size_t i=0;i<n;++i)other->rx.push_back(p[i]);return n;}};
struct Socket{bool live=false;int opens=0,writes=0;void stop(){live=false;}void open(const char*h,uint16_t p){assert(!strcmp(h,"broker.test")&&p==1883);live=true;++opens;}bool connected(){return live;}bool failed(){return false;}int available(){return 0;}int read(){return -1;}size_t write(const uint8_t*,size_t n){++writes;return n;}};
int main(){flprog_bridge::Server server("{}");FLProgTcpBridge plc;assert(plc.attach(server));Port a,b;a.other=&b;b.other=&a;Socket socket;FLProgReadClient web;FLProgBridgeTcpProxy esp;uint32_t now=0xfffffff0UL;
 auto tick=[&](){esp.pool(socket,a,web,now,true,false,123+now);server.pool(b,now,64);plc.pool(now);++now;};
 auto finish=[&](){for(int i=0;i<3000&&plc.busy();++i)tick();assert(plc.state()==FLProgTcpBridge::Done);};
 assert(!plc.open("",1883,now)&&!plc.open("broker.test",0,now)&&!plc.read(1,now));
 assert(plc.open("broker.test",1883,now));assert(!plc.open("broker.test",1883,now));finish();assert(plc.connected()&&socket.opens==1);
 uint8_t bytes[]={1,2,3,4,5};assert(!plc.write(bytes,221,now)&&!plc.read(221,now));assert(plc.write(bytes,5,now));
 for(int i=0;i<2000&&!socket.writes;++i)tick();assert(socket.writes==1);b.drop=true;
 for(int i=0;i<1800;++i)tick();assert(socket.writes==1&&!socket.live);b.drop=false;
 // Returning communication cannot replay the write accepted before lost ACK.
 for(int i=0;i<2000;++i)tick();assert(socket.writes==1&&socket.opens==1);
 plc.cancel();assert(plc.open("broker.test",1883,now));finish();assert(socket.opens==2);
 assert(plc.write(bytes,5,now));esp.stop(socket);for(int i=0;i<11000;++i){plc.pool(now++);}assert(plc.state()==FLProgTcpBridge::Failed&&socket.writes==1);
 assert(plc.open("broker.test",1883,now));finish();server.resetTransport();plc.pool(now);assert(!plc.connected());
 esp.pool(socket,a,web,now,false,false,99);assert(!socket.live);
 printf("PASS TCP proxy bounds/busy, partial UART, lost RESULT ACK/no replay, deadline, PLC reset, link loss; PLC=%zu ESP=%zu\n",sizeof(plc),sizeof(esp));}
