#pragma once
#include "BridgeModbusTcp.h"
// One TCP owner at a time. WebUI lease/job has priority before any UART byte.
class FLProgBridgeModbusRuntime {
 FLProgModbusClient client_;
 FLProgModbusTcpSession gateway_{client_};
 uint32_t generation_=0;
 bool active_=false;
public:
 void stop(){gateway_.disconnect();active_=false;}
 template<class Tcp,class Uart,class WebClient>
 void pool(Tcp &tcp,Uart &uart,WebClient &web,uint32_t now,bool networkReady,bool webOwnsUart,uint64_t nonce){
  if(!networkReady||webOwnsUart){tcp.stop();stop();return;}
  if(!tcp.connected()){stop();return;}
  if(!active_||generation_!=tcp.generation()){
   stop();generation_=tcp.generation();active_=true;
   // A Modbus HELLO changes the common PLC session; WebUI must HELLO next.
   web.invalidateSession();gateway_.begin(now);
  }
  gateway_.pool(tcp,uart,now,true,nonce);
 }
};
