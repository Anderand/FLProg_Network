#!/usr/bin/env python3
"""Compile & execute the actual FLProgRmiiInterface class with a minimal API mock.

This is a class-contract test; it does not emulate ESP32 ETH or STM32Ethernet.
"""
import subprocess, tempfile, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
head=(ROOT/'src/flprogNetwork.h').read_text(encoding='utf-8')
start='// Independent public RMII device for the FLProg generator.'
end='// Safe typed NET NUM lookups:'
assert head.count(start)==1 and head.count(end)==1
class_code='#if FLPROG_NETWORK_HAS_RMII_INTERFACE\n'+start+head.split(start,1)[1].split(end,1)[0]
assert 'class FLProgRmiiInterface' in class_code
src=r'''#define FLPROG_NETWORK_HAS_RMII_INTERFACE 1
#include <cstdint>
#include <cassert>
#include <string>
#include <iostream>
using String=std::string;
struct IPAddress {
 uint8_t v[4]={0,0,0,0};
 IPAddress()=default;
 IPAddress(uint32_t x):v{(uint8_t)x,(uint8_t)(x>>8),(uint8_t)(x>>16),(uint8_t)(x>>24)}{}
 IPAddress(uint8_t a,uint8_t b,uint8_t c,uint8_t d):v{a,b,c,d}{}
 bool operator==(const IPAddress &x)const{return v[0]==x.v[0]&&v[1]==x.v[1]&&v[2]==x.v[2]&&v[3]==x.v[3];}
};
enum FLProgNetworkDeviceKind:uint8_t {FLPROG_NETWORK_DEVICE_KIND_BASE=0,FLPROG_NETWORK_DEVICE_KIND_WIFI=1,FLPROG_NETWORK_DEVICE_KIND_WIZNET=2,FLPROG_NETWORK_DEVICE_KIND_RMII=3};
#define FLPROG_NETWORK_MODE_ETHERNET 1
class FLProgRmiiEthernet {
 int32_t phy_=0;int mdc_=23,mdio_=18,power_=-1,reset_=-1;uint8_t clock_=0;
 String hostname_;
 IPAddress ip_,gw_,sn_,dns_,dns2_;
 bool dhcp_=true;
 public:
 void setPhyAddress(int32_t x){phy_=x;}int32_t phyAddress()const{return phy_;}
 void setMdcPin(int x){mdc_=x;}int mdcPin()const{return mdc_;}
 void setMdioPin(int x){mdio_=x;}int mdioPin()const{return mdio_;}
 void setPowerPin(int x){power_=x;}int powerPin()const{return power_;}
 void setResetPin(int x){reset_=x;}int resetPin()const{return reset_;}
 void setClockMode(uint8_t x){clock_=x;}uint8_t clockMode()const{return clock_;}
 void setHostname(const String &x){hostname_=x;}String hostname()const{return hostname_;}
 void dhcpMode(bool x){dhcp_=x;}bool isDhcp()const{return dhcp_;}
 void localIP(IPAddress x){ip_=x;}IPAddress configuredIP()const{return ip_;}
 void gateway(IPAddress x){gw_=x;}IPAddress configuredGateway()const{return gw_;}
 void subnet(IPAddress x){sn_=x;}IPAddress configuredSubnet()const{return sn_;}
 void dns(IPAddress x){dns_=x;}IPAddress configuredDns()const{return dns_;}
 void dns2(IPAddress x){dns2_=x;}IPAddress configuredDns2()const{return dns2_;}
 String macAddress()const{return "AA:BB:CC:DD:EE:FF";}
 bool supported()const{return true;}bool isReady()const{return false;}bool linkUp()const{return false;}
 uint8_t error()const{return 0;}uint16_t linkSpeed()const{return 0;}bool fullDuplex()const{return false;}
};
class FLProgNetworkInterface {
 FLProgNetworkDeviceKind kind_=FLPROG_NETWORK_DEVICE_KIND_BASE;
 uint8_t mode_=0;bool wiznet_=true,rmii_=false,work_=false,dhcp_=true;
 IPAddress ip_,gw_,sn_,dns_;
 FLProgRmiiEthernet hw_;
 public:
 FLProgNetworkInterface()=default;
 FLProgNetworkDeviceKind deviceKind()const{return kind_;}
 void networkMode(uint8_t value){mode_=value;} uint8_t networkMode()const{return mode_;}
 void wiznetMode(bool value){wiznet_=value;}bool wiznetMode()const{return wiznet_;}
 void rmiiMode(bool value){rmii_=value;}bool rmiiMode()const{return rmii_;}
 void workMode(bool value){work_=value;}bool workMode()const{return work_;}
 void setRmiiPhyAddress(int32_t x){hw_.setPhyAddress(x);}
 void setRmiiMdcPin(int x){hw_.setMdcPin(x);}
 void setRmiiMdioPin(int x){hw_.setMdioPin(x);}
 void setRmiiPowerPin(int x){hw_.setPowerPin(x);}
 void setRmiiResetPin(int x){hw_.setResetPin(x);}
 void setRmiiClockMode(uint8_t x){hw_.setClockMode(x);}
 void setRmiiHostname(const String &x){hw_.setHostname(x);}
 void rmiiDhcpMode(bool x){hw_.dhcpMode(x);}
 void rmiiLocalIP(IPAddress x){hw_.localIP(x);}
 void rmiiGateway(IPAddress x){hw_.gateway(x);}
 void rmiiSubnet(IPAddress x){hw_.subnet(x);}
 void rmiiDns(IPAddress x){hw_.dns(x);}
 void rmiiDns2(IPAddress x){hw_.dns2(x);}
 FLProgRmiiEthernet &rmiiHardware(){return hw_;}
 const FLProgRmiiEthernet &rmiiHardware()const{return hw_;}
 void dhcpMode(bool x){dhcp_=x;}bool isDhcp()const{return dhcp_;}
 void localIP(IPAddress x){ip_=x;}IPAddress localIP()const{return ip_;}
 void gateway(IPAddress x){gw_=x;}IPAddress gateway()const{return gw_;}
 void subnet(IPAddress x){sn_=x;}IPAddress subnet()const{return sn_;}
 void dns(IPAddress x){dns_=x;}IPAddress dns()const{return dns_;}
 void connect(){}uint8_t pool(){return 0;}
 protected:void setDeviceKind(FLProgNetworkDeviceKind x){kind_=x;}
};
'''+class_code+r'''
int main(){
 FLProgRmiiInterface net;
 FLProgNetworkInterface *base=&net;
 assert(base->deviceKind()==FLPROG_NETWORK_DEVICE_KIND_RMII);
 assert(base->networkMode()==FLPROG_NETWORK_MODE_ETHERNET);
 assert(!base->wiznetMode()&&base->rmiiMode()&&base->workMode());
 FLProgRmiiInterface custom(1,23,18);
 assert(custom.phyAddress()==1&&custom.mdcPin()==23&&custom.mdioPin()==18);
 custom.setPowerPin(4); custom.setResetPin(5); custom.setClockMode(2);custom.setHostname("flprog-rmii");
 assert(custom.powerPin()==4&&custom.resetPin()==5&&custom.clockMode()==2&&custom.hostname()=="flprog-rmii");
 custom.resetDhcp();assert(!custom.isDhcp()&&!custom.rmiiHardware().isDhcp());
 const IPAddress ip(192,168,1,25),gw(192,168,1,1),sn(255,255,255,0),dns(1,1,1,1),dns2(8,8,8,8);
 custom.localIP(ip);custom.gateway(gw);custom.subnet(sn);custom.dns(dns);custom.dns2(dns2);
 assert(custom.localIP()==ip && custom.gateway()==gw&&custom.subnet()==sn&&custom.dns()==dns&&custom.dns2()==dns2);
 assert(custom.rmiiHardware().configuredIP()==ip &&custom.rmiiHardware().configuredGateway()==gw);
 assert(custom.rmiiHardware().configuredSubnet()==sn && custom.rmiiHardware().configuredDns()==dns&&custom.rmiiHardware().configuredDns2()==dns2);
 custom.setDhcp();assert(custom.isDhcp()&&custom.rmiiHardware().isDhcp());
 custom.localIP(10,0,0,13);assert(custom.rmiiHardware().configuredIP()==IPAddress(10,0,0,13));
 assert(custom.phyMacAddress()=="AA:BB:CC:DD:EE:FF");
 assert(custom.supported() && !custom.phyReady()&&!custom.phyLinkUp()&&!custom.phyError());
 assert(custom.begin()==0);
 std::cout<<"RMII_PUBLIC_CLASS_CONTRACT_PASS"<<std::endl;
}
'''
with tempfile.TemporaryDirectory(prefix='flprog_rmii_class_') as tmp:
 test=Path(tmp)/'test.cpp';test.write_text(src)
 for compiler in ('g++','clang++'):
  if not shutil.which(compiler):continue
  for flags in ([],['-fsanitize=address,undefined','-fno-omit-frame-pointer']):
   cmd=[compiler,'-std=c++11','-Wall','-Wextra','-Werror','-pedantic','-fno-rtti','-fno-exceptions',*flags,str(test),'-o',str(Path(tmp)/'test.out')]
   subprocess.run(cmd,check=True)
   subprocess.run([str(Path(tmp)/'test.out')],check=True)
print('ALL_RMII_CLASS_TESTS_PASS')
