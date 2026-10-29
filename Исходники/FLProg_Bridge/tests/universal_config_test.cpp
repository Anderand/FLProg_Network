#include <cassert>
#include <cstdio>
#include <initializer_list>
#include "BridgeConfig.h"
int main(){
 FLProgBridgeConfig c;assert(!bridgeConfigValid(c));strcpy(c.ssid,"test network");assert(bridgeConfigValid(c));strcpy(c.password,"12345678");assert(bridgeConfigValid(c));
 auto valid=c;c.rx=6;assert(!bridgeConfigValid(c));c=valid;c.tx=35;assert(!bridgeConfigValid(c));c=valid;c.rx=c.tx;assert(!bridgeConfigValid(c));c=valid;assert(!bridgeConfigValid(c,true));c.rx=25;c.tx=26;assert(bridgeConfigValid(c,true));
 c=valid;c.baud=1199;assert(!bridgeConfigValid(c));c=valid;c.baud=1000001;assert(!bridgeConfigValid(c));c=valid;c.port=80;assert(!bridgeConfigValid(c));c=valid;c.port=8080;assert(!bridgeConfigValid(c));c=valid;c.port=8081;assert(!bridgeConfigValid(c));c=valid;c.format=6;assert(!bridgeConfigValid(c));c=valid;c.idleMs=3600001;assert(!bridgeConfigValid(c));c=valid;c.idleMs=0;assert(bridgeConfigValid(c));
 c=valid;c.version=3;assert(!bridgeConfigValid(c));c=valid;c.magic=0;assert(!bridgeConfigValid(c));c=valid;memset(c.ssid,'a',sizeof(c.ssid));assert(!bridgeConfigValid(c));c=valid;strcpy(c.password,"short");assert(!bridgeConfigValid(c));
 uint32_t n=0;assert(bridgeUnsigned("0",n)&&n==0);assert(bridgeUnsigned("4294967295",n)&&n==0xffffffffUL);
 for(auto s:{"","-1","+1","12x"," 10","4294967296","999999999999999999999"})assert(!bridgeUnsigned(s,n));
 printf("PASS: saved config validation, GPIO/PSRAM, UART formats, idle, lengths, version, unsigned overflow; config=%zu bytes\n",sizeof(c));
}
