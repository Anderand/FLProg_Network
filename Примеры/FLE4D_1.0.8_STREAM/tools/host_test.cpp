
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <cstdio>
#include <string>
#include <vector>
#include <cassert>
#include <iostream>
#include <algorithm>
#define FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES 2048
#define FLPROG_WEB_SERVER_HEAD 2
#define FLPROG_HTTP_SERVER_STATE_SENDING 5
#define FLPROG_HTTP_SERVER_STATE_CLOSING 6
#define FLPROG_HTTP_SERVER_STATE_ERROR 7
#define FLPROG_HTTP_SERVER_ERROR_TIMEOUT 12
#define FLPROG_HTTP_SERVER_EVENT_TIMEOUT 16
#define FLPROG_HTTP_SERVER_EVENT_RESPONSE 4
uint32_t clockMs=1;uint32_t millis(){return clockMs;}
struct FLProgNetworkTcpServerClient {
 std::string bytes;size_t capacity=1000000,maxCall=0,calls=0;bool closed=false;
 size_t write(const uint8_t* p,size_t size){calls++;maxCall=std::max(maxCall,size);size=std::min(size,capacity);bytes.append((const char*)p,size);return size;}
 void stop(){closed=true;}
};
struct FLProgNetworkHttpServer {
 struct ClientContext {
  union {char line[256];struct{const uint8_t*data;uint32_t length,offset;}flash;};
  char response[2049];uint16_t responseLength=0,responseOffset=0;bool responseOverflow=false;
  uint8_t responseStructured=0,method=0,state=0,error=0;uint32_t lastActivityAt=1;
 } _clients[1];
 bool _legacyAutoStart=false;uint16_t _writeBudget=256;uint32_t _requestTimeoutMs=5000;
 uint32_t _responseCount=0,_events=0,_timeoutCount=0;uint8_t _error=0;
 FLProgNetworkTcpServerClient*_legacyProcessingClient=nullptr;
 ClientContext*currentContext(){return &_clients[0];}
 static const char*reasonPhrase(int){return "OK";}
 void queueProtocolError(uint8_t,ClientContext&,int,uint8_t){}
 void processInput(uint8_t,FLProgNetworkTcpServerClient&,ClientContext&){}
 bool sendStreamProgmem(int,const char*,const void*,uint32_t,const char* =nullptr);
 bool appendResponse(ClientContext&,const uint8_t*,size_t);
 bool appendResponseProgmem(ClientContext&,const char*,size_t);
 void flushResponse(uint8_t,FLProgNetworkTcpServerClient&,ClientContext&);
 void updateClient(uint8_t,FLProgNetworkTcpServerClient&);
};
bool FLProgNetworkHttpServer::sendStreamProgmem(
    int statusCode, const char *type, const void *data, uint32_t length,
    const char *encoding)
{
    ClientContext *ctx = currentContext();
    if (!ctx || _legacyAutoStart || (length && !data)) return false;
    if (encoding && std::strcmp(encoding, "gzip") != 0) return false;
    if (!type || !*type) type = "application/octet-stream";
    ctx->responseLength = ctx->responseOffset = 0;
    ctx->responseOverflow = false;
    ctx->responseStructured = 1;
    const size_t headerCapacity = sizeof(ctx->response) < 320U ? sizeof(ctx->response) : 320U;
    const int count = std::snprintf(ctx->response, headerCapacity,
        "HTTP/1.1 %d %s\r\nContent-Type: %s\r\nContent-Length: %lu\r\n%sConnection: close\r\n\r\n",
        statusCode, reasonPhrase(statusCode), type, (unsigned long)length,
        encoding ? "Content-Encoding: gzip\r\nVary: Accept-Encoding\r\n" : "");
    if (count <= 0 || (size_t)count >= headerCapacity ||
        (size_t)count > FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES) return false;
    ctx->responseLength = (uint16_t)count;
    if (ctx->method != FLPROG_WEB_SERVER_HEAD && length) {
        ctx->flash.data = static_cast<const uint8_t *>(data);
        ctx->flash.length = length; ctx->flash.offset = 0;
        ctx->responseStructured = 2;
    }
    return true;
}
void FLProgNetworkHttpServer::flushResponse(
    uint8_t,
    FLProgNetworkTcpServerClient &client,
    ClientContext &ctx)
{
    if (ctx.responseOffset >= ctx.responseLength && ctx.responseStructured == 2 &&
        ctx.flash.offset < ctx.flash.length)
    {
        // Refill only the existing queue, and perform at most one bounded
        // write per pool iteration. Partial/zero writes keep the same chunk.
        size_t amount = ctx.flash.length - ctx.flash.offset;
        if (amount > _writeBudget) amount = _writeBudget;
        if (amount > 256U) amount = 256U;
        if (amount > FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES) amount = FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES;
        ctx.responseLength = 0;
        ctx.responseOffset = 0;
        if (!appendResponseProgmem(ctx, reinterpret_cast<const char *>(ctx.flash.data + ctx.flash.offset), amount))
        {
            client.stop(); ctx.state = FLPROG_HTTP_SERVER_STATE_CLOSING; return;
        }
        ctx.flash.offset += amount;
    }
    if (ctx.responseOffset >= ctx.responseLength)
    {
        client.stop();
        ctx.state = FLPROG_HTTP_SERVER_STATE_CLOSING;
        _responseCount++;
        _events |= FLPROG_HTTP_SERVER_EVENT_RESPONSE;
        return;
    }

    size_t remaining = (size_t)(ctx.responseLength - ctx.responseOffset);
    if (remaining > _writeBudget) remaining = _writeBudget;
    const size_t written = client.write(
        reinterpret_cast<const uint8_t *>(ctx.response + ctx.responseOffset),
        remaining);
    if (written > 0)
    {
        ctx.responseOffset = (uint16_t)(ctx.responseOffset + written);
        ctx.lastActivityAt = millis();
    }
}
bool FLProgNetworkHttpServer::appendResponse(
    ClientContext &ctx,
    const uint8_t *data,
    size_t length)
{
    if (data == nullptr || length == 0) return true;
    if ((size_t)ctx.responseLength + length > FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES)
    {
        ctx.responseOverflow = true;
        return false;
    }
    std::memcpy(ctx.response + ctx.responseLength, data, length);
    ctx.responseLength = (uint16_t)(ctx.responseLength + length);
    ctx.response[ctx.responseLength] = 0;
    return true;
}
bool FLProgNetworkHttpServer::appendResponseProgmem(
    ClientContext &ctx,
    const char *data,
    size_t length)
{
    if (data == nullptr || length == 0) return true;
    if ((size_t)ctx.responseLength + length > FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES)
    {
        ctx.responseOverflow = true;
        return false;
    }
#if defined(ESP8266)
    for (size_t index = 0; index < length; ++index)
    {
        ctx.response[ctx.responseLength + index] = (char)pgm_read_byte(data + index);
    }
#else
    std::memcpy(ctx.response + ctx.responseLength, data, length);
#endif
    ctx.responseLength = (uint16_t)(ctx.responseLength + length);
    ctx.response[ctx.responseLength] = 0;
    return true;
}
void FLProgNetworkHttpServer::updateClient(
    uint8_t slot,
    FLProgNetworkTcpServerClient &client)
{
    ClientContext &ctx = _clients[slot];

    if (ctx.state == FLPROG_HTTP_SERVER_STATE_SENDING)
    {
        // Bound a stalled response too. An error response cannot be queued on
        // a blocked writer; close the client so the shared STA/AP slot recovers.
        if (ctx.responseOffset < ctx.responseLength && _requestTimeoutMs != 0 &&
            (uint32_t)(millis() - ctx.lastActivityAt) >= _requestTimeoutMs)
        {
            _timeoutCount++;
            _events |= FLPROG_HTTP_SERVER_EVENT_TIMEOUT;
            _error = FLPROG_HTTP_SERVER_ERROR_TIMEOUT;
            ctx.error = FLPROG_HTTP_SERVER_ERROR_TIMEOUT;
            client.stop();
            ctx.state = FLPROG_HTTP_SERVER_STATE_CLOSING;
            return;
        }
        flushResponse(slot, client, ctx);
        return;
    }
    if (ctx.state == FLPROG_HTTP_SERVER_STATE_CLOSING || ctx.state == FLPROG_HTTP_SERVER_STATE_ERROR)
    {
        return;
    }

    if (
        _requestTimeoutMs != 0 &&
        (uint32_t)(millis() - ctx.lastActivityAt) >= _requestTimeoutMs)
    {
        _timeoutCount++;
        _events |= FLPROG_HTTP_SERVER_EVENT_TIMEOUT;
        queueProtocolError(slot, ctx, 408, FLPROG_HTTP_SERVER_ERROR_TIMEOUT);
        return;
    }

    _legacyProcessingClient = &client;
    processInput(slot, client, ctx);
    _legacyProcessingClient = nullptr;
}
int main(){
 std::vector<uint8_t> resource(131072);for(size_t i=0;i<resource.size();i++)resource[i]=i*37;
 for(size_t writable:{size_t(7),size_t(256),size_t(9999)}){
  clockMs=1;
  FLProgNetworkHttpServer s;auto&ctx=s._clients[0];FLProgNetworkTcpServerClient c;c.capacity=writable;
  assert(s.sendStreamProgmem(200,"application/octet-stream",resource.data(),resource.size()));
  assert(ctx.responseLength<320);ctx.state=5;
  for(unsigned i=0;i<100000&&!c.closed;i++){clockMs++;size_t before=c.calls;s.updateClient(0,c);assert(c.calls-before<=1);}
  assert(c.closed&&s._responseCount==1);auto split=c.bytes.find("\r\n\r\n")+4;
  assert(c.bytes.substr(split)==std::string((char*)resource.data(),resource.size()));
  assert(c.maxCall<=256);assert(c.bytes.find("Content-Length: 131072\r\n")!=std::string::npos);
 }
 {FLProgNetworkHttpServer s;auto&ctx=s._clients[0];FLProgNetworkTcpServerClient c;
  ctx.lastActivityAt=clockMs;s.sendStreamProgmem(200,"x",resource.data(),resource.size());ctx.state=5;
  c.capacity=0;for(int i=0;i<6;i++){clockMs+=1000;s.updateClient(0,c);}assert(c.closed&&s._timeoutCount==1);assert(s._responseCount==0);
 }
 {FLProgNetworkHttpServer s;auto&ctx=s._clients[0];FLProgNetworkTcpServerClient c;ctx.method=2;
  ctx.lastActivityAt=clockMs;
  s.sendStreamProgmem(200,"x",resource.data(),resource.size(),"gzip");ctx.state=5;
  while(!c.closed)s.updateClient(0,c);
  assert(c.bytes.size()==c.bytes.find("\r\n\r\n")+4);assert(c.bytes.find("Content-Encoding: gzip")!=std::string::npos);
 }
 {FLProgNetworkHttpServer s;assert(!s.sendStreamProgmem(200,"x",nullptr,1));assert(!s.sendStreamProgmem(200,"x","x",1,"br"));s._legacyAutoStart=true;assert(!s.sendStreamProgmem(200,"x","x",1));}
 {FLProgNetworkHttpServer s;FLProgNetworkTcpServerClient c;s._clients[0].lastActivityAt=clockMs;assert(s.sendStreamProgmem(200,"x",nullptr,0));s._clients[0].state=5;while(!c.closed)s.updateClient(0,c);assert(c.bytes.size()==c.bytes.find("\r\n\r\n")+4);}
 std::cout<<"PASS: real server methods, 128KiB, partial/zero writes, one write/pool, timeout, HEAD, empty, invalid arguments\n";
}
