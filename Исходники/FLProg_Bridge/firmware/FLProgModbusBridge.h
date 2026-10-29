#pragma once
#include "FLProgBridgeProtocol.h"
// Optional PLC service 2. All banks belong to the application; no bank copies.
class FLProgModbusBridge {
public:
 struct Banks {uint8_t *coils;uint16_t coilCount;const uint8_t *discrete;uint16_t discreteCount;uint16_t *holding;uint16_t holdingCount;const uint16_t *input;uint16_t inputCount;};
 typedef bool (*WritePolicy)(uint8_t function,uint16_t address,uint16_t quantity,const uint8_t *unitAndPdu,uint16_t length);
 FLProgModbusBridge(uint8_t unit,Banks banks,WritePolicy permit=nullptr):unit_(unit),banks_(banks),permit_(permit){}
 bool attach(flprog_bridge::Server &server){return unit_>=1&&unit_<=247&&server.add(2,dispatch,this);}
private:
 uint8_t unit_;Banks banks_;WritePolicy permit_;
 static uint16_t be(const uint8_t*p){return ((uint16_t)p[0]<<8)|p[1];}
 static void put(uint8_t*p,uint16_t v){p[0]=v>>8;p[1]=v;}
 static bool range(uint16_t a,uint16_t n,uint16_t count){return n && (uint32_t)a+n<=count;}
 static flprog_bridge::Status dispatch(void*self,uint8_t op,const uint8_t*d,uint16_t n,uint8_t*out,uint16_t&size){return static_cast<FLProgModbusBridge*>(self)->handle(op,d,n,out,size);}
 flprog_bridge::Status handle(uint8_t op,const uint8_t*d,uint16_t n,uint8_t*out,uint16_t&size){
  using namespace flprog_bridge;
  if(op!=1)return Unsupported;if(n<2||n>254||size<3||!d[0]||d[0]>247)return BadRequest;
  const uint8_t fc=d[1];out[0]=d[0];auto exception=[&](uint8_t code){out[1]=fc|0x80;out[2]=code;size=3;return Ok;};
  if(d[0]!=unit_)return exception(11);
  if(fc!=1&&fc!=2&&fc!=3&&fc!=4&&fc!=5&&fc!=6&&fc!=15&&fc!=16)return exception(1);
  if(n<6)return exception(3);uint16_t a=be(d+2),q=be(d+4);
  if(fc<=4){
   if(n!=6||!q||q>(fc<=2?2000:125))return exception(3);
   if(fc<=2){const uint8_t*bank=fc==1?banks_.coils:banks_.discrete;uint16_t count=fc==1?banks_.coilCount:banks_.discreteCount;
    if(!bank||!range(a,q,count))return exception(2);uint16_t bytes=(q+7)/8;if(size<3+bytes)return BadRequest;out[1]=fc;out[2]=bytes;memset(out+3,0,bytes);
    for(uint16_t i=0;i<q;++i)if((bank[(a+i)/8]>>((a+i)%8))&1)out[3+i/8]|=1u<<(i%8);size=3+bytes;return Ok;
   }
   const uint16_t*bank=fc==3?banks_.holding:banks_.input;uint16_t count=fc==3?banks_.holdingCount:banks_.inputCount;
   if(!bank||!range(a,q,count))return exception(2);if(size<3+q*2)return BadRequest;out[1]=fc;out[2]=q*2;for(uint16_t i=0;i<q;++i)put(out+3+i*2,bank[a+i]);size=3+q*2;return Ok;
  }
  uint16_t count=(fc==5||fc==15)?banks_.coilCount:banks_.holdingCount;
  bool bank=(fc==5||fc==15)?banks_.coils!=nullptr:banks_.holding!=nullptr;uint16_t quantity=(fc==5||fc==6)?1:q;
  if(fc==5||fc==6){if(n!=6||(fc==5&&q!=0&&q!=0xff00))return exception(3);}
  else{uint16_t bytes=fc==15?(q+7)/8:q*2;if(n<7||!q||q>(fc==15?1968:123)||d[6]!=bytes||n!=7+bytes)return exception(3);}
  if(!bank||!range(a,quantity,count))return exception(2);
  if(size<6)return BadRequest;
  if(!permit_||!permit_(fc,a,quantity,d,n))return exception(1);
  if(fc==5||fc==15){for(uint16_t i=0;i<quantity;++i){bool v=fc==5?q!=0:((d[7+i/8]>>(i%8))&1);uint8_t &b=banks_.coils[(a+i)/8],mask=(uint8_t)(1u<<((a+i)%8));if(v)b|=mask;else b&=(uint8_t)~mask;}}
  else for(uint16_t i=0;i<quantity;++i)banks_.holding[a+i]=fc==6?q:be(d+7+i*2);
  memcpy(out+1,d+1,5);size=6;return Ok;
 }
};
