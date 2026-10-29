#include "http_read_native_adapter.h"
using WebServer=MockServer;
#include "BridgeProjectHttp.h"
#include "FLProgWebUiBridge.h"
#include "FLProgBridgeResources.h"
#include "MockProject.h"
#include "MockIdentity.h"
#include "FLProgBridgeProject.h"
#include <iostream>
#include <sstream>
#include <vector>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
static std::string hex(const std::string&s){std::string r;const char*d="0123456789abcdef";for(unsigned char c:s){r+=d[c>>4];r+=d[c&15];}return r.empty()?"-":r;}
static std::string unhex(const std::string&s){if(s=="-")return "";assert(s.size()%2==0);std::string r;for(size_t i=0;i<s.size();i+=2)r+=(char)std::stoi(s.substr(i,2),nullptr,16);return r;}
int main(int argc,char**argv){
#ifdef _WIN32
 _setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);
#endif
 registerPlcReadHttpRoutes();beginProjectServer();fillMock();Port a,b;a.other=&b;b.other=&a;
 std::string identity=MOCK_IDENTITY;bool corrupt=argc>1&&std::string(argv[1])=="corrupt";
 if(argc>1&&std::string(argv[1])=="wrong-id"){auto at=identity.find("FLE4D-30MT");assert(at!=std::string::npos);identity.replace(at,10,"other-board");}
 std::vector<uint8_t> package(FLPROG_BRIDGE_WEB_PACKAGE,FLPROG_BRIDGE_WEB_PACKAGE+FLPROG_BRIDGE_WEB_PACKAGE_SIZE);if(corrupt)package[100]^=1;
 flprog_bridge::Server server(identity.c_str());FLProgWebUiBridge web(mockModel);assert(web.attach(server));
 FLProgBridgeResources resources(package.data(),package.size(),FLPROG_BRIDGE_WEB_PACKAGE_PLAIN_SIZE,FLPROG_BRIDGE_WEB_PACKAGE_SHA256);assert(resources.attach(server));
 uint32_t chunks=0,batches=0,frames=0;std::string line;
 while(std::getline(std::cin,line)){
  if(line.size()>4096)return 2;std::istringstream fields(line);std::vector<std::string>v;std::string s;while(fields>>s)v.push_back(unhex(s));if(v.size()!=10)return 3;
  if(v[0]=="STATS"){std::string body="{\"chunks\":"+std::to_string(chunks)+",\"batches\":"+std::to_string(batches)+",\"frames\":"+std::to_string(frames)+",\"packageBytes\":"+std::to_string(package.size())+"}";std::cout<<200<<" "<<hex(body)<<"\n"<<std::flush;continue;}
  projectServer.args={{"op",v[2]},{"channel",v[3]},{"token",v[4]},{"ticket",v[6]},{"offset",v[7]},{"count",v[8]},{"channels",v[9]}};projectServer.headers={{"Cookie",v[5]}};
  uint32_t before=plcReadJob.ticket;projectServer.invoke(v[1].c_str(),v[0]=="POST"?HTTP_POST:HTTP_GET);
  if(plcReadJob.ticket!=before){++frames;if(plcReadJob.kind==5)++chunks;if(plcReadJob.kind==6)++batches;}
  std::cout<<projectServer.code<<" "<<hex(projectServer.body)<<"\n"<<std::flush;
  for(int i=0;i<16;++i){plcReadJob.client.pool(a,clockNow,64);server.pool(b,clockNow,64);++clockNow;}
 }
}
