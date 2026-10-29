#pragma once
#include <string>
#include <map>
#include <vector>
#include <functional>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <deque>
#define F(x) x
#define PROGMEM
class String:public std::string{public:using std::string::string;using std::string::operator=;String(){}String(const std::string&s):std::string(s){}String(int n):std::string(std::to_string(n)){}String(unsigned n):std::string(std::to_string(n)){}String(long n):std::string(std::to_string(n)){}String(unsigned long n):std::string(std::to_string(n)){}int indexOf(const String&s)const{auto at=find(s);return at==npos?-1:at;}bool isEmpty()const{return empty();}void toCharArray(char*p,size_t n)const{if(n){strncpy(p,c_str(),n-1);p[n-1]=0;}}String toString()const{return *this;}};
enum{HTTP_GET,HTTP_POST,WL_CONNECTED=3,WIFI_AP};
struct FakeWiFi{int value=WL_CONNECTED;int status(){return value;}void mode(int){}bool softAP(const char*,const char*,int,bool,int){return true;}String softAPIP(){return "192.0.2.1";}} WiFi;
static uint32_t clockNow=0;uint32_t millis(){return clockNow;}uint32_t esp_random(){static uint32_t n=100;return ++n;}
static bool fakePsram=false;bool psramFound(){return fakePsram;}
struct FakeSerial{template<class...T>void printf(const char*,T...){}template<class T>void println(const T&){} }Serial;
struct FakeESP{bool restarted=false;uint64_t getEfuseMac(){return 123;}void restart(){restarted=true;}}ESP;
struct PrefsStorage{std::map<std::string,std::vector<uint8_t>>blobs;std::map<std::string,std::string>strings;bool fail=false;int writes=0;} fakePrefs;
struct Preferences{std::string space;bool readonly=false;bool begin(const char*s,bool ro){space=s;readonly=ro;return true;}void end(){}std::string key(const char*s){return space+"/"+s;}size_t getBytesLength(const char*s){return fakePrefs.blobs[key(s)].size();}size_t getBytes(const char*s,void*p,size_t n){auto&b=fakePrefs.blobs[key(s)];if(n>b.size())return 0;memcpy(p,b.data(),n);return n;}size_t putBytes(const char*s,const void*p,size_t n){if(readonly||fakePrefs.fail)return 0;auto a=(const uint8_t*)p;fakePrefs.blobs[key(s)]={a,a+n};++fakePrefs.writes;return n;}String getString(const char*s,const char*f){auto at=fakePrefs.strings.find(key(s));return at==fakePrefs.strings.end()?f:at->second.c_str();}size_t putString(const char*s,const String&v){if(readonly||fakePrefs.fail)return 0;fakePrefs.strings[key(s)]=v;++fakePrefs.writes;return v.length();}};
#include "BridgeUrlForm.h"
struct MockServer{int port;explicit MockServer(int p):port(p){}std::map<std::pair<std::string,int>,std::function<void()>>routes;std::map<std::string,std::string>args,headers,responseHeaders;int code=0,requestMethod=HTTP_GET;std::string body;bool begun=false;
 bool begin(uint16_t p=0){if(p)port=p;begun=true;return true;}void handleClient(){}void collectHeaders(const char**,size_t){}void on(const char*p,int m,std::function<void()>f){routes[{p,m}]=f;}String arg(const char*k){auto i=args.find(k);return i==args.end()?String():String(i->second);}bool hasArg(const char*k){return args.count(k);}String header(const char*k){return headers[k];}int method(){return requestMethod;}void sendHeader(const char*k,const String&v){responseHeaders[k]=v;}void send(int c,const char* type="text/plain",const String&b=String()){code=c;body=b;}void send_P(int c,const char*,const char*b){code=c;body=b;}
 void form(const std::string&body){args.clear();const char*at=body.c_str();while(*at){const char*end=strchr(at,'&');if(!end)end=at+strlen(at);const char*eq=(const char*)memchr(at,'=',end-at);if(eq)args[bridgeFormDecode(at,eq-at)]=bridgeFormDecode(eq+1,end-eq-1);at=*end?end+1:end;}}
 void invoke(const char*p,int m){code=0;body.clear();responseHeaders.clear();requestMethod=m;auto i=routes.find({p,m});if(i==routes.end()){code=404;return;}i->second();}
};
using BridgeWebServer=MockServer;
#include "BridgeConfig.h"
static FLProgBridgeNetworkConfig::Kind activeNetworkKind=FLProgBridgeNetworkConfig::Wifi;
static bool wiredReady[3]={false,true,true};
inline bool bridgeNetworkReady(){return activeNetworkKind==FLProgBridgeNetworkConfig::Wifi?WiFi.value==WL_CONNECTED:wiredReady[activeNetworkKind];}
inline String bridgeNetworkIPString(){return "127.0.0.1";}
inline const char*bridgeActiveNetworkName(){return activeNetworkKind==FLProgBridgeNetworkConfig::Wifi?"Wi-Fi":activeNetworkKind==FLProgBridgeNetworkConfig::Wiznet?"LAN · Wiznet SPI":"LAN · RMII LAN8720";}
static bool tcpBusy=false;bool tcpBridgeBusy(){return tcpBusy;}
#include "BridgeSetup.h"
struct Port{std::deque<uint8_t>rx;Port*other=nullptr;int available(){return rx.size();}int read(){int n=rx.front();rx.pop_front();return n;}int availableForWrite(){return 64;}size_t write(const uint8_t*p,size_t n){for(size_t i=0;i<n;i++)other->rx.push_back(p[i]);return n;}};
