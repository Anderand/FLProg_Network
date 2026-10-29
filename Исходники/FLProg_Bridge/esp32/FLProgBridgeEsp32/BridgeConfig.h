#pragma once
#include <stdint.h>
#include <string.h>
#include "BridgeNetworkConfig.h"
struct FLProgBridgeConfigV1 {
    uint32_t magic=0x464c4231,baud=115200,idleMs=60000;
    uint16_t version=1,port=3234;
    uint8_t rx=16,tx=17,format=0;
    char ssid[33]{},password[65]{};
};
struct FLProgBridgeConfig:FLProgBridgeConfigV1 {
    FLProgBridgeNetworkConfig network;
    FLProgBridgeConfig(){version=2;network.kind=FLProgBridgeNetworkConfig::Wifi;network.service=FLProgBridgeNetworkConfig::RawBridge;}
};
inline FLProgBridgeNetworkConfig bridgeTransportConfig(const FLProgBridgeConfig &c){auto n=c.network;n.uartRx=c.rx;n.uartTx=c.tx;n.baud=c.baud;n.port=c.port;return n;}
inline bool bridgeRxPin(int n){
    return n==4||n==13||n==14||(n>=16&&n<=19)||(n>=21&&n<=23)||(n>=25&&n<=27)||(n>=32&&n<=39);
}
inline bool bridgeConfigValid(const FLProgBridgeConfig &c,bool psram=false){
    if(c.magic!=0x464c4231||c.version!=2||c.baud<1200||c.baud>1000000||(c.port<1024&&!(c.network.service==FLProgBridgeNetworkConfig::ModbusTcp&&c.port==502))||(c.port==8080 || c.port==8081)||c.format>5||c.idleMs>3600000)return false;
    if(!bridgeRxPin(c.rx)||!bridgeRxPin(c.tx)||c.tx>=34||c.rx==c.tx)return false;
    if(psram&&(c.rx==16||c.rx==17||c.tx==16||c.tx==17))return false;
    if(psram){const auto &n=c.network;if(n.kind==FLProgBridgeNetworkConfig::Wiznet&&(n.sck==16||n.sck==17||n.miso==16||n.miso==17||n.mosi==16||n.mosi==17||n.cs==16||n.cs==17))return false;if(n.kind==FLProgBridgeNetworkConfig::RmiiLan8720&&(n.clock>=2||n.mdc==16||n.mdc==17||n.mdio==16||n.mdio==17||n.power==16||n.power==17||n.reset==16||n.reset==17))return false;}
    if(!memchr(c.ssid,0,sizeof(c.ssid))||!memchr(c.password,0,sizeof(c.password)))return false;
    size_t ssid=strlen(c.ssid),pass=strlen(c.password);
    return (c.network.kind!=FLProgBridgeNetworkConfig::Wifi || ssid>0)&&ssid<=32&&(pass==0||(pass>=8&&pass<=63))&&bridgeNetworkValid(bridgeTransportConfig(c));
}
inline bool bridgeUnsigned(const char *s,uint32_t &out){
    if(!s||!*s)return false;uint32_t value=0;
    while(*s){if(*s<'0'||*s>'9')return false;uint32_t n=(uint32_t)(*s++-'0');if(value>(0xffffffffUL-n)/10)return false;value=value*10+n;}
    out=value;return true;
}
