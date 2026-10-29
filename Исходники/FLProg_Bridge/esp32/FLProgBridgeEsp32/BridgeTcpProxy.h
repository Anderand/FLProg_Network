#pragma once
#include "BridgeReadClient.h"
// ESP is UART master for all services. Service5 pulls a single PLC socket job.
class FLProgBridgeTcpProxy {
 FLProgBridgeSharedSession*shared_=nullptr;uint32_t epoch_=0;
 FLProgModbusClient client_;enum Phase{Hello,Poll,Network,Result};Phase phase_=Hello;
 uint32_t due_=0,started_=0,id_=0;uint8_t op_=0,payload_[223]{},reply_[226]{};uint16_t length_=0,replySize_=0;bool waiting_=false;
public:
 void bindSession(FLProgBridgeSharedSession&s){shared_=&s;client_.bindSession(s);epoch_=s.epoch;}
 bool ownsUart()const{return client_.busy();}
 template<class Socket>void stop(Socket&s){s.stop();client_.cancel();phase_=Hello;waiting_=false;due_=0;}
 template<class Socket,class Uart,class Web>
 void pool(Socket&s,Uart&uart,Web&web,uint32_t now,bool ready,bool blocked,uint64_t nonce){
  if(!ready||blocked){stop(s);return;}
  if(shared_&&epoch_!=shared_->epoch){if(epoch_){s.stop();client_.cancelLocal();phase_=Hello;waiting_=false;due_=0;}epoch_=shared_->epoch;}
  if(shared_&&!client_.hasSession()&&!waiting_&&phase_!=Hello){s.stop();client_.cancelLocal();phase_=Hello;due_=0;}
  if(phase_==Network){
   bool done=true,ok=true;uint16_t n=0;
   if(op_==1){if(s.connected()){}else if(s.failed()||(uint32_t)(now-started_)>=8000)ok=false;else done=false;}
   else if(op_==2){if(!s.connected())ok=false;else{size_t sent=s.write(payload_,length_);if(sent>length_)sent=length_;flprog_bridge::putLE(reply_+6,sent,2);n=2;}}
   else if(op_==3){if(!s.connected()&&!s.available())ok=false;else {int available=s.available();uint16_t wanted=(uint16_t)flprog_bridge::getLE(payload_,2);n=available>0?(available>wanted?wanted:(uint16_t)available):0;for(uint16_t i=0;i<n;++i){int b=s.read();if(b<0){n=i;break;}reply_[6+i]=(uint8_t)b;}}}
   else if(op_==4)s.stop();else ok=false;
   if(!done)return;if(!ok)s.stop();flprog_bridge::putLE(reply_,id_,4);reply_[4]=ok?0:1;reply_[5]=s.connected()?1:0;replySize_=6+n;phase_=Result;waiting_=false;
  }
  if(waiting_){client_.pool(uart,now,64);if(client_.busy())return;waiting_=false;
   if(client_.state()!=FLProgModbusClient::Done){stop(s);due_=now+1000;return;}
   if(phase_==Hello){phase_=Poll;}
   else if(phase_==Result){phase_=Poll;due_=now+10;return;}
   else {const uint8_t*p=client_.result();uint16_t n=client_.size();if(n==1&&p[0]==0){due_=now+10;return;}if(n<5||n>228){stop(s);due_=now+1000;return;}id_=(uint32_t)flprog_bridge::getLE(p,4);op_=p[4];length_=n-5;memcpy(payload_,p+5,length_);bool valid=id_&&((op_==1&&length_>=4&&payload_[0]&&payload_[0]<=127&&length_==3+payload_[0]&&flprog_bridge::getLE(payload_+1,2)&&!memchr(payload_+3,0,payload_[0]))||(op_==2&&length_&&length_<=220)||(op_==3&&length_==2&&flprog_bridge::getLE(payload_,2)&&flprog_bridge::getLE(payload_,2)<=220)||(op_==4&&!length_));if(!valid){stop(s);due_=now+1000;return;}phase_=Network;started_=now;if(op_==1){char host[128];memcpy(host,payload_+3,payload_[0]);host[payload_[0]]=0;s.stop();s.open(host,(uint16_t)flprog_bridge::getLE(payload_+1,2));}return;}
  }
  if(due_&&(int32_t)(now-due_)<0)return;
  if(phase_==Hello){if(shared_&&client_.hasSession()){phase_=Poll;waiting_=client_.tcpPoll(now);}else{if(!shared_)web.invalidateSession();waiting_=client_.hello(nonce?nonce:1,now);if(shared_)epoch_=shared_->epoch;}}
  else if(phase_==Poll)waiting_=client_.tcpPoll(now);
  else if(phase_==Result)waiting_=client_.tcpResult(reply_,replySize_,now);
 }
};
