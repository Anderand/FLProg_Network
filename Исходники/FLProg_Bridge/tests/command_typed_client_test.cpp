#include "http_read_native_adapter.h"
static int calls=0;
static flprog_bridge::Status service(void*,uint8_t op,const uint8_t *data,uint16_t len,uint8_t*,uint16_t&size){assert(op==3&&len<=65);++calls;size=0;return flprog_bridge::Ok;}
int main(){
 FLProgReadClient client;Port a,b;a.other=&b;b.other=&a;flprog_bridge::Server server("{}");assert(server.add(1,service,nullptr));
 auto run=[&](){for(int i=0;i<100&&client.busy();++i){client.pool(a,clockNow,7);server.pool(b,clockNow,7);++clockNow;}assert(client.state()==FLProgReadClient::Done);};
 assert(client.hello(42,clockNow));run();
 uint8_t data[65];data[0]=101;data[1]=3;memset(data+2,'x',63);assert(client.command(data,65,clockNow));run();assert(calls==1);
 data[1]=3;assert(client.command(data,2,clockNow));run();assert(calls==2);
 data[1]=0;data[2]=2;assert(!client.command(data,3,clockNow));data[2]=1;assert(client.command(data,3,clockNow));run();assert(calls==3);
 data[0]=100;assert(!client.command(data,3,clockNow));data[0]=101;data[1]=2;flprog_bridge::putLE(data+2,0x7fc00000UL,4);assert(!client.command(data,6,clockNow));data[1]=3;data[2]=0;assert(!client.command(data,3,clockNow));
 data[1]=0;data[2]=1;assert(client.command(data,3,clockNow));client.pool(a,clockNow,64);server.pool(b,clockNow,64);assert(calls==4);a.rx.clear();clockNow+=1500;client.pool(a,clockNow);assert(client.state()==FLProgReadClient::Timeout);
 size_t before=a.writes;for(int i=0;i<10;i++)client.pool(a,++clockNow);assert(a.writes==before&&calls==4&&!client.hasSession());
 puts("PASS: max/empty text, bool, NaN/system/NUL rejection, bounded frames, dropped ACK once, no replay");
}
