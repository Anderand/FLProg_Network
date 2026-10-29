#include <flprogEthernet.h>
#include <flprogNtpUserBlocks.h>
FLProgWiznetInterface network(PB12,0);
#define FLPROG_WIZNET_INTERFACE1 network
FLProgNtpUserBlock ntpBlock;
bool EN=true,SYNC=false,VALID,SYNCED,Busy,Error,DST_ACTIVE;
long NET_KIND=1,NET_NUM=1,PERIOD_S=3600,TIMEOUT_MS=15000,UTC_MIN=420,DST_MODE=0;
long ERR,YEAR,MONTH,DAY,HOUR,MINUTE,SECOND,WEEKDAY,OFFSET_MIN;
String SERVER="pool.ntp.org";
void setup(){RT_HW_Base.spiSetPins(PB13,PB14,PB15,0);RT_HW_Base.spiBegin(0);network.setDhcp();}
void loop(){network.pool();
FLProgNetworkInterface *ntpSelectedNetwork = nullptr;
#if defined(FLPROG_WIZNET_INTERFACE1)
if (NET_KIND == 1 && NET_NUM == 1) ntpSelectedNetwork = &FLPROG_WIZNET_INTERFACE1;
#endif
#if defined(FLPROG_WIZNET_INTERFACE2)
if (NET_KIND == 1 && NET_NUM == 2) ntpSelectedNetwork = &FLPROG_WIZNET_INTERFACE2;
#endif
#if defined(FLPROG_WIZNET_INTERFACE3)
if (NET_KIND == 1 && NET_NUM == 3) ntpSelectedNetwork = &FLPROG_WIZNET_INTERFACE3;
#endif
#if defined(FLPROG_WIZNET_INTERFACE4)
if (NET_KIND == 1 && NET_NUM == 4) ntpSelectedNetwork = &FLPROG_WIZNET_INTERFACE4;
#endif
#if defined(FLPROG_WIZNET_INTERFACE5)
if (NET_KIND == 1 && NET_NUM == 5) ntpSelectedNetwork = &FLPROG_WIZNET_INTERFACE5;
#endif
#if defined(FLPROG_WIZNET_INTERFACE6)
if (NET_KIND == 1 && NET_NUM == 6) ntpSelectedNetwork = &FLPROG_WIZNET_INTERFACE6;
#endif
#if defined(FLPROG_WIZNET_INTERFACE7)
if (NET_KIND == 1 && NET_NUM == 7) ntpSelectedNetwork = &FLPROG_WIZNET_INTERFACE7;
#endif
#if defined(FLPROG_WIZNET_INTERFACE8)
if (NET_KIND == 1 && NET_NUM == 8) ntpSelectedNetwork = &FLPROG_WIZNET_INTERFACE8;
#endif
#if defined(FLPROG_WIFI_INTERFACE1)
if (NET_KIND == 2 && NET_NUM == 1) ntpSelectedNetwork = &FLPROG_WIFI_INTERFACE1;
#endif
#if defined(FLPROG_WIFI_INTERFACE2)
if (NET_KIND == 2 && NET_NUM == 2) ntpSelectedNetwork = &FLPROG_WIFI_INTERFACE2;
#endif
#if defined(FLPROG_WIFI_INTERFACE3)
if (NET_KIND == 2 && NET_NUM == 3) ntpSelectedNetwork = &FLPROG_WIFI_INTERFACE3;
#endif
#if defined(FLPROG_WIFI_INTERFACE4)
if (NET_KIND == 2 && NET_NUM == 4) ntpSelectedNetwork = &FLPROG_WIFI_INTERFACE4;
#endif
#if defined(FLPROG_WIFI_INTERFACE5)
if (NET_KIND == 2 && NET_NUM == 5) ntpSelectedNetwork = &FLPROG_WIFI_INTERFACE5;
#endif
#if defined(FLPROG_WIFI_INTERFACE6)
if (NET_KIND == 2 && NET_NUM == 6) ntpSelectedNetwork = &FLPROG_WIFI_INTERFACE6;
#endif
#if defined(FLPROG_WIFI_INTERFACE7)
if (NET_KIND == 2 && NET_NUM == 7) ntpSelectedNetwork = &FLPROG_WIFI_INTERFACE7;
#endif
#if defined(FLPROG_WIFI_INTERFACE8)
if (NET_KIND == 2 && NET_NUM == 8) ntpSelectedNetwork = &FLPROG_WIFI_INTERFACE8;
#endif
if (NET_KIND == 0 && NET_NUM >= 0 && NET_NUM < 255)
    ntpSelectedNetwork = flprogNetworkDevices.getDevice((FLProgNetworkDeviceId)NET_NUM);
ntpBlock.control(ntpSelectedNetwork, EN, SYNC, SERVER, PERIOD_S, TIMEOUT_MS, UTC_MIN, DST_MODE);
VALID = ntpBlock.valid();
SYNCED = ntpBlock.synced;
Busy = EN && ntpBlock.ntp.busy();
ERR = ntpBlock.error();
Error = ERR != 0;
YEAR = VALID ? ntpBlock.local.year : 0;
MONTH = VALID ? ntpBlock.local.month : 0;
DAY = VALID ? ntpBlock.local.day : 0;
HOUR = VALID ? ntpBlock.local.hours : 0;
MINUTE = VALID ? ntpBlock.local.minutes : 0;
SECOND = VALID ? ntpBlock.local.seconds : 0;
WEEKDAY = VALID ? ntpBlock.local.weekDay : 0;
DST_ACTIVE = VALID && ntpBlock.local.daylight;
OFFSET_MIN = VALID ? ntpBlock.local.offsetMinutes : 0;
}
