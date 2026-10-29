#include "lan_web_native_adapter.h"
#include "FLProgWebUiBridge.h"
#include "FLProgBridgeResources.h"
#include "MockProject.h"
#include "MockIdentity.h"
#include "FLProgBridgeProject.h"
#include <iostream>
#include <sstream>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
static std::string hex(const std::string&s){const char*d="0123456789abcdef";std::string r;for(unsigned char c:s){r+=d[c>>4];r+=d[c&15];}return r.empty()?"-":r;}
static std::string unhex(const std::string&s){if(s=="-")return "";std::string r;for(size_t i=0;i<s.size();i+=2)r+=(char)std::stoi(s.substr(i,2),nullptr,16);return r;}
static bool policy(uint8_t c,const uint8_t*,uint16_t){return c>100;}
static void consume(){for(uint8_t i=0;i<mockModel.count();++i){if(!mockModel.commandPending(i))continue;bool b;int32_t n;float f;char text[64];switch(mockModel.typeAt(i)){case FLPROG_WEBUI_BOOL:mockModel.takeBool(i,b);break;case FLPROG_WEBUI_INT32:mockModel.takeInt(i,n);break;case FLPROG_WEBUI_FLOAT:mockModel.takeFloat(i,f);break;case FLPROG_WEBUI_TEXT:mockModel.takeText(i,text,64);break;}}mockModel.publishBool(71,mockModel.boolAt(70));}
int main(){
#ifdef _WIN32
 _setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);
#endif
 FLProgBridgeConfigV1 legacy;strcpy(legacy.ssid,"stand-wifi");strcpy(legacy.password,"saved-demo-pass");Preferences p;p.begin("flpbridge",false);p.putBytes("config",&legacy,sizeof(legacy));p.putString("setupKey","demo12345");p.end();assert(loadConfig());beginSettingsWeb(false);beginProjectServer();fillMock();consume();
 flprog_bridge::Server server(MOCK_IDENTITY);FLProgWebUiBridge web(mockModel,policy);assert(web.attach(server));FLProgBridgeResources resources(FLPROG_BRIDGE_WEB_PACKAGE,FLPROG_BRIDGE_WEB_PACKAGE_SIZE,FLPROG_BRIDGE_WEB_PACKAGE_PLAIN_SIZE,FLPROG_BRIDGE_WEB_PACKAGE_SHA256);assert(resources.attach(server));Port a,b;a.other=&b;b.other=&a;
 uint32_t chunks=0,frames=0;std::string line;
 while(std::getline(std::cin,line)){
  std::istringstream fields(line);std::vector<std::string>v;std::string s;while(fields>>s)v.push_back(unhex(s));if(v.size()!=6)return 3;
  if(v[1]=="REBOOT"){plcReadJob.client.cancel();viewerLease.clear();commandPermit=false;restartPending=false;server.resetTransport();assert(loadConfig());activeNetworkKind=config.network.kind;WiFi.value=activeNetworkKind==FLProgBridgeNetworkConfig::Wifi?WL_CONNECTED:0;beginSettingsWeb(false);beginProjectServer();std::cout<<"200 7b7d -\n"<<std::flush;continue;}
  if(v[1]=="OFFLINE"||v[1]=="ONLINE"){bool ready=v[1]=="ONLINE";if(activeNetworkKind==FLProgBridgeNetworkConfig::Wifi)WiFi.value=ready?WL_CONNECTED:0;else wiredReady[activeNetworkKind]=ready;if(!ready){plcReadJob.client.cancel();commandPermit=false;viewerLease.clear();}std::cout<<"200 7b7d -\n"<<std::flush;continue;}
  if(v[1]=="STATS"){std::string body="{\"network\":"+std::to_string((int)activeNetworkKind)+",\"wifiReady\":"+(WiFi.value==WL_CONNECTED?"true":"false")+",\"networkReady\":"+(bridgeNetworkReady()?"true":"false")+",\"chunks\":"+std::to_string(chunks)+",\"frames\":"+std::to_string(frames)+",\"legacyPreserved\":"+(fakePrefs.blobs["flpbridge/config"].size()==sizeof(legacy)&&!memcmp(fakePrefs.blobs["flpbridge/config"].data(),&legacy,sizeof(legacy))?"true":"false")+"}";std::cout<<200<<" "<<hex(body)<<" -\n"<<std::flush;continue;}
  MockServer &http=v[0]=="admin"?setupServer:projectServer;http.form(v[4]+(v[4].empty()||v[5].empty()?"":"&")+v[5]);http.headers={{"Cookie",v[3]}};uint32_t before=plcReadJob.ticket;http.invoke(v[2].c_str(),v[1]=="POST"?HTTP_POST:HTTP_GET);if(before!=plcReadJob.ticket){++frames;if(plcReadJob.kind==5)++chunks;}
  std::string responseHeaders;for(auto &h:http.responseHeaders)responseHeaders+=h.first+": "+h.second+"\n";std::cout<<http.code<<" "<<hex(http.body)<<" "<<hex(responseHeaders)<<"\n"<<std::flush;
  for(int i=0;i<16;i++){plcReadJob.client.pool(a,clockNow,64);server.pool(b,clockNow,64);consume();++clockNow;}
 }
}
