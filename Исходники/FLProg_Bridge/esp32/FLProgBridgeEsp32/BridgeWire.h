// Service-neutral UART transport. No Arduino, network or editor dependencies.
#pragma once
#ifndef FLPROG_BRIDGE_WIRE_V1_DEFINED
#define FLPROG_BRIDGE_WIRE_V1_DEFINED
#include <stdint.h>
#include <stddef.h>
#include <string.h>

namespace flprog_bridge {
enum Status { Ok=0, BadRequest=1, Unsupported=2, Session=3, Busy=4, Denied=5, Duplicate=6 };
enum ServiceId { Control=0, WebUi=1, Modbus=2, Mqtt=3, WebResources=4 };
static const uint16_t MaxPayload=256, MaxEncoded=280, HeaderSize=18;
inline uint32_t crc32(const uint8_t *p, size_t n) {
    uint32_t c=0xffffffffUL;
    while(n--) { c^=*p++; for(uint8_t b=0;b<8;b++) c=(c>>1)^((c&1)?0xedb88320UL:0); }
    return c^0xffffffffUL;
}
inline uint64_t getLE(const uint8_t *p,uint8_t n) { uint64_t v=0; for(uint8_t i=0;i<n;i++) v|=(uint64_t)p[i]<<(8*i); return v; }
inline void putLE(uint8_t *p,uint64_t v,uint8_t n) { for(uint8_t i=0;i<n;i++) p[i]=(uint8_t)(v>>(8*i)); }
inline uint16_t encode(const uint8_t *p,uint16_t n,uint8_t *out) {
    uint16_t at=0,pos=1; uint8_t code=1;
    for(uint16_t i=0;i<n;i++) {
        if(!p[i]) { out[at]=code; at=pos++;code=1; }
        else { out[pos++]=p[i]; if(++code==255) {out[at]=code;at=pos++;code=1;} }
    }
    out[at]=code;out[pos++]=0;return pos;
}
inline uint16_t decode(uint8_t *p,uint16_t n) {
    uint16_t src=0,dst=0;
    while(src<n) {
        uint8_t code=p[src++]; if(!code || src+code-1>n) return 0;
        for(uint8_t j=1;j<code;j++) p[dst++]=p[src++];
        if(code!=255 && src<n) p[dst++]=0;
    }
    return dst;
}
// Handler must return promptly; payload and output must never be retained.
typedef Status (*Handler)(void*,uint8_t,const uint8_t*,uint16_t,uint8_t*,uint16_t&);
struct Service { uint8_t id; Handler call; void *context; };

class Server {
public:
    explicit Server(const char *identityJson): identity(identityJson) {}
    bool add(uint8_t id,Handler call,void *context) {
        if(!id||!call||count==4) return false;
        for(uint8_t i=0;i<count;i++) if(services[i].id==id) return false;
        services[count++]={id,call,context};return true;
    }
    // Invoke every PLC cycle. At most budget bytes RX AND budget bytes TX.
    // UART must provide nonblocking available/read/availableForWrite/write.
    template<class Port> void pool(Port &port,uint32_t now,uint8_t budget=64) {
        if(rxAt && (uint32_t)(now-lastByte)>250) {rxAt=0;dropping=true;}
        if(txAt<txSize) {
            int room=port.availableForWrite();
            if(room>0) {
                uint16_t n=txSize-txAt; if(n>budget)n=budget;if(n>room)n=(uint16_t)room;
                size_t sent=port.write(tx+txAt,n); if(sent>n)sent=n;txAt+=(uint16_t)sent;
            }
            if(txAt<txSize) return;
        }
        txAt=txSize=0;
        uint8_t remaining=budget;
        while(remaining-- && port.available()>0) {
            int value=port.read();if(value<0)break;lastByte=now;
            if(!value) {
                if(rxAt && !dropping) process();rxAt=0;dropping=false;
                if(txSize)break;
            } else if(!dropping) {
                if(rxAt==MaxEncoded) {rxAt=0;dropping=true;badFrames++;}
                else rx[rxAt++]=(uint8_t)value;
            }
        }
    }
    uint32_t errors() const { return badFrames; }
    // Invalidate transport state on disable/reconfiguration, without removing services.
    void resetTransport() {
        rxAt=txAt=txSize=0;lastByte=lastSequence=lastRequestAt=0;
        session=0;dropping=false;
    }
    uint64_t currentSession() const { return session; }
    bool sessionAlive(uint32_t now,uint32_t timeout=3500) const {return session && (uint32_t)(now-lastRequestAt)<=timeout;}
private:
    Service services[4]{};uint8_t count=0;
    const char *identity;
    uint8_t rx[MaxEncoded]{}, tx[MaxEncoded+1]{}, reply[MaxPayload+HeaderSize+4]{};
    uint16_t rxAt=0,txAt=0,txSize=0;
    uint32_t lastByte=0,badFrames=0,lastSequence=0,lastRequestAt=0;
    uint64_t session=0;bool dropping=false;
    void process() {
        uint16_t n=decode(rx,rxAt);
        if(n<HeaderSize+4||rx[0]!=1||rx[3]!=0) {badFrames++;return;}
        uint16_t len=(uint16_t)getLE(rx+16,2);
        if(len>MaxPayload||n!=HeaderSize+len+4||crc32(rx,n-4)!=getLE(rx+n-4,4)) {badFrames++;return;}
        uint64_t incoming=getLE(rx+8,8); uint32_t seq=(uint32_t)getLE(rx+4,4);
        Status status=Unsupported; uint16_t used=0;
        uint8_t *out=reply+HeaderSize+1;
        if(rx[1]==Control && rx[2]==1) {
            if(!incoming||!seq||len!=10||memcmp(rx+HeaderSize,"FLPBRIDGE1",10)) status=BadRequest;
            else {
                const char *prefix="{\"protocol\":1,\"services\":[";
                used=(uint16_t)strlen(prefix);memcpy(out,prefix,used);
                for(uint8_t i=0;i<count;i++) {
                    // Registered service IDs 1..255 represented without printf.
                    if(i)out[used++]=',';
                    uint8_t id=services[i].id;
                    if(id>=100)out[used++]='0'+id/100;
                    if(id>=10)out[used++]='0'+(id/10)%10;
                    out[used++]='0'+id%10;
                }
                const char *middle="],\"identity\":";
                memcpy(out+used,middle,strlen(middle));used+=(uint16_t)strlen(middle);
                size_t size=identity?strlen(identity):0;
                if(!size||used+size+1>MaxPayload-1) {status=BadRequest;used=0;}
                else {
                    memcpy(out+used,identity,size);used+=(uint16_t)size;out[used++]='}';status=Ok;
                    // A duplicate HELLO must NOT reopen the command sequence.
                    if(incoming!=session) {session=incoming;lastSequence=seq;}
                    lastRequestAt=lastByte;
                }
            }
        } else if(!incoming||incoming!=session) status=Session;
        else if(!seq||seq<=lastSequence) status=Duplicate;
        else {
            lastSequence=seq;
            lastRequestAt=lastByte;
            if(rx[1]==Control && rx[2]==2) status=len?BadRequest:Ok; // PING
            else for(uint8_t i=0;i<count;i++) if(services[i].id==rx[1]) {
                used=MaxPayload-1;
                status=services[i].call(services[i].context,rx[2],rx+HeaderSize,len,out,used);
                if(used>MaxPayload-1) {status=BadRequest;used=0;}
                break;
            }
        }
        if(status!=Ok)used=0;
        memcpy(reply,rx,HeaderSize);reply[3]=1;reply[HeaderSize]=(uint8_t)status;
        putLE(reply+16,used+1,2);uint16_t rawSize=HeaderSize+used+1;
        putLE(reply+rawSize,crc32(reply,rawSize),4);
        txSize=encode(reply,rawSize+4,tx);txAt=0;
    }
};
}

#endif // FLPROG_BRIDGE_WIRE_V1_DEFINED
