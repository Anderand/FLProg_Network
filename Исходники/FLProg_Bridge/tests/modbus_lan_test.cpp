#include "FLProgModbusBridge.h"
#include "BridgeModbusTcp.h"
#include "BridgeNetworkConfig.h"
#include <cassert>
#include <deque>
#include <vector>
#include <cstdio>
struct Port{std::deque<uint8_t>rx;std::vector<uint8_t>out;Port*other=nullptr;bool live=true;size_t writes=0;int available(){return rx.size();}int read(){if(rx.empty())return -1;int v=rx.front();rx.pop_front();return v;}int availableForWrite(){return 7;}size_t write(const uint8_t*p,size_t n){if(n>3)n=3;writes+=n;for(size_t i=0;i<n;++i){if(other)other->rx.push_back(p[i]);else out.push_back(p[i]);}return n;}void stop(){live=false;}};
static bool permit=true;static int policyCalls=0;
static bool policy(uint8_t,uint16_t,uint16_t,const uint8_t*,uint16_t){++policyCalls;return permit;}
int main(){
 uint8_t coils[250]{},discrete[250]{};uint16_t holding[125]{},input[125]{};holding[0]=0x1234;input[0]=0xabcd;coils[0]=0x55;discrete[0]=0xaa;
 flprog_bridge::Server server("{\"model\":\"modbus-native\"}");
 server.add(1,[](void*,uint8_t op,const uint8_t*d,uint16_t n,uint8_t*out,uint16_t&size){if(op!=1||n!=1||d[0]!=101)return flprog_bridge::BadRequest;out[0]=1;flprog_bridge::putLE(out+1,25,4);size=5;return flprog_bridge::Ok;},nullptr);
FLProgModbusBridge svc(1,{coils,2000,discrete,2000,holding,125,input,125},policy);assert(svc.attach(server));
 Port uart,plc;uart.other=&plc;plc.other=&uart;FLProgModbusClient client;FLProgModbusTcpSession gateway(client);uint32_t now=0;uint16_t tid=0;
 auto request=[&](std::vector<uint8_t> pdu,bool free=true,uint8_t unit=1){Port tcp;gateway.begin(now);std::vector<uint8_t>adu={(uint8_t)(++tid>>8),(uint8_t)tid,0,0,(uint8_t)((pdu.size()+1)>>8),(uint8_t)(pdu.size()+1),unit};adu.insert(adu.end(),pdu.begin(),pdu.end());for(auto b:adu)tcp.rx.push_back(b);
  for(int i=0;i<2000&&(tcp.out.size()<6||tcp.out.size()<6+((tcp.out[4]<<8)|tcp.out[5]));++i){gateway.pool(tcp,uart,now,free,(uint64_t)now+43);server.pool(plc,now,7);++now;}
  assert(tcp.live&&tcp.out.size()>=9&&tcp.out[0]==adu[0]&&tcp.out[1]==adu[1]);return std::vector<uint8_t>(tcp.out.begin()+7,tcp.out.end());};
 auto r=request({3,0,0,0,1});assert((r==std::vector<uint8_t>{3,2,0x12,0x34}));
 r=request({4,0,0,0,1});assert((r==std::vector<uint8_t>{4,2,0xab,0xcd}));
 r=request({1,0,0,0,8});assert((r==std::vector<uint8_t>{1,1,0x55}));r=request({2,0,0,0,8});assert(r[2]==0xaa);
 r=request({6,0,0,0x45,0x67});assert(holding[0]==0x4567&&r.size()==5);
 r=request({5,0,0,0xff,0});assert((coils[0]&1));
 r=request({16,0,0,0,2,4,0,7,0,8});assert(holding[0]==7&&holding[1]==8);
 r=request({15,0,0,0,9,2,0x5a,1});assert(coils[0]==0x5a&&(coils[1]&1));
 r=request({1,0,0,7,0xd0});assert(r.size()==252&&r[1]==250);
 coils[249]=0xc3;std::vector<uint8_t> bits={15,0,0,7,0xb0,246};bits.resize(252,0xaa);r=request(bits);assert(coils[245]==0xaa&&coils[249]==0xc3);
 r=request({3,0,0,0,125});assert(r.size()==252&&r[1]==250);
 std::vector<uint8_t> large={16,0,0,0,123,246};for(int i=0;i<123;++i){large.push_back(0);large.push_back(i);}r=request(large);assert(holding[122]==122);
 r=request({3,0xff,0xff,0,2});assert(r[0]==0x83&&r[1]==2);
 r=request({3,0,0,0,126});assert(r[1]==3);
 r=request({5,0,0,0x12,0x34});assert(r[1]==3);
 int before=policyCalls;r=request({16,0,0,0,2,2,0,9});assert(r[1]==3&&policyCalls==before&&holding[0]==0);
 permit=false;r=request({6,0,0,0,99});assert(r[1]==1&&holding[0]==0);permit=true;
 r=request({3,0,0,0,1},false);assert(r[0]==0x83&&r[1]==6);
 r=request({3,0,0,0,1},true,2);assert(r[1]==11);
 r=request({99});assert(r[1]==1);
 // Same UART/server, actual WebUI and Modbus clients: no interleaving/replay.
 FLProgReadClient web;auto runWeb=[&](){for(int i=0;i<1000&&web.busy();++i){web.pool(uart,now,64);server.pool(plc,now,64);++now;}};
 assert(web.hello((uint64_t)now+200,now));runWeb();assert(web.state()==FLProgReadClient::Done);
 assert(web.read(101,now));size_t atWrites=uart.writes;r=request({3,0,0,0,1},false);assert(r[1]==6&&uart.writes==atWrites);runWeb();assert(web.state()==FLProgReadClient::Done&&flprog_bridge::getLE(web.result()+1,4)==25);
 r=request({3,0,0,0,1});assert(r[0]==3);assert(web.read(101,now));runWeb();assert(web.status()==3&&!web.hasSession());assert(web.hello((uint64_t)now+201,now));runWeb();assert(web.read(101,now));runWeb();assert(web.state()==FLProgReadClient::Done);
 // Modbus also refreshes its invalidated session before the next independent request.
 client.invalidateSession();
 // Invalid MBAP closes without UART traffic.
 Port bad;for(auto b:std::vector<uint8_t>{0,1,0,1,0,6,1,3,0,0,0,1})bad.rx.push_back(b);gateway.begin(now);size_t bytes=uart.writes;gateway.pool(bad,uart,now,true,(uint64_t)now+43);assert(!bad.live&&uart.writes==bytes);
 // Lost ACK after a write: one policy call, no retransmit, explicit timeout exception.
 Port lost;for(auto b:std::vector<uint8_t>{0,9,0,0,0,6,1,6,0,0,0,77})lost.rx.push_back(b);gateway.begin(now);before=policyCalls;
 for(int i=0;i<1000&&policyCalls==before;++i){gateway.pool(lost,uart,now,true,(uint64_t)now+43);server.pool(plc,now,64);++now;}
 assert(holding[0]==77&&policyCalls==before+1);uart.rx.clear();size_t sent=uart.writes;now+=1500;
 for(int i=0;i<50;++i){gateway.pool(lost,uart,now,true,(uint64_t)now+43);server.pool(plc,now,64);++now;}
 assert(uart.writes==sent&&policyCalls==before+1&&lost.out.size()==9&&lost.out[8]==11);
 // A CRC-valid but malformed PLC response is never forwarded as successful Modbus.
 {flprog_bridge::Server broken("{}");broken.add(2,[](void*,uint8_t,const uint8_t*,uint16_t,uint8_t*out,uint16_t&n){out[0]=1;out[1]=3;out[2]=4;out[3]=0;out[4]=1;n=5;return flprog_bridge::Ok;},nullptr);
  FLProgModbusClient c;FLProgModbusTcpSession g(c);Port x,y,t;x.other=&y;y.other=&x;for(auto b:std::vector<uint8_t>{0,1,0,0,0,6,1,3,0,0,0,1})t.rx.push_back(b);g.begin(now);
  for(int i=0;i<1000&&t.out.size()<9;++i){g.pool(t,x,now,true,(uint64_t)now+100);broken.pool(y,now,64);++now;}assert(t.out.size()==9&&t.out[7]==0x83&&t.out[8]==11);
 }
 FLProgBridgeNetworkConfig config;assert(bridgeNetworkValid(config));config.uartRx=18;assert(!bridgeNetworkValid(config));config=FLProgBridgeNetworkConfig();config.kind=FLProgBridgeNetworkConfig::RmiiLan8720;assert(bridgeNetworkValid(config));config.uartTx=23;assert(!bridgeNetworkValid(config));config=FLProgBridgeNetworkConfig();config.kind=FLProgBridgeNetworkConfig::Wifi;assert(bridgeNetworkValid(config));
 printf("PASS Modbus 1/2/3/4/5/6/15/16, maxima, endian, atomic validation, policy, MBAP, UART busy, wrong unit, lostACK/no replay, WiFi/Wiznet/RMII configs; client=%zu gateway=%zu\n",sizeof(client),sizeof(gateway));
}
