#include "FLProgBridgeTcpClient.h"
#include "BridgeTcpProxy.h"
#include <deque>
#include <cassert>
#include <cstdio>
struct Port{std::deque<uint8_t>rx;Port*other=nullptr;int available(){return rx.size();}int read(){int b=rx.front();rx.pop_front();return b;}int availableForWrite(){return 7;}size_t write(const uint8_t*p,size_t n){if(n>3)n=3;for(size_t i=0;i<n;++i)other->rx.push_back(p[i]);return n;}};
struct Socket{std::deque<uint8_t>rx;bool live=false;void stop(){live=false;rx.clear();}void open(const char*,uint16_t){live=true;}bool connected(){return live;}bool failed(){return false;}int available(){return rx.size();}int read(){int b=rx.front();rx.pop_front();if(rx.empty())live=false;return b;}size_t write(const uint8_t*,size_t n){return n;}};
int main(){flprog_bridge::Server server("{}");FLProgTcpBridge service;assert(service.attach(server));FLProgBridgeTcpClient stream(service);Socket socket;Port a,b;a.other=&b;b.other=&a;FLProgReadClient web;FLProgBridgeTcpProxy esp;uint32_t now=1;
 auto tick=[&](){esp.pool(socket,a,web,now,true,false,now+123);server.pool(b,now,7);stream.pool(now);++now;};
 stream.pool(now);assert(stream.connect("server.test",1234));for(int i=0;i<2000&&!stream.connected();++i)tick();assert(stream.connected());
 for(auto c:{'t','a','i','l'})socket.rx.push_back(c);for(int i=0;i<2000&&!stream.available();++i)tick();assert(!socket.live&&stream.connected()&&!stream.canWrite()&&stream.available()==4);
 assert(stream.read()=='t');assert(stream.read()=='a');for(int i=0;i<100;++i)tick();assert(stream.connected()&&stream.available()==2);assert(stream.read()=='i');assert(stream.read()=='l');assert(!stream.connected()&&stream.available()==0);
 assert(stream.connect("server.test",1234));for(int i=0;i<2000&&!stream.connected();++i)tick();socket.rx.push_back('x');for(int i=0;i<2000&&!stream.available();++i)tick();assert(stream.available()==1);stream.stop();assert(!stream.connected()&&!stream.available());
 printf("PASS PLC TCP EOF: last bytes survive FIN, partial drain persists, EOF after drain, explicit stop discards RX\n");}
