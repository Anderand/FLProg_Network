#pragma once
#include "FLProgTcpBridge.h"
// Cooperative PLC TCP stream. connect() queues an attempt, connected() reports it.
// write() accepts into a bounded buffer, not a delivery acknowledgement.
class FLProgBridgeTcpClient {
 FLProgTcpBridge&bridge_;uint8_t tx_[220]{},rx_[220]{};uint16_t txSize_=0,txAt_=0,rxSize_=0,rxAt_=0;
 uint8_t waiting_=0;bool connected_=false,closing_=false;uint32_t now_=0,nextRead_=0;
public:
 explicit FLProgBridgeTcpClient(FLProgTcpBridge&b):bridge_(b){}
 bool connect(const char*h,uint16_t port){if(bridge_.busy()||connected_)return false;txSize_=rxSize_=rxAt_=0;closing_=false;if(!bridge_.open(h,port,now_))return false;waiting_=1;return true;}
 // Preserve TCP EOF semantics: buffered RX remains readable after peer FIN.
 bool connected()const{return connected_||available()>0;}
 bool canWrite()const{return connected_&&!closing_;}
 bool writePending()const{return txSize_!=0;}
 int available()const{return rxSize_-rxAt_;}int read(){return available()?rx_[rxAt_++]:-1;}
 size_t write(const uint8_t*p,size_t n){if(!connected_||closing_||txSize_)return 0;if(n>220)n=220;if(n)memcpy(tx_,p,n);txSize_=n;txAt_=0;return n;}
 void stop(){bridge_.cancel();connected_=false;waiting_=0;txSize_=rxSize_=rxAt_=0;closing_=!bridge_.close(now_);if(!closing_)waiting_=4;}
 void pool(uint32_t now){now_=now;bridge_.pool(now);if(bridge_.busy())return;
  if(waiting_){uint8_t op=waiting_;waiting_=0;if(bridge_.state()!=FLProgTcpBridge::Done){connected_=false;txSize_=0;return;}connected_=bridge_.connected();
   if(op==2){uint16_t sent=(uint16_t)flprog_bridge::getLE(bridge_.result(),2);txAt_+=sent;if(txAt_>=txSize_)txSize_=txAt_=0;}
   if(op==3){rxSize_=bridge_.size();rxAt_=0;memcpy(rx_,bridge_.result(),rxSize_);nextRead_=now+10;}
  }
  if(closing_){closing_=false;if(bridge_.close(now))waiting_=4;return;}
  if(!connected_)return;
  if(txSize_){if(bridge_.write(tx_+txAt_,txSize_-txAt_,now))waiting_=2;return;}
  if(!available()&&(int32_t)(now-nextRead_)>=0&&bridge_.read(220,now))waiting_=3;
 }
};
