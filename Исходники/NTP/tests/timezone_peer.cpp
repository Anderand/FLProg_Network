#include <cstdio>
#include <cstdlib>
#include <cassert>
#include "flprogNtpTimeZone.h"
int main(int argc,char**argv){
 FLProgNtpTimeZone z;
 assert(z.setFixed(420));assert(!z.setFixed(841));assert(z.local(0).hours==7);
 assert(!z.setRules(0,60,{0,1,0,2},{10,1,0,2}));assert(z.local(0).hours==7);
 assert(!z.setRules(840,60,{3,1,0,2},{10,1,0,2}));
 assert(!z.setRules(0,60,{3,1,0,2},{3,1,0,2}));
 assert(!z.setRules(0,0,{3,1,0,2},{10,1,0,2}));
 int mode=argc>1?atoi(argv[1]):0,offset=argc>2?atoi(argv[2]):0;bool ok=false;
 if(mode==0)ok=z.setFixed(offset);
 if(mode==1)ok=z.setEuropean(offset);
 if(mode==2)ok=z.setUS(offset);
 if(mode==3)ok=z.setRules(600,60,{10,1,0,2},{4,1,0,3});
 if(mode==4)ok=z.setRules(630,30,{10,1,0,2},{4,1,0,2});
 if(mode==5)ok=z.setRules(840,-60,{1,1,0,0},{6,1,0,0});
 assert(ok);unsigned long long n;
 while(scanf("%llu",&n)==1){assert(n<=0xffffffffULL);auto a=z.local((uint32_t)n);
 printf("%lld %u %u %u %u %u %u %u %d %d\n",(long long)a.localUnixTime,a.year,a.month,a.day,a.hours,a.minutes,a.seconds,a.weekDay,a.offsetMinutes,a.daylight?1:0);}
}
