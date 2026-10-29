#include <cassert>
#include <cstdio>
#include <deque>
#include <vector>
#include <cstring>
#include "BridgeHttpReadJob.h"
struct Port {
    std::deque<uint8_t> rx;Port *other=nullptr;int capacity=3,partial=2;size_t reads=0,writes=0;
    int available(){return (int)rx.size();}
    int read(){if(rx.empty())return -1;int n=rx.front();rx.pop_front();++reads;return n;}
    int availableForWrite(){return capacity;}
    size_t write(const uint8_t *data,size_t n){if(n>(size_t)partial)n=partial;for(size_t i=0;i<n;++i)other->rx.push_back(data[i]);writes+=n;return n;}
};
static int commandCalls=0;
static flprog_bridge::Status channel(void*,uint8_t op,const uint8_t *data,uint16_t len,uint8_t*out,uint16_t&size){
    if(op==3){++commandCalls;return flprog_bridge::Denied;}
    if(len!=1 || data[0]!=101)return flprog_bridge::BadRequest;
    if(op==1){out[0]=1;flprog_bridge::putLE(out+1,25,4);size=5;return flprog_bridge::Ok;}
    if(op==2){out[0]=101;out[1]=1;out[2]=2;memcpy(out+3,"setpoint",8);size=11;return flprog_bridge::Ok;}
    return flprog_bridge::Unsupported;
}
static void run(FLProgReadClient &c,flprog_bridge::Server &server,Port&a,Port&b,uint32_t&now){
    for(int i=0;i<1000 && c.busy();++i){
        size_t r=a.reads,w=a.writes;c.pool(a,now,7);assert(a.reads-r<=7&&a.writes-w<=7);
        server.pool(b,now,5);++now;
    }
    assert(!c.busy());
}
int main(){
    Port a,b;a.other=&b;b.other=&a;uint32_t now=0;
    flprog_bridge::Server server("{\"projectId\":\"native-read-test\"}");assert(server.add(1,channel,nullptr));
    FLProgHttpReadJob job;auto &c=job.client;
    assert(!c.read(101,now));assert(job.start(2,101,now,42,false)==409);
    assert(job.start(7,101,now,42,false)==400);assert(job.start(1,101,now,42,true)==409);assert(job.ticket==0);
    assert(job.start(1,0,now,42,false)==202);assert(job.start(2,101,now,42,false)==409);
    run(c,server,a,b,now);assert(c.state()==FLProgReadClient::Done&&c.hasSession()&&c.size()>10&&c.result()[0]=='{');
    assert(job.start(2,101,now,42,false)==202);run(c,server,a,b,now);
    assert(c.state()==FLProgReadClient::Done&&c.size()==5&&c.result()[0]==1&&flprog_bridge::getLE(c.result()+1,4)==25);
    assert(job.start(3,101,now,42,false)==202);run(c,server,a,b,now);assert(c.size()==11&&c.result()[0]==101);
    assert(job.start(2,102,now,42,false)==202);run(c,server,a,b,now);assert(c.state()==FLProgReadClient::PlcError&&c.status()==1);
    // Corrupt + overlong frames are discarded; a following correct response is accepted.
    a.capacity=a.partial=b.capacity=b.partial=64;
    assert(job.start(2,101,now,42,false)==202);c.pool(a,now,64);server.pool(b,now,64);server.pool(b,now,64);
    std::vector<uint8_t> good(a.rx.begin(),a.rx.end());assert(good.size()>24);a.rx.clear();
    for(int i=0;i<300;++i)a.rx.push_back(2);a.rx.push_back(0);
    auto corrupt=good;corrupt[8]^=0x40;for(auto v:corrupt)a.rx.push_back(v);for(auto v:good)a.rx.push_back(v);
    run(c,server,a,b,now);assert(c.state()==FLProgReadClient::Done&&c.badFrames()>=2);
    auto sent=a.writes;for(int i=0;i<100;++i)c.pool(a,now++,64);assert(a.writes==sent);
    // Deadline wraps with millis; zero room never waits and no stale request resumes later.
    FLProgReadClient stalled;Port x,y;x.other=&y;y.other=&x;x.capacity=0;uint32_t start=0xfffffff0UL;
    assert(stalled.hello(12,start));stalled.pool(x,start);stalled.pool(x,start+1500u);
    assert(stalled.state()==FLProgReadClient::Timeout&&!stalled.hasSession()&&x.writes==0);
    x.capacity=64;stalled.pool(x,start+1501u);assert(x.writes==0);
    assert(stalled.hello(13,5));stalled.cancel();assert(stalled.state()==FLProgReadClient::Cancelled);stalled.pool(x,6);assert(x.writes==0);
    // Protocol session error invalidates HTTP's session without replaying the read.
    server.resetTransport();assert(job.start(2,101,now,42,false)==202);run(c,server,a,b,now);assert(c.status()==3&&!c.hasSession());
    assert(job.start(2,101,now,42,false)==409);assert(job.start(1,0,now,99,false)==202);run(c,server,a,b,now);assert(c.hasSession());
    c.invalidateSession();assert(!c.hasSession());assert(commandCalls==0);
    printf("PASS: real C++ server/client, short writes, budgets, read/meta, CRC/overflow, deadline/wrap, cancel, fresh session, TCP arbitration, no commands/replay; client=%zu job=%zu bytes\n",sizeof(c),sizeof(job));
}
