#pragma once
#include <string>
#include <stdint.h>
#include "flprogNtpTimeZone.h"
#define FLPROG_DNS_MAX_HOSTNAME_LENGTH 253
#define FLPROG_NTP_TIMEZONE_API 1
using String=std::string;
class FLProgNetworkInterface{};
using FLProgNetworkDeviceId=uint8_t;
struct FakeRegistry {FLProgNetworkInterface *getDevice(FLProgNetworkDeviceId){return nullptr;}};
static FakeRegistry flprogNetworkDevices;
static bool FakeBeginReady=false;
class FLProgNetworkNtp {
 FLProgNtpTimeZone zone;
public:
 uint32_t utc=0,success=0,period=3600;mutable int localCalls=0;
 int begins=0,ends=0,periodCalls=0,serverCalls=0,syncCalls=0;bool has=false,on=true;
 bool begin(FLProgNetworkInterface &){++begins;on=true;if(FakeBeginReady){has=true;utc=1704067200;}return true;}
 void end(){++ends;}
 void setEnabled(bool value){on=value;}
 uint8_t error()const{return 0;}
 bool setTimeZone(int offset,uint8_t mode){return mode==0?zone.setFixed(offset):mode==1?zone.setEuropean(offset):zone.setUS(offset);}
 void setServer(const char*){++serverCalls;}
 uint32_t requestPeriod()const{return period;}
 void setRequestPeriod(uint32_t value){period=value;++periodCalls;}
 void setTimeout(uint32_t){}
 void syncNow(){++syncCalls;}
 uint32_t successCount()const{return success;}
 bool hasTime()const{return has;}
 uint32_t unixTime()const{return utc;}
 FLProgNtpLocalDateTime localDateTime()const{++localCalls;return zone.local(utc);}
 bool busy()const{return false;}
};
