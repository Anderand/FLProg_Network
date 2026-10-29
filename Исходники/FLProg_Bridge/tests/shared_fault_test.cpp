#include "FLProgTcpBridge.h"
#include "BridgeTcpProxy.h"
#include <deque>
#include <vector>
#include <cassert>
#include <cstdio>
struct Fault{int side=0,operation=0;bool corrupt=false,armed=false,fired=false;};
struct Port{std::deque<uint8_t>rx;std::vector<uint8_t>frame;Port*other=nullptr;Fault*f=nullptr;int side=0;
 int available(){return rx.size();}int read(){int b=rx.front();rx.pop_front();return b;}int availableForWrite(){return 7;}
 size_t write(const uint8_t*p,size_t n){if(n>3)n=3;for(size_t i=0;i<n;++i){if(p[i]){frame.push_back(p[i]);assert(frame.size()<=280);continue;}bool fault=false;
  if(!frame.empty()){auto raw=frame;uint16_t size=flprog_bridge::decode(raw.data(),raw.size());fault=f->armed&&!f->fired&&f->side==side&&size>=22&&raw[1]==5&&raw[2]==f->operation;
   // NEXT response: affect only a delivered write job, not an idle poll.
   if(fault&&side==1&&f->operation==1)fault=size>24&&raw[flprog_bridge::HeaderSize+5]==2;
  }
  if(fault){f->fired=true;if(f->corrupt){frame[frame.size()/2]^=1;for(auto b:frame)other->rx.push_back(b);other->rx.push_back(0);}}
  else{for(auto b:frame)other->rx.push_back(b);other->rx.push_back(0);}frame.clear();
 }return n;}
};
struct Socket{bool live=false;unsigned writes=0,opens=0;void stop(){live=false;}void open(const char*,uint16_t){live=true;++opens;}bool connected(){return live;}bool failed(){return false;}int available(){return 0;}int read(){return -1;}size_t write(const uint8_t*,size_t n){++writes;return n;}};
int main(){using namespace flprog_bridge;unsigned cases=0;
 for(int scenario=0;scenario<7;++scenario){Server server("{}");FLProgTcpBridge plc;assert(plc.attach(server));assert(server.add(1,[](void*,uint8_t op,const uint8_t*,uint16_t,uint8_t*out,uint16_t&n){if(op!=1)return BadRequest;out[0]=1;putLE(out+1,42,4);n=5;return Ok;},nullptr));
  Fault fault;Port a,b;a.other=&b;b.other=&a;a.f=b.f=&fault;a.side=0;b.side=1;
  Socket socket;FLProgReadClient web;FLProgBridgeTcpProxy esp;FLProgBridgeSharedSession session;web.bindSession(session);esp.bindSession(session);uint32_t now=1;unsigned reads=0;bool pending=false;
  auto tick=[&](){if(pending&&!web.busy()){if(web.state()==FLProgReadClient::Done){assert(web.size()==5&&getLE(web.result()+1,4)==42);++reads;}pending=false;}if(!pending)pending=web.read(101,now);
   if(web.busy()&&!esp.ownsUart()){esp.pool(socket,a,web,now,true,false,now+999);web.pool(a,now,7);}else esp.pool(socket,a,web,now,true,false,now+999);server.pool(b,now,7);plc.pool(now);++now;};
  assert(plc.open("broker.test",1883,now));for(int i=0;i<3000&&plc.busy();++i)tick();assert(plc.state()==FLProgTcpBridge::Done);for(int i=0;i<200;++i)tick();
  fault.side=scenario==0||scenario==2?0:1;fault.operation=scenario==0||scenario==1||scenario==4?1:2;fault.corrupt=scenario==4||scenario==5;fault.armed=scenario!=6;
  uint8_t data[]={1,2,3,4,5};assert(plc.write(data,5,now));bool linkLost=false;
  for(int i=0;i<12500;++i){tick();if(scenario==6&&!linkLost&&socket.writes){esp.stop(socket);web.cancel();linkLost=true;}}
  assert(scenario==6?linkLost:fault.fired);unsigned expected=scenario==0||scenario==1||scenario==4?0:1;assert(socket.writes==expected&&!socket.live&&!plc.connected());
  unsigned before=socket.writes;fault.armed=false;assert(plc.open("broker.test",1883,now));for(int i=0;i<3000&&plc.busy();++i)tick();assert(plc.state()==FLProgTcpBridge::Done&&socket.live);for(int i=0;i<300;++i)tick();assert(socket.writes==before&&reads>0);++cases;
 }
 printf("PASS shared faults: %u scenarios NEXT request/response, RESULT, ACK, CRC corruption, link loss; writes0-or1, no replay after reopen, web recovers\n",cases);
}
