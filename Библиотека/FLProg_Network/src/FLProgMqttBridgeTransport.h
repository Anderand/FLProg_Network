#pragma once
#include "service/flprogNetworkMqttClient.h"
#include "bridge/FLProgBridgeTcpClient.h"
// One instance per PLC UART Server. All MQTT state stays in MQTT client on PLC.
class FLProgMqttBridgeTransport:public FLProgMqttTransport {
 FLProgTcpBridge bridge_;
 FLProgBridgeTcpClient stream_{bridge_};
 char host_[128]{};uint16_t port_=0,queued_=0;bool pending_=false;
public:
 bool attach(flprog_bridge::Server&server,uint8_t number=1){
  if(number<1||number>8||flprogMqttBridgeTransport(number))return false;
  if(!bridge_.attach(server))return false;flprogMqttBridgeRegistry()[number-1]=this;return true;
 }
 bool connect(const char*h,uint16_t port)override{size_t n=h?strlen(h):0;if(!n||n>127||!port)return false;memcpy(host_,h,n+1);port_=port;pending_=true;return true;}
 bool connected()override{return stream_.connected();}
 int available()override{return stream_.available();}
 int read(uint8_t*p,size_t n)override{size_t at=0;while(at<n&&stream_.available())p[at++]=(uint8_t)stream_.read();return (int)at;}
 size_t write(const uint8_t*p,size_t n)override{
  if(queued_){if(!stream_.canWrite()||stream_.writePending())return 0;uint16_t done=queued_;queued_=0;return done;}
  queued_=(uint16_t)stream_.write(p,n);return 0;
 }
 void stop()override{queued_=0;pending_=false;stream_.stop();}
 void pool()override{stream_.pool(millis());if(pending_&&!bridge_.busy()&&!stream_.connected()&&stream_.connect(host_,port_))pending_=false;}
 bool failed()override{return !pending_&&bridge_.state()==FLProgTcpBridge::Failed;}
};
