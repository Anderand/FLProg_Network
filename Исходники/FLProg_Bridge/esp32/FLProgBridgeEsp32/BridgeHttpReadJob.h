#pragma once
#include "BridgeReadClient.h"
class FLProgHttpReadJob {
public:
    FLProgReadClient client;
    uint32_t ticket=0;
    uint8_t kind=0;
    // 1=HELLO, 2=read, 3=metadata, 4=resource info; 5=chunk, 6=batch. No command operation exists.
    int start(uint8_t operation,uint16_t channel,uint32_t now,uint64_t session,bool tcpBusy){
        if(operation<1 || operation>4 || channel>255)return 400;
        if(tcpBusy || client.busy())return 409;
        if(ticket==0xffffffffUL)return 503;
        bool ok=operation==1?client.hello(session,now):operation==2?client.read((uint8_t)channel,now):operation==3?client.metadata((uint8_t)channel,now):client.resourceInfo(now);
        if(!ok)return 409;
        ++ticket;kind=operation;return 202;
    }
    int command(const uint8_t *data,uint8_t count,uint32_t now,bool tcpBusy){
        if(!FLProgReadClient::validCommand(data,count))return 400;
        if(tcpBusy || client.busy())return 409;if(ticket==0xffffffffUL)return 503;
        if(!client.command(data,count,now))return 409;++ticket;kind=7;return 202;
    }
    int chunk(uint32_t offset,uint16_t count,uint32_t now,bool tcpBusy){
        if(!count || count>224 || offset>=2097152UL)return 400;
        if(tcpBusy || client.busy())return 409;if(ticket==0xffffffffUL)return 503;
        if(!client.resourceChunk(offset,count,now))return 409;++ticket;kind=5;return 202;
    }
    int batch(const uint8_t *channels,uint8_t count,uint32_t now,bool tcpBusy){
        if(!count || count>16)return 400;
        if(tcpBusy || client.busy())return 409;if(ticket==0xffffffffUL)return 503;
        if(!client.batch(channels,count,now))return 409;++ticket;kind=6;return 202;
    }

};
