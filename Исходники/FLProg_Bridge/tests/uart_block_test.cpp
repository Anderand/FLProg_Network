#include <deque>
#include <vector>
#include <cassert>
#include <cstdio>
#include "FLProgBridgeUartBlock.h"
using namespace flprog_bridge;
struct Backend {
 std::deque<uint8_t> input;std::vector<uint8_t> output;bool busy=false,startOk=true;int begins=0,ends=0,roomSize=3;unsigned reads=0,writes=0;
 bool valid(uint8_t n){return n==6;}bool occupied(uint8_t){return busy;}
 bool begin(uint8_t,uint32_t){++begins;busy=true;return startOk;}void end(uint8_t){++ends;busy=false;}
 int available(uint8_t){return input.size();}int read(uint8_t){if(input.empty())return -1;int b=input.front();input.pop_front();++reads;return b;}
 int room(uint8_t){return roomSize;}bool write(uint8_t,uint8_t b){if(!roomSize)return false;output.push_back(b);++writes;return true;}
};
void hello(Backend &io,uint64_t session,uint32_t seq=1){uint8_t raw[64]={1,0,1,0};putLE(raw+4,seq,4);putLE(raw+8,session,8);putLE(raw+16,10,2);memcpy(raw+18,"FLPBRIDGE1",10);putLE(raw+28,crc32(raw,28),4);uint8_t encoded[80];int n=encode(raw,32,encoded);io.input.insert(io.input.end(),encoded,encoded+n);}
int main(){
 Backend io;Server server("{\"projectId\":\"block-test\"}");UartBlock<Backend> b(io);
 b.pool(server,false,6,115200,64,0);assert(!b.ready() && io.begins==0 && io.ends==0);
 b.pool(server,true,9,115200,64,0);assert(b.fault()==1 && io.begins==0);
 b.pool(server,true,6,1199,64,0);assert(b.fault()==2 && io.begins==0);
 b.pool(server,true,6,115200,129,0);assert(b.fault()==3 && io.begins==0);
 io.busy=true;b.pool(server,true,6,115200,64,0);assert(b.fault()==5 && io.ends==0);io.busy=false;
 io.startOk=false;b.pool(server,true,6,115200,64,0);assert(b.fault()==4 && io.ends==1 && !io.busy);io.startOk=true;
 b.pool(server,true,6,115200,8,1);assert(b.ready() && !b.connected(server,1));
 hello(io,123);for(unsigned t=2;t<40;++t){auto r=io.reads,w=io.writes;b.pool(server,true,6,115200,8,t);assert(io.reads-r<=8 && io.writes-w<=8);}
 assert(b.connected(server,40) && server.currentSession()==123 && b.received()>0 && b.sent()>0);
 assert(!b.connected(server,4000));
 auto reads=io.reads;b.pool(server,true,5,115200,64,4001);assert(b.fault()==6 && io.reads==reads);
 b.pool(server,true,6,115200,64,4002);assert(b.ready());
 // TX back pressure never spins and resumes from the same cursor.
 io.output.clear();io.roomSize=0;hello(io,456);b.pool(server,true,6,115200,64,4003);assert(io.output.empty());
 b.pool(server,true,6,115200,64,4004);assert(io.output.empty());
 io.roomSize=1;for(unsigned t=4005;t<4020;++t)b.pool(server,true,6,115200,8,t);assert(!io.output.empty());
 b.pool(server,false,6,115200,64,4020);assert(!b.ready() && server.currentSession()==0 && io.ends==2);
 auto sent=b.sent();b.pool(server,true,6,115200,8,4021);assert(b.ready() && !b.connected(server,4021) && b.sent()==sent);
 // Bad frame counter persists across disable and does not establish a session.
 io.input.push_back(1);io.input.push_back(0);b.pool(server,true,6,115200,8,4022);assert(server.errors()==1 && !b.connected(server,4022));
 b.pool(server,false,6,115200,8,4023);assert(server.errors()==1);
 puts("PASS: validation, UART ownership, failed begin cleanup, bounded RX/TX, HELLO, heartbeat expiry, live change rejection, backpressure, disable/session reset, bad frames");
}
