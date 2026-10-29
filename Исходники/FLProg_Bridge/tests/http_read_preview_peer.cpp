#include "http_read_native_adapter.h"
#include <iostream>
#include <sstream>
#include <vector>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
static int writes=0;
static flprog_bridge::Status valueHandler(void*,uint8_t op,const uint8_t*p,uint16_t n,uint8_t*out,uint16_t&size){
 if(op==3){++writes;return flprog_bridge::Denied;}
 if(n!=1 || p[0]!=101)return flprog_bridge::BadRequest;
 if(op==1){out[0]=1;flprog_bridge::putLE(out+1,25,4);size=5;return flprog_bridge::Ok;}
 if(op==2){out[0]=101;out[1]=1;out[2]=2;memcpy(out+3,"preview_setpoint",16);size=19;return flprog_bridge::Ok;}
 return flprog_bridge::Unsupported;
}
static std::string hex(const std::string&s){std::string r;const char*d="0123456789abcdef";for(unsigned char c:s){r+=d[c>>4];r+=d[c&15];}return r.empty()?"-":r;}
static std::string unhex(const std::string&s){if(s=="-")return "";assert(s.size()%2==0);std::string r;for(size_t i=0;i<s.size();i+=2)r+=(char)std::stoi(s.substr(i,2),nullptr,16);return r;}
int main(){
#ifdef _WIN32
 _setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);
#endif
 registerPlcReadHttpRoutes();Port a,b;a.other=&b;b.other=&a;
 flprog_bridge::Server server("{\"model\":\"DEMO HTTP ESP\",\"projectId\":\"native-preview\",\"firmware\":\"software-only\"}");server.add(1,valueHandler,nullptr);
 std::string line;
 while(std::getline(std::cin,line)){
  if(line.size()>4096)return 2;
  std::istringstream fields(line);std::vector<std::string> v;std::string s;
  while(fields>>s)v.push_back(unhex(s));if(v.size()!=7)return 3;
  setupServer.args={{"op",v[2]},{"channel",v[3]},{"token",v[4]},{"ticket",v[6]}};
  setupServer.headers={{"Cookie",v[5]}};
  setupServer.invoke(v[1].c_str(),v[0]=="POST"?HTTP_POST:HTTP_GET);
  std::cout<<setupServer.code<<" "<<hex(setupServer.body)<<"\n"<<std::flush;
  for(int i=0;i<8;++i){plcReadJob.client.pool(a,clockNow,64);server.pool(b,clockNow,64);++clockNow;}
  assert(writes==0);
 }
}
