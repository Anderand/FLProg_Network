// Read-only, bounded resource service. Bytes remain in Flash; no resource buffer.
#pragma once
#include "FLProgBridgeProtocol.h"
#if defined(__AVR__)
#include <avr/pgmspace.h>
#endif
class FLProgBridgeResources {
public:
    FLProgBridgeResources(const uint8_t *data,uint32_t length,uint32_t plainLength,const uint8_t *sha256):data(data),length(length),plainLength(plainLength),digest(sha256) {}
    bool attach(flprog_bridge::Server &server){return server.add(flprog_bridge::WebResources,dispatch,this);}
private:
    const uint8_t *data;uint32_t length,plainLength;const uint8_t *digest;
    static uint8_t flashByte(const uint8_t *p) {
#if defined(__AVR__)
        return pgm_read_byte(p);
#else
        return *p;
#endif
    }
    static flprog_bridge::Status dispatch(void *self,uint8_t op,const uint8_t *in,uint16_t n,uint8_t *out,uint16_t &size) {
        return static_cast<FLProgBridgeResources*>(self)->handle(op,in,n,out,size);
    }
    flprog_bridge::Status handle(uint8_t op,const uint8_t *in,uint16_t n,uint8_t *out,uint16_t &size) {
        using namespace flprog_bridge;
        if(op==1) {
            if(n || size<44 || !data || !digest || !length || !plainLength)return BadRequest;
            out[0]=1;out[1]=1;putLE(out+2,224,2);putLE(out+4,length,4);putLE(out+8,plainLength,4);
            for(uint8_t i=0;i<32;i++)out[12+i]=flashByte(digest+i);
            size=44;return Ok;
        }
        if(op!=2)return Unsupported;
        if(n!=6)return BadRequest;
        uint32_t offset=(uint32_t)getLE(in,4);uint16_t count=(uint16_t)getLE(in+4,2);
        if(!count || count>224 || offset>=length)return BadRequest;
        if(count>length-offset)count=(uint16_t)(length-offset);
        if(size<4+count)return BadRequest;
        putLE(out,offset,4);
        for(uint16_t i=0;i<count;i++)out[4+i]=flashByte(data+offset+i);
        size=4+count;return Ok;
    }
};
