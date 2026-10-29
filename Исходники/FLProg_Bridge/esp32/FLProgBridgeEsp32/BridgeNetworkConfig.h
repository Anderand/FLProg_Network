#pragma once
#include <stdint.h>
struct FLProgBridgeNetworkConfig {
 enum Kind:uint8_t {Wifi=0,Wiznet=1,RmiiLan8720=2};
 enum Service:uint8_t {RawBridge=0,ModbusTcp=1,PlcTcpClient=2};Service service=ModbusTcp;
 Kind kind=Wiznet;int8_t sck=18,miso=19,mosi=23,cs=5;
 int8_t mdc=23,mdio=18,power=-1,reset=-1;uint8_t phy=0,clock=0;
 uint8_t uartRx=32,uartTx=33;uint32_t baud=115200;uint16_t port=502;
};
inline bool bridgePin(int p,bool output=false){return p>=0&&p<=39&&!(p>=6&&p<=11)&&(!output||p<34)&&p!=20&&p!=24&&p!=28&&p!=29&&p!=30&&p!=31;}
inline bool bridgeNetworkValid(const FLProgBridgeNetworkConfig&c){
 if(c.kind>2||c.service>2||!bridgePin(c.uartRx)||!bridgePin(c.uartTx,true)||c.uartRx==c.uartTx||c.baud<1200||c.baud>1000000||!c.port||c.port==8080||c.port==8081||(c.port==3234&&c.service==FLProgBridgeNetworkConfig::ModbusTcp))return false;
 if(c.kind==FLProgBridgeNetworkConfig::Wiznet){const int p[]={c.sck,c.miso,c.mosi,c.cs};for(int i=0;i<4;i++){if(!bridgePin(p[i],i!=1)||p[i]==c.uartRx||p[i]==c.uartTx)return false;for(int j=0;j<i;j++)if(p[i]==p[j])return false;}}
 if(c.kind==FLProgBridgeNetworkConfig::RmiiLan8720){if(c.clock>3||c.phy>31||!bridgePin(c.mdc,true)||!bridgePin(c.mdio,true)||c.mdc==c.mdio)return false;
  const int pins[]={19,21,22,25,26,27,c.mdc,c.mdio,c.power,c.reset,c.clock==2?16:c.clock==3?17:0};
  for(unsigned i=0;i<sizeof(pins)/sizeof(pins[0]);++i)if(pins[i]>=0){if(pins[i]==c.uartRx||pins[i]==c.uartTx)return false;for(unsigned j=0;j<i;++j)if(pins[j]==pins[i])return false;}
  if((c.power>=0&&!bridgePin(c.power,true))||(c.reset>=0&&!bridgePin(c.reset,true)))return false;
 }
 return true;
}
