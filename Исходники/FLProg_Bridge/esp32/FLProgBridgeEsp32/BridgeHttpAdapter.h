#pragma once
#include <WebServer.h>
#include <functional>
#include <vector>
#include <memory>
#include "BridgeUrlForm.h"
// WebServer-compatible bridge facade. Normal operation always uses FLProg_Network.
// Arduino WebServer is created only for the recovery AP on port80.
class BridgeWebServer {
 struct Route{String path;HTTPMethod method;std::function<void()> callback;};
 std::vector<Route> routes_;FLProgNetworkHttpServer http_;std::unique_ptr<::WebServer> ap_;String headers_;uint16_t port_;bool native_=false;
 inline static BridgeWebServer*instances_[2]={nullptr,nullptr};
 static void dispatch(FLProgNetworkHttpServer*server){for(auto self:instances_)if(self && &self->http_==server){self->headers_="";for(auto&r:self->routes_)if(r.path==server->uri()&&r.method==self->method()){r.callback();return;}server->sendDefault404Page();return;}}
public:
 explicit BridgeWebServer(uint16_t port):port_(port){for(auto &slot:instances_)if(!slot){slot=this;break;}}
 void on(const char*path,HTTPMethod method,std::function<void()> callback){for(auto&r:routes_)if(r.path==path&&r.method==method){r.callback=callback;return;}if(routes_.size()<14)routes_.push_back({path,method,callback});}
 void collectHeaders(const char**,size_t){} // FLProg_Network parses headers itself.
 bool begin(uint16_t port=0){if(port)port_=port;if(port_==80){native_=true;ap_.reset(new ::WebServer(80));const char*h[]={"Cookie"};ap_->collectHeaders(h,1);for(auto&r:routes_)ap_->on(r.path,r.method,r.callback);ap_->begin();return true;}
  native_=false;http_.setBrowserHeaderCompatibility(true);http_.setReadBudget(64);http_.setWriteBudget(256);
  for(auto&r:routes_)if(!http_.addHandler(r.path.c_str(),dispatch,r.method==HTTP_GET?FLPROG_WEB_SERVER_GET:FLPROG_WEB_SERVER_POST))return false;
  return http_.begin(bridgeNetwork,port_,bridgeNetworkRoute(),1);
 }
 void handleClient(){if(native_)ap_->handleClient();} // Normal servers are managed by bridgeNetwork.pool().
 HTTPMethod method(){return native_?ap_->method():http_.method()==FLPROG_WEB_SERVER_GET?HTTP_GET:HTTP_POST;}
 String header(const char*key){return native_?ap_->header(key):http_.headerValueAtKey(key);}
 bool hasArg(const char*key){if(native_){if(ap_->hasArg(key))return true;String value;return bridgeFormFind(ap_->arg("plain").c_str(),key,value);}String value;return http_.hasArgumentKey(key)||bridgeFormFind(http_.body(),key,value);}
 String arg(const char*key){if(native_){if(ap_->hasArg(key))return ap_->arg(key);String value;bridgeFormFind(ap_->arg("plain").c_str(),key,value);return value;}if(http_.hasArgumentKey(key))return http_.argumentValueAtKey(key);String value;bridgeFormFind(http_.body(),key,value);return value;}
 void sendHeader(const char*key,const String&value){if(native_){ap_->sendHeader(key,value);return;}if(value.indexOf('\r')>=0||value.indexOf('\n')>=0||headers_.length()+strlen(key)+value.length()+4>512)return;headers_+=key;headers_+=": ";headers_+=value;headers_+="\r\n";}
 void send(int code,const char*type="text/plain; charset=utf-8",const String&body=String()){
  if(native_){ap_->send(code,type,body);return;}
  String head="HTTP/1.1 "+String(code)+" "+String(code==200?"OK":code==202?"Accepted":code==303?"See Other":code==403?"Forbidden":code==400?"Bad Request":"Response")+"\r\nContent-Type: "+String(type)+"\r\nContent-Length: "+String(body.length())+"\r\nConnection: close\r\n"+headers_+"\r\n";
  if(head.length()+body.length()>FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES){http_.send(500,"text/plain","Bridge response exceeds bounded queue");return;}
  http_.print(head);http_.print(body);
 }
 void send_P(int code,const char*type,const char*body){if(native_)ap_->send_P(code,type,body);else http_.sendStreamProgmem(code,type,body,strlen(body));}
};
