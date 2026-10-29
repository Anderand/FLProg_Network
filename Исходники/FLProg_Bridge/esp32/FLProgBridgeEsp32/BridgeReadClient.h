// Cooperative typed client. UART framing is the same as PC/PLC Bridge v1.
#pragma once
#include "BridgeWire.h"
#include <math.h>
struct FLProgBridgeSharedSession{uint64_t session=0;uint32_t sequence=0,epoch=0;bool hello=false;const void*owner=nullptr;const void*waiter=nullptr;uint32_t until=0;};
template<unsigned TxCapacity=96> class FLProgBridgeTypedClient {
public:
    enum State {Idle=0,Sending=1,Waiting=2,Done=3,Timeout=4,PlcError=5,Cancelled=6};
    bool busy() const {return state_==Sending || state_==Waiting;}
    State state() const {return state_;}
    uint8_t status() const {return status_;}
    uint16_t size() const {return resultSize_;}
    const uint8_t *result() const {return rx_+flprog_bridge::HeaderSize+1;}
    uint32_t badFrames() const {return bad_;}
    void bindSession(FLProgBridgeSharedSession&s){shared_=&s;}
    bool hasSession() const {return shared_?shared_->hello:hello_;}
    void invalidateSession(){hello_=false;if(shared_)shared_->hello=false;}
    void cancelLocal(){if(busy())state_=Cancelled;if(shared_&&shared_->owner==this)shared_->owner=nullptr;if(shared_&&shared_->waiter==this)shared_->waiter=nullptr;txAt_=txSize_=rxAt_=0;}
    void cancel(){cancelLocal();invalidateSession();}
    bool hello(uint64_t session,uint32_t now){
        if(busy() || !session || !sharedReady(now))return false;
        if(shared_&&shared_->hello){session_=shared_->session;sequence_=shared_->sequence;hello_=true;return start(0,1,(const uint8_t*)"FLPBRIDGE1",10,now);}
        session_=session;sequence_=0;hello_=false;if(shared_){shared_->session=session;shared_->sequence=0;shared_->hello=false;++shared_->epoch;}
        return start(0,1,(const uint8_t*)"FLPBRIDGE1",10,now);
    }
    uint64_t session() const {return shared_?shared_->session:session_;}
    bool resourceInfo(uint32_t now){return hasSession() && start(4,1,nullptr,0,now);}
    bool resourceChunk(uint32_t offset,uint16_t count,uint32_t now){
        if(!hasSession() || !count || count>224 || offset>=2097152UL)return false;
        uint8_t data[6];flprog_bridge::putLE(data,offset,4);flprog_bridge::putLE(data+4,count,2);return start(4,2,data,6,now);
    }
    bool batch(const uint8_t *channels,uint8_t count,uint32_t now){return hasSession() && count && count<=16 && start(1,4,channels,count,now);}
    bool read(uint8_t channel,uint32_t now){return hasSession() && start(1,1,&channel,1,now);}
    bool metadata(uint8_t channel,uint32_t now){return hasSession() && start(1,2,&channel,1,now);}
    static bool validCommand(const uint8_t *p,uint8_t n){
        if(n<2 || n>65 || p[0]<=100 || p[1]>3)return false;
        if(p[1]==0)return n==3 && p[2]<=1;
        if(p[1]==1)return n==6;
        if(p[1]==2){if(n!=6)return false;uint32_t bits=(uint32_t)flprog_bridge::getLE(p+2,4);float f;memcpy(&f,&bits,4);return isfinite(f);}
        return memchr(p+2,0,n-2)==nullptr;
    }
    bool command(const uint8_t *p,uint8_t n,uint32_t now){return hasSession() && validCommand(p,n) && start(1,3,p,n,now);}
    bool modbus(const uint8_t *p,uint16_t n,uint32_t now){return TxCapacity>=288 && hasSession() && n>=2 && n<=254 && start(2,1,p,(uint8_t)n,now);}
    bool tcpPoll(uint32_t now){return TxCapacity>=288 && hasSession() && start(5,1,nullptr,0,now);}
    bool tcpResult(const uint8_t*p,uint16_t n,uint32_t now){return TxCapacity>=288 && hasSession() && n>=6 && n<=226 && start(5,2,p,(uint8_t)n,now);}
    template<class Port> void pool(Port &port,uint32_t now,uint8_t budget=64){
        if(!busy())return;
        if((uint32_t)(now-started_)>=1500){state_=Timeout;invalidateSession();if(shared_&&shared_->owner==this)shared_->owner=nullptr;txAt_=txSize_=rxAt_=0;return;}
        if(state_==Sending){
            int room=port.availableForWrite();
            if(room>0){uint16_t n=txSize_-txAt_;if(n>budget)n=budget;if(n>room)n=(uint16_t)room;
                size_t sent=port.write(tx_+txAt_,n);if(sent>n)sent=n;txAt_+=(uint16_t)sent;}
            if(txAt_<txSize_)return;
            state_=Waiting;
        }
        if(rxAt_ && (uint32_t)(now-lastByte_)>250){rxAt_=0;dropping_=true;}
        for(uint8_t left=budget;left && port.available()>0;--left){
            int value=port.read();if(value<0)break;lastByte_=now;
            if(value==0){if(rxAt_ && !dropping_)process();rxAt_=0;dropping_=false;if(!busy())return;}
            else if(!dropping_){if(rxAt_==sizeof(rx_)){rxAt_=0;dropping_=true;++bad_;}else rx_[rxAt_++]=(uint8_t)value;}
        }
    }
private:
    FLProgBridgeSharedSession*shared_=nullptr;
    uint8_t tx_[TxCapacity]{},rx_[flprog_bridge::MaxEncoded]{};
    uint16_t txAt_=0,txSize_=0,rxAt_=0,resultSize_=0;
    uint64_t session_=0;
    uint32_t sequence_=0,started_=0,lastByte_=0,bad_=0;
    State state_=Idle;uint8_t service_=0,operation_=0,status_=0;
    bool dropping_=false,hello_=false;
    bool sharedReady(uint32_t now){if(!shared_)return true;if(shared_->waiter&&(int32_t)(now-shared_->until)>=0)shared_->waiter=nullptr;if(shared_->owner&&shared_->owner!=this){shared_->waiter=this;shared_->until=now+20;return false;}if(shared_->waiter&&shared_->waiter!=this)return false;if(shared_->waiter==this)shared_->waiter=nullptr;return true;}
    bool start(uint8_t service,uint8_t operation,const uint8_t *data,uint8_t len,uint32_t now){
        using namespace flprog_bridge;
        if(!sharedReady(now))return false;
        if(shared_){session_=shared_->session;sequence_=shared_->sequence;}
        if(busy() || sequence_==0xffffffffUL || HeaderSize+len+5>TxCapacity-8)return false;
        // No generic public exchange: explicit operations and validated typed commands only.
        uint8_t raw[TxCapacity-8]{};raw[0]=1;raw[1]=service;raw[2]=operation;
        putLE(raw+4,++sequence_,4);putLE(raw+8,session_,8);putLE(raw+16,len,2);if(len)memcpy(raw+HeaderSize,data,len);
        if(shared_){shared_->sequence=sequence_;shared_->owner=this;}
        putLE(raw+HeaderSize+len,crc32(raw,HeaderSize+len),4);
        tx_[0]=0;txSize_=1+encode(raw,HeaderSize+len+4,tx_+1);
        txAt_=rxAt_=resultSize_=0;started_=lastByte_=now;dropping_=false;status_=0;
        service_=service;operation_=operation;state_=Sending;return true;
    }
    void process(){
        using namespace flprog_bridge;
        uint16_t n=decode(rx_,rxAt_);
        if(n<HeaderSize+5 || rx_[0]!=1 || rx_[3]!=1){++bad_;return;}
        uint16_t len=(uint16_t)getLE(rx_+16,2);
        if(!len || len>MaxPayload || n!=HeaderSize+len+4 || crc32(rx_,n-4)!=getLE(rx_+n-4,4)){++bad_;return;}
        if(rx_[1]!=service_ || rx_[2]!=operation_ || getLE(rx_+4,4)!=sequence_ || getLE(rx_+8,8)!=session_)return;
        status_=rx_[HeaderSize];resultSize_=len-1;if(shared_&&shared_->owner==this)shared_->owner=nullptr;
        if(status_!=Ok){state_=PlcError;if(status_==Session)invalidateSession();return;}
        state_=Done;if(service_==0 && operation_==1){hello_=true;if(shared_)shared_->hello=true;}
    }
};

using FLProgReadClient=FLProgBridgeTypedClient<96>;
using FLProgModbusClient=FLProgBridgeTypedClient<288>;
