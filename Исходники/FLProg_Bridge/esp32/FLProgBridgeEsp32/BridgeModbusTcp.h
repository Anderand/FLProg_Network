#pragma once
#include "BridgeReadClient.h"
// One Modbus TCP connection. Port read/write are nonblocking; max64 bytes/pool.
// A session owns UART until its response is sent; caller arbitrates with WebUI/raw.
class FLProgModbusTcpSession {
public:
 enum State {Receiving,NeedUart,Hello,Exchange,Responding,Closed};
 explicit FLProgModbusTcpSession(FLProgModbusClient&client):client_(client){}
 void begin(uint32_t now){state_=Receiving;used_=target_=sent_=0;started_=now;}
 void disconnect(){client_.cancel();state_=Closed;used_=target_=sent_=0;}
 State state()const{return state_;}bool ownsUart()const{return state_==Hello||state_==Exchange;}
 template<class Tcp,class Uart> void pool(Tcp&tcp,Uart&uart,uint32_t now,bool uartFree,uint64_t nonce){
  if(state_==Closed)return;
  if((uint32_t)(now-started_)>=3000){disconnect();tcp.stop();return;}
  if(state_==Receiving){for(uint8_t budget=64;budget&&tcp.available()>0;--budget){int v=tcp.read();if(v<0)break;if(used_>=sizeof(buffer_)){disconnect();tcp.stop();return;}buffer_[used_++]=v;
    if(used_==6){uint16_t length=be(buffer_+4);if(be(buffer_+2)!=0||length<2||length>254){disconnect();tcp.stop();return;}target_=6+length;}
    if(target_&&used_==target_){if(!buffer_[6]||buffer_[6]>247){disconnect();tcp.stop();return;}state_=NeedUart;break;}
   }}
  if(state_==NeedUart){if(!uartFree||client_.busy()){if(!uartFree&&!client_.busy())client_.invalidateSession();exception(6);return;}if(!client_.hasSession()){if(!client_.hello(nonce,now)){exception(11);return;}state_=Hello;}else submit(now);}
  if(state_==Hello||state_==Exchange){client_.pool(uart,now,64);if(client_.busy())return;
   if(client_.state()!=FLProgModbusClient::Done){exception(client_.state()==FLProgModbusClient::Timeout?11:10);return;}
   if(state_==Hello){submit(now);return;}
   uint16_t n=client_.size();if(!validReply(client_.result(),n)){exception(11);return;}
   memcpy(buffer_+6,client_.result(),n);put(buffer_+4,n);used_=6+n;sent_=0;state_=Responding;
  }
  if(state_==Responding){int room=tcp.availableForWrite();if(room<=0)return;uint16_t n=used_-sent_;if(n>64)n=64;if(n>room)n=room;size_t done=tcp.write(buffer_+sent_,n);if(done>n)done=n;sent_+=done;if(sent_==used_)begin(now);}
 }
private:
 FLProgModbusClient&client_;uint8_t buffer_[260]{};uint16_t used_=0,target_=0,sent_=0;uint32_t started_=0;State state_=Closed;
 static uint16_t be(const uint8_t*p){return ((uint16_t)p[0]<<8)|p[1];}static void put(uint8_t*p,uint16_t n){p[0]=n>>8;p[1]=n;}
 bool validReply(const uint8_t *p,uint16_t n)const{
  if(n<2||n>254||p[0]!=buffer_[6]||((p[1]&0x7f)!=(buffer_[7]&0x7f)))return false;
  if(p[1]&0x80)return n==3&&p[2]!=0;
  uint8_t fc=p[1];if(fc>=1&&fc<=4){if(target_<12)return false;uint16_t q=be(buffer_+10),bytes=fc<=2?(q+7)/8:q*2;return n==3+bytes&&p[2]==bytes;}
  if(fc==5||fc==6||fc==15||fc==16)return n==6&&target_>=12&&!memcmp(p+1,buffer_+7,5);
  return false;
 }
 void exception(uint8_t code){buffer_[7]|=0x80;buffer_[8]=code;put(buffer_+4,3);used_=9;sent_=0;state_=Responding;}
 void submit(uint32_t now){if(!client_.modbus(buffer_+6,target_-6,now)){exception(11);return;}state_=Exchange;}
};
