#pragma once
// Actual ESP HTTP route handlers on a native WebServer adapter; no hardware.
#include <string>
#include <map>
#include <functional>
#include <cstdio>
#include <cassert>
#include <deque>
#define F(x) x
#define PROGMEM
class String:public std::string {
public:
 using std::string::string;using std::string::operator=;
 String(){} String(const std::string&s):std::string(s){} String(int n):std::string(std::to_string(n)){} String(unsigned n):std::string(std::to_string(n)){}
 int indexOf(const String&s)const{auto at=find(s);return at==npos?-1:(int)at;}
};
enum {HTTP_GET,HTTP_POST,WL_CONNECTED=3};
struct FakeWifi {int value=WL_CONNECTED;int status(){return value;}} WiFi;
uint32_t clockNow=0;uint32_t millis(){return clockNow;}uint32_t esp_random(){static uint32_t value=12345;return ++value;}
struct MockServer {
 MockServer(int=0){}
 bool begin(){return true;} void handleClient(){} void collectHeaders(const char**,size_t){}
 std::map<std::pair<std::string,int>,std::function<void()>> routes;
 std::map<std::string,std::string> args,headers;int code=0;std::string body;
 void on(const char* path,int method,std::function<void()> f){routes[{path,method}]=f;}
 String arg(const char* name){return args[name];}String header(const char* name){return headers[name];}
 void sendHeader(const char*,const char*){}
 void send(int value,const char*,const String& text){code=value;body=text;}
 void send_P(int value,const char*,const char* text){code=value;body=text;}
 void invoke(const char* path,int method){code=0;body.clear();auto it=routes.find({path,method});if(it==routes.end()){code=404;return;}it->second();}
};
using BridgeWebServer=MockServer;
MockServer setupServer;
bool setupMode=false,tcpBusy=false;String setupToken="form-token",adminSession="0123456789abcdef0123456789abcdef";
bool tcpBridgeBusy(){return tcpBusy;}bool authorizedSettings(){return true;}
inline bool bridgeNetworkReady(){return WiFi.status()==WL_CONNECTED;}
#include "BridgeConfig.h"
#include "BridgePlcHttp.h"
struct Port {
 std::deque<uint8_t>rx;Port*other=nullptr;size_t writes=0;
 int available(){return rx.size();}int read(){int n=rx.front();rx.pop_front();return n;}int availableForWrite(){return 64;}
 size_t write(const uint8_t*p,size_t n){for(size_t i=0;i<n;i++)other->rx.push_back(p[i]);writes+=n;return n;}
};
