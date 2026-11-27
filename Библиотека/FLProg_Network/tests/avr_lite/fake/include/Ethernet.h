#pragma once
#include <Arduino.h>
enum EthernetHardwareStatus { EthernetNoHardware=0, EthernetW5100=1, EthernetW5200=2, EthernetW5500=3 };
enum EthernetLinkStatus { Unknown=0, LinkON=1, LinkOFF=2 };
class EthernetClass {
public:
  bool physical=true, carrier=true, dhcpSuccess=true, initialized=false, renewZero=false;
  int maintainResult=0;
  int initCalls=0, beginCalls=0, maintainCalls=0, linkCalls=0;
  IPAddress ip=IPAddress(192,168,1,100), dns=IPAddress(192,168,1,1), gw=IPAddress(192,168,1,1), mask=IPAddress(255,255,255,0);
  void init(uint8_t) { ++initCalls; /* CS selection does not probe W5100 */ }
  int hardwareStatus() { return initialized && physical ? EthernetW5500 : EthernetNoHardware; }
  int linkStatus() { ++linkCalls; initialized=true; return carrier ? LinkON : LinkOFF; }
  int begin(uint8_t *, unsigned long, unsigned long) { ++beginCalls; initialized=true; if (dhcpSuccess) ip=IPAddress(192,168,1,100); else ip=IPAddress(); return dhcpSuccess?1:0; }
  void begin(uint8_t *, IPAddress newIp, IPAddress newDns, IPAddress newGw, IPAddress newMask) { ++beginCalls; initialized=true; ip=newIp;dns=newDns;gw=newGw;mask=newMask; }
  IPAddress localIP() { return ip; }
  void setLocalIP(IPAddress newIp) { ip=newIp; }
  IPAddress dnsServerIP() { return dns; }
  IPAddress gatewayIP() { return gw; }
  IPAddress subnetMask() { return mask; }
  int maintain() { ++maintainCalls; if(renewZero) ip=IPAddress(); return maintainResult; }
};
extern EthernetClass Ethernet;

