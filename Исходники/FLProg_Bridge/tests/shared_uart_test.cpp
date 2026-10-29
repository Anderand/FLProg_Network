#include "FLProgTcpBridge.h"
#include "BridgeTcpProxy.h"
#include <deque>
#include <vector>
#include <cassert>
#include <cstdio>
struct Port{std::deque<uint8_t>rx;Port*other=nullptr;int available(){return rx.size();}int read(){int b=rx.front();rx.pop_front();return b;}int availableForWrite(){return 7;}size_t write(const uint8_t*p,size_t n){if(n>5)n=5;for(size_t i=0;i<n;++i)other->rx.push_back(p[i]);return n;}};
struct Socket{bool live=false;unsigned opens=0,writes=0;void stop(){live=false;}void open(const char*,uint16_t){live=true;++opens;}bool connected(){return live;}bool failed(){return false;}int available(){return 0;}int read(){return -1;}size_t write(const uint8_t*,size_t n){if(n>7)n=7;writes+=n;return n;}};
int main(){using namespace flprog_bridge;Server server("{}");FLProgTcpBridge plc;assert(plc.attach(server));
 assert(server.add(1,[](void*,uint8_t op,const uint8_t*d,uint16_t n,uint8_t*out,uint16_t&size){if(op!=1||n!=1||d[0]!=101)return BadRequest;out[0]=1;putLE(out+1,42,4);size=5;return Ok;},nullptr));
 assert(server.add(4,[](void*,uint8_t op,const uint8_t*d,uint16_t n,uint8_t*out,uint16_t&size){if(op!=2||n!=6)return BadRequest;uint16_t count=getLE(d+4,2);if(count>224)return BadRequest;memcpy(out,d,4);for(uint16_t i=0;i<count;++i)out[4+i]=(uint8_t)(getLE(d,4)+i);size=count+4;return Ok;},nullptr));
 Port a,b;a.other=&b;b.other=&a;Socket socket;FLProgReadClient web;FLProgBridgeTcpProxy esp;FLProgBridgeSharedSession shared;web.bindSession(shared);esp.bindSession(shared);uint32_t now=1;unsigned reads=0;bool seen=false;
 auto tick=[&](){if(web.busy()&&!esp.ownsUart()){esp.pool(socket,a,web,now,true,false,now+123);web.pool(a,now,7);}else esp.pool(socket,a,web,now,true,false,now+123);server.pool(b,now,7);plc.pool(now);++now;};
 auto readTick=[&](){if(!seen&&web.state()==FLProgReadClient::Done&&web.size()==5){seen=true;assert(getLE(web.result()+1,4)==42);++reads;}if(!web.busy()&&web.read(101,now))seen=false;tick();};
 assert(plc.open("broker.test",1883,now));for(int i=0;i<3000&&plc.busy();++i)readTick();assert(plc.state()==FLProgTcpBridge::Done&&socket.live&&reads>0);
 // Repeated independent network writes and web reads share one sequence/session.
 uint8_t payload[220]{};for(int j=0;j<100;++j){assert(plc.write(payload,220,now));for(int i=0;i<3000&&plc.busy();++i)readTick();assert(plc.state()==FLProgTcpBridge::Done&&getLE(plc.result(),2)==7&&socket.live&&socket.opens==1);}
 while(web.busy())tick();const uint8_t*result=web.result();assert(web.state()==FLProgReadClient::Done);std::vector<uint8_t>snapshot(result,result+web.size());for(int i=0;i<100;++i)tick();assert(snapshot==std::vector<uint8_t>(web.result(),web.result()+web.size()));
 // Full-sized Flash chunks can be requested even if proxy established HELLO.
 while(!web.resourceChunk(0,224,now))tick();while(web.busy())tick();assert(web.state()==FLProgReadClient::Done&&web.size()==228);for(int i=0;i<224;++i)assert(web.result()[4+i]==(uint8_t)i);assert(socket.live&&socket.opens==1);
 assert(shared.sequence>200);
 uint64_t oldSession=shared.session;uint32_t oldEpoch=shared.epoch;while(!web.hello(888,now))tick();while(web.busy())tick();assert(shared.session==oldSession&&shared.epoch==oldEpoch&&socket.live);
 // A deliberate new HELLO closes the old TCP, never carries an old command over.
 web.invalidateSession();while(!web.hello(999,now))tick();while(web.busy())tick();for(int i=0;i<100;++i)tick();assert(!socket.live&&!plc.connected());
 assert(shared.sequence>0&&shared.hello&&!web.busy());printf("PASS shared UART: web reads=%u, TCP writes100, chunk224, one HELLO/socket, independent results, new-session close; context=%zu\n",reads,sizeof(shared));
}
