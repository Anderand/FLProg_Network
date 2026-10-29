#include "FLProgBridgeTcpClient.h"
#include "BridgeTcpProxy.h"
#include <deque>
#include <vector>
#include <cassert>
#include <cstdio>
struct Port {
 std::deque<uint8_t> rx; Port* other=nullptr;
 int available(){return rx.size();} int read(){int b=rx.front();rx.pop_front();return b;}
 int availableForWrite(){return 7;}
 size_t write(const uint8_t*p,size_t n){if(n>3)n=3;for(size_t i=0;i<n;++i)other->rx.push_back(p[i]);return n;}
};
struct Socket {
 bool live=false; unsigned calls=0; std::vector<uint8_t> tx; std::deque<uint8_t> rx;
 void stop(){live=false;rx.clear();} void open(const char*,uint16_t){live=true;}
 bool connected(){return live;} bool failed(){return false;}
 int available(){return rx.size();} int read(){int b=rx.front();rx.pop_front();return b;}
 size_t write(const uint8_t*p,size_t n){++calls;if(calls%5==0)return 0;if(n>7)n=7;tx.insert(tx.end(),p,p+n);return n;}
};
int main(){
 flprog_bridge::Server server("{}"); FLProgTcpBridge service;assert(service.attach(server));
 FLProgBridgeTcpClient stream(service);Socket socket;Port a,b;a.other=&b;b.other=&a;
 FLProgReadClient web;FLProgBridgeTcpProxy esp;uint32_t now=0xfffff000U;
 auto tick=[&](){esp.pool(socket,a,web,now,true,false,123);server.pool(b,now,7);stream.pool(now);++now;};
 stream.pool(now);assert(stream.connect("test",1883));for(int i=0;i<2000&&!stream.connected();++i)tick();assert(stream.connected());
 const size_t count=65536;std::vector<uint8_t> source(count);for(size_t i=0;i<count;++i)source[i]=(uint8_t)(i*31+i/251);
 size_t queued=0;unsigned ticks=0;
 while(queued<count||stream.writePending()){
  if(!stream.writePending()&&queued<count){size_t n=stream.write(source.data()+queued,count-queued);assert(n&&n<=220);queued+=n;
   uint8_t other=99;assert(stream.write(&other,1)==0);}
  tick();assert(stream.canWrite());assert(++ticks<3000000);
 }
 assert(socket.tx==source);
 // A slow PLC consumer must leave its unread chunk intact and apply backpressure.
 for(auto byte:source)socket.rx.push_back(byte);
 for(int i=0;i<3000&&!stream.available();++i)tick();assert(stream.available()==220);
 auto left=socket.rx.size();for(int i=0;i<500;++i)tick();assert(socket.rx.size()==left&&stream.available()==220);
 size_t received=0;
 while(received<count){if(ticks%13==0&&stream.available()){assert(stream.read()==source[received]);++received;}tick();assert(++ticks<5000000);}
 assert(socket.rx.empty()&&stream.available()==0);
 printf("PASS backpressure: 65536 bytes each direction, partial/zero writes, slow RX, bounded220 buffers, millis wrap; ticks=%u writes=%u streamBytes=%zu\n",ticks,socket.calls,sizeof(stream));
}
