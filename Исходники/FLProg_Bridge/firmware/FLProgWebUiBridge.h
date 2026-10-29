// Optional service adapter, independent from the WebUI editor and HTTP server.
#pragma once
#include "FLProgBridgeProtocol.h"
#include <FLProgWebUi.h>
#include <math.h>
#include <stdio.h>

class FLProgWebUiBridge {
public:
    // Project policy checks busy, ranges, allowed outputs etc. No policy = read only.
    typedef bool (*WritePolicy)(uint8_t,const uint8_t*,uint16_t);
    typedef void (*BeforeRead)(uint8_t);
    explicit FLProgWebUiBridge(FLProgWebUiModel &model,WritePolicy policy=nullptr,BeforeRead beforeRead=nullptr):model(model),policy(policy),beforeRead(beforeRead) {}
    bool attach(flprog_bridge::Server &server) {return server.add(flprog_bridge::WebUi,dispatch,this);}
    void setHooks(WritePolicy value,BeforeRead refresh=nullptr){policy=value;beforeRead=refresh;}
private:
    FLProgWebUiModel &model;WritePolicy policy;BeforeRead beforeRead;
    static flprog_bridge::Status dispatch(void *self,uint8_t op,const uint8_t *data,uint16_t len,uint8_t *out,uint16_t &size) {
        return static_cast<FLProgWebUiBridge*>(self)->handle(op,data,len,out,size);
    }
    flprog_bridge::Status handle(uint8_t op,const uint8_t *data,uint16_t len,uint8_t *out,uint16_t &size) {
        using namespace flprog_bridge;
        if(!len)return BadRequest;
        if(op==4) { // Bounded batch: request up to 16 channel numbers.
            if(len>16)return BadRequest;
            for(uint16_t i=0;i<len;i++) {
                int16_t at=model.fbdSlot(data[i]);if(at<0)return BadRequest;
                if(model.directionAt((uint8_t)at)==FLPROG_WEBUI_COMMAND)return Denied;
            }
            if(beforeRead) {
                uint8_t refresh=data[0];
                for(uint16_t i=0;i<len;i++)if(data[i]<=100){refresh=data[i];break;}
                beforeRead(refresh);
            }
            uint16_t used=1;out[0]=0;
            for(uint16_t i=0;i<len;i++) {
                uint8_t at=(uint8_t)model.fbdSlot(data[i]);
                uint16_t need=model.typeAt(at)==FLPROG_WEBUI_TEXT?(uint16_t)strlen(model.textAt(at))+1:
                              model.typeAt(at)==FLPROG_WEBUI_BOOL?2:5;
                if(need>64)return BadRequest;
                if(used+2+need>size)break;
                uint16_t written=need;
                Status result=readValue(at,out+used+2,written);if(result!=Ok)return result;
                out[used]=data[i];out[used+1]=(uint8_t)written;used+=2+written;out[0]++;
            }
            size=used;return out[0]?Ok:BadRequest;
        }
        int16_t index=model.fbdSlot(data[0]);if(index<0)return BadRequest;
        uint8_t slot=(uint8_t)index,type=(uint8_t)model.typeAt(slot);
        if(op==1) { // Read a typed value. Command-only slots may contain secrets.
            if(len!=1)return BadRequest;
            if(model.directionAt(slot)==FLPROG_WEBUI_COMMAND)return Denied;
            if(beforeRead)beforeRead(data[0]);
            return readValue(slot,out,size);
        }
        if(op==2) { // Metadata uses a compact binary record, ID is UTF-8.
            if(len!=1)return BadRequest;
            const char *id=model.descriptor(slot)->id;size=(uint16_t)strlen(id)+3;
            if(size>255)return BadRequest;
            out[0]=data[0];out[1]=type;out[2]=(uint8_t)model.directionAt(slot);
            memcpy(out+3,id,size-3);return Ok;
        }
        if(op!=3)return Unsupported;
        if(len<2||data[1]!=type)return BadRequest;
        if(data[0]<=100||model.directionAt(slot)==FLPROG_WEBUI_PUBLISH||!policy)return Denied;
        bool valid=false;
        switch(type) {
            case FLPROG_WEBUI_BOOL:valid=len==3&&data[2]<=1;break;
            case FLPROG_WEBUI_INT32:valid=len==6;break;
            case FLPROG_WEBUI_FLOAT: { if(len==6) {uint32_t bits=(uint32_t)getLE(data+2,4);float f;memcpy(&f,&bits,4);valid=isfinite(f);}break; }
            case FLPROG_WEBUI_TEXT:valid=len<=65 && memchr(data+2,0,len-2)==nullptr;break;
        }
        if(!valid)return BadRequest;
        if(model.commandPending(slot))return Busy;
        if(!policy(data[0],data+1,len-1))return Denied;
        bool accepted=false;
        switch(type) {
            case FLPROG_WEBUI_BOOL:accepted=model.queueBool(slot,data[2]!=0);break;
            case FLPROG_WEBUI_INT32:accepted=model.queueInt(slot,(int32_t)getLE(data+2,4));break;
            case FLPROG_WEBUI_FLOAT: {uint32_t bits=(uint32_t)getLE(data+2,4);float f;memcpy(&f,&bits,4);accepted=model.queueFloat(slot,f);break;}
            case FLPROG_WEBUI_TEXT: {char s[64];memcpy(s,data+2,len-2);s[len-2]=0;accepted=model.queueText(slot,s);break;}
        }
        size=0;return accepted?Ok:BadRequest;
    }
    flprog_bridge::Status readValue(uint8_t slot,uint8_t *out,uint16_t &size) {
        using namespace flprog_bridge;uint8_t type=(uint8_t)model.typeAt(slot);
        out[0]=type;size=1;
        switch(type) {
            case FLPROG_WEBUI_BOOL:out[size++]=model.boolAt(slot)?1:0;break;
            case FLPROG_WEBUI_INT32:putLE(out+1,(uint32_t)model.intAt(slot),4);size=5;break;
            case FLPROG_WEBUI_FLOAT: {float f=model.floatAt(slot);if(!isfinite(f))return BadRequest;uint32_t bits;memcpy(&bits,&f,4);putLE(out+1,bits,4);size=5;break;}
            case FLPROG_WEBUI_TEXT: {const char *s=model.textAt(slot);size=(uint16_t)strlen(s)+1;if(size>64)return BadRequest;memcpy(out+1,s,size-1);break;}
            default:return BadRequest;
        }
        return Ok;
    }
};
