from pathlib import Path
import re,subprocess
W=Path(__file__).resolve().parent
cpp=(W.parents[2]/'Библиотека/FLProg_Network/src/service/flprogNetworkHttpServer.cpp').read_text(encoding='utf-8')
names=['sendStreamProgmem','flushResponse','appendResponse','appendResponseProgmem','updateClient']
methods=[]
for name in names:
    match=re.search(r'(?:bool|void) FLProgNetworkHttpServer::'+name+r'\(',cpp)
    start=cpp.index('{',match.start());depth=1;at=start+1
    # These functions contain no brace literals in strings.
    while depth:
        if cpp[at]=='{':depth+=1
        elif cpp[at]=='}':depth-=1
        at+=1
    methods.append(cpp[match.start():at])
prefix=r'''
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
'''
main=r'''
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
'''
(W/'host_test.cpp').write_text(prefix+'\n'.join(methods)+main,encoding='utf-8')
zig=Path(r'E:\FLP\Flprog_network\audit\host-tools\ziglang\zig.exe')
subprocess.run([str(zig),'c++',str(W/'host_test.cpp'),'-o',str(W/'host_test.exe')],check=True)
subprocess.run([str(W/'host_test.exe')],check=True)
