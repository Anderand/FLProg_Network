#pragma once
#include "FLProgBridgeProtocol.h"
// PLC-owned socket intent. ESP pulls operations; it never stores MQTT settings.
class FLProgTcpBridge {
public:
 enum Op:uint8_t {Open=1,Write=2,Read=3,Close=4};
 enum State:uint8_t {Idle,Pending,Dispatched,Done,Failed};
 bool attach(flprog_bridge::Server&s){server_=&s;return s.add(5,dispatch,this);}
 bool open(const char*host,uint16_t port,uint32_t now){size_t n=host?strlen(host):0;if(!n||n>127||!port)return false;uint8_t p[130];p[0]=(uint8_t)n;flprog_bridge::putLE(p+1,port,2);memcpy(p+3,host,n);return submit(Open,p,n+3,now);}
 bool write(const uint8_t*p,uint16_t n,uint32_t now){return connected_&&n&&n<=220&&submit(Write,p,n,now);}
 bool read(uint16_t n,uint32_t now){uint8_t p[2];flprog_bridge::putLE(p,n,2);return connected_&&n&&n<=220&&submit(Read,p,2,now);}
 bool close(uint32_t now){return submit(Close,nullptr,0,now);}
 void cancel(){abort();}
 void pool(uint32_t now){if(server_&&session_&&server_->currentSession()!=session_)abort();if(busy()&&(uint32_t)(now-started_)>=10000)abort();}
 bool busy()const{return state_==Pending||state_==Dispatched;}bool connected()const{return connected_;}
 State state()const{return state_;}uint16_t size()const{return resultSize_;}const uint8_t*result()const{return result_;}uint32_t id()const{return id_;}
private:
 flprog_bridge::Server*server_=nullptr;uint64_t session_=0;uint32_t id_=0,started_=0;
 uint8_t data_[223]{},result_[220]{};uint16_t length_=0,resultSize_=0;uint8_t op_=0;State state_=Idle;bool connected_=false;
 void abort(){state_=Failed;connected_=false;resultSize_=0;session_=0;}
 bool submit(uint8_t op,const uint8_t*p,uint16_t n,uint32_t now){if(busy()||n>sizeof(data_)||id_==0xffffffffUL)return false;op_=op;length_=n;if(n)memcpy(data_,p,n);resultSize_=0;started_=now;++id_;state_=Pending;return true;}
 static flprog_bridge::Status dispatch(void*self,uint8_t op,const uint8_t*p,uint16_t n,uint8_t*out,uint16_t&size){return static_cast<FLProgTcpBridge*>(self)->handle(op,p,n,out,size);}
 flprog_bridge::Status handle(uint8_t op,const uint8_t*p,uint16_t n,uint8_t*out,uint16_t&size){using namespace flprog_bridge;
  uint64_t current=server_->currentSession();if(session_&&session_!=current)abort();session_=current;
  if(op==1){if(n)return BadRequest;if(state_!=Pending){out[0]=0;size=1;return Ok;}if(size<5+length_)return BadRequest;putLE(out,id_,4);out[4]=op_;if(length_)memcpy(out+5,data_,length_);size=5+length_;state_=Dispatched;return Ok;}
  if(op==2){if(n<6||n>226||state_!=Dispatched||getLE(p,4)!=id_)return BadRequest;
   uint16_t count=n-6;uint8_t status=p[4];if(status>1||p[5]>1||(!status&&((op_==Write&&(count!=2||getLE(p+6,2)>length_))||(op_==Read&&count>getLE(data_,2))||(op_==Open&&count)||(op_==Close&&count))))return BadRequest;
   connected_=p[5];state_=status?Failed:Done;resultSize_=count;if(count)memcpy(result_,p+6,count);size=0;return Ok;}
  return Unsupported;
 }
};
