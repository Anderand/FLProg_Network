#include "FLProgModbusBridge.h"
#include "BridgeModbusRuntime.h"
#include <cassert>
#include <deque>
#include <vector>
#include <cstdio>
struct Port {
 std::deque<uint8_t>rx;std::vector<uint8_t>out;Port*other=nullptr;
 bool live=true;uint32_t epoch=1;size_t writes=0;
 bool connected(){return live;}uint32_t generation(){return epoch;}
 int available(){return rx.size();}int read(){if(rx.empty())return -1;int b=rx.front();rx.pop_front();return b;}
 int availableForWrite(){return 7;}
 size_t write(const uint8_t*p,size_t n){if(n>3)n=3;writes+=n;for(size_t i=0;i<n;++i)if(other)other->rx.push_back(p[i]);else out.push_back(p[i]);return n;}
 void stop(){live=false;++epoch;rx.clear();}
 void connect(){live=true;++epoch;out.clear();}
 void request(uint8_t fc=3,uint16_t value=1){out.clear();uint8_t b[]={0,1,0,0,0,6,1,fc,0,0,(uint8_t)(value>>8),(uint8_t)value};for(auto x:b)rx.push_back(x);}
};
int main(){
 uint16_t registers[2]={42,0};flprog_bridge::Server server("{}");
 FLProgModbusBridge service(1,{nullptr,0,nullptr,0,registers,2,nullptr,0});assert(service.attach(server));
 Port tcp,uart,plc;uart.other=&plc;plc.other=&uart;FLProgReadClient web;FLProgBridgeModbusRuntime runtime;uint32_t now=1;
 auto run=[&](){for(int i=0;i<2000&&(tcp.out.size()<6||tcp.out.size()<6+((tcp.out[4]<<8)|tcp.out[5]))&&tcp.live;++i){runtime.pool(tcp,uart,web,now,true,false,now+77);server.pool(plc,now,7);++now;}};
 tcp.request();run();assert(tcp.out.size()==11&&tcp.out[7]==3&&tcp.out[10]==42);
 // Defaults stay read-only; a TCP write is never implicit permission to write PLC.
 tcp.request(6,99);run();assert(tcp.out.size()==9&&tcp.out[7]==0x86&&tcp.out[8]==1&&registers[0]==42);
 // An active web transfer gets priority before even HELLO is sent.
 tcp.connect();tcp.request();size_t sent=uart.writes;runtime.pool(tcp,uart,web,now,true,true,123);assert(!tcp.live&&uart.writes==sent);
 // A disconnected or offline socket cannot carry a queued command after recovery.
 tcp.connect();tcp.request(6,100);runtime.pool(tcp,uart,web,now,false,false,124);assert(!tcp.live&&uart.writes==sent&&registers[0]==42);
 tcp.connect();tcp.request();run();assert(tcp.out.size()==11&&tcp.out[10]==42);
 // Disconnect halfway through UART HELLO, then reconnect: framing resynchronizes.
 tcp.connect();tcp.request();runtime.pool(tcp,uart,web,now,true,false,now+700);server.pool(plc,now,7);++now;
 tcp.stop();runtime.stop();tcp.connect();tcp.request();run();assert(tcp.out.size()==11&&tcp.out[10]==42);
 // Invalidate an established WebUI session when a new Modbus owner takes UART.
 tcp.stop();runtime.stop();assert(web.hello(now+999,now));
 for(int i=0;i<1000&&web.busy();++i){web.pool(uart,now,64);server.pool(plc,now,64);++now;}assert(web.hasSession());
 tcp.connect();tcp.request();runtime.pool(tcp,uart,web,now,true,false,now+1000);assert(!web.hasSession());run();assert(tcp.out.size()==11);
 // Idle connection is bounded, then WebUI can establish a fresh session.
 now+=3001;runtime.pool(tcp,uart,web,now,true,false,99);assert(!tcp.live);runtime.stop();
 assert(web.hello(now+888,now));for(int i=0;i<1000&&web.busy();++i){web.pool(uart,now,64);server.pool(plc,now,64);++now;}assert(web.hasSession());
 printf("PASS combined runtime: read, default read-only, WebUI priority, offline/no queue, reconnect, fresh HELLO, bounded idle; runtime=%zu\n",sizeof(runtime));
}
