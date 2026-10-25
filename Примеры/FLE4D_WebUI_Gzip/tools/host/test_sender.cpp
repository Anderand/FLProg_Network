#include "FLProgWebUiGzipHttp.h"
#include <cassert>
#include <iostream>
int main(){
 for(const char *s:{"", "gzip", "br, gzip", "GZIP; q=0.5", "*;q=1"})assert(flprogWebUiGzipAllowed(String(s)));
 for(const char *s:{"identity", "gzip;q=0", "*;q=0", "gzip;q=0, *;q=1", "gzip;q=2"})assert(!flprogWebUiGzipAllowed(String(s)));
 const unsigned char data[]={0x1f,0x8b,0x00,0xff};FLProgNetworkHttpServer server;
 server.accept=String("gzip");flprogWebUiSendGzip(&server,"application/javascript",data,sizeof(data));
 auto end=server.bytes.find("\r\n\r\n")+4;
 assert(server.bytes.substr(end)==std::string((const char*)data,4));
 assert(server.bytes.find("Content-Length: 4\r\n")!=std::string::npos);
 assert(server.bytes.find("Content-Encoding: gzip\r\n")!=std::string::npos);
 server.bytes.clear();server.verb=FLPROG_WEB_SERVER_HEAD;flprogWebUiSendGzip(&server,"text/css",data,4);
 assert(server.bytes.size()==server.bytes.find("\r\n\r\n")+4);
 server.bytes.clear();server.verb=0;server.accept=String("gzip;q=0, *;q=1");flprogWebUiSendGzip(&server,"text/css",data,4);
 assert(server.bytes.find("406 Not Acceptable")!=std::string::npos);
 assert(server.bytes.substr(server.bytes.find("\r\n\r\n")+4).size()==24);
 std::cout<<"PASS: compiled sender negotiation, binary NUL, lengths, Vary, HEAD and 406\n";
}
