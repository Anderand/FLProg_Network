#include <cassert>
#include <cstdio>
#include "flprogNtpUserBlocks.h"
int main(){
 FLProgNetworkInterface net;FLProgNtpUserBlock b;
 auto run=[&](bool en,bool sync,int offset=420,int mode=0){b.control(&net,en,sync,"pool.ntp.org",60,1000,offset,mode);};
 run(true,false);assert(!b.valid());assert(b.ntp.begins==1 && b.ntp.periodCalls==1);
 b.ntp.has=true;b.ntp.utc=1704067200;b.ntp.success=1;
 run(true,false);assert(b.synced&&b.valid()&&b.local.hours==7);assert(b.ntp.localCalls==1);
 for(int i=0;i<2000;++i)run(true,false);
 assert(!b.synced && b.ntp.localCalls==1 && b.ntp.begins==1 && b.ntp.periodCalls==1 && b.ntp.serverCalls==1);
 run(true,true);run(true,true);assert(b.ntp.syncCalls==1);
 run(true,false);run(true,true);assert(b.ntp.syncCalls==2);
 b.ntp.utc++;run(true,false);assert(b.ntp.localCalls==2);
 run(true,false,60,1);assert(b.ntp.localCalls==3 && b.local.hours==1);
 run(true,false,841);assert(!b.valid()&&b.error()==102&&!b.ntp.on);
 run(true,false,420);assert(b.valid() && b.ntp.on && b.local.hours==7);
 run(false,false);assert(!b.valid() && b.ntp.ends==1 && b.error()==0);
 run(true,false);assert(b.ntp.begins==2);
 b.control(nullptr,true,false,"pool.ntp.org",60,1000,0,0);assert(b.error()==100&&!b.valid());
 run(true,false);assert(b.valid());
 b.control(&net,true,false,"",60,1000,0,0);assert(b.error()==101);
 printf("PASS: block enable/recovery, edge SYNC, one cached calendar per UTC second, no per-scan period reset/rebind; zone=%zu bytes\n",sizeof(FLProgNtpTimeZone));
}
