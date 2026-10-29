#include "wrapper_platform.h"
#include "BridgeHttpAdapter.h"
int main(){
 BridgeWebServer settings(8080),project(8081);auto admin=FLProgNetworkHttpServer::all[0],web=FLProgNetworkHttpServer::all[1];
 settings.on("/cookie",HTTP_POST,[&]{settings.sendHeader("Set-Cookie","flpadmin=test; Path=/; HttpOnly; SameSite=Strict");settings.sendHeader("Location","/");settings.send(303);});
 settings.on("/echo",HTTP_POST,[&]{assert(settings.hasArg("payload"));settings.send(200,"text/plain",settings.arg("payload"));});
 settings.on("/large",HTTP_GET,[&]{settings.send(200,"text/plain",String(2100,'x'));});
 static char asset[22001];memset(asset,'A',22000);project.on("/",HTTP_GET,[&]{project.send_P(200,"text/html",asset);});assert(settings.begin()&&project.begin());
 assert(admin->route==4&&web->route==4&&admin->port==8080&&web->port==8081&&admin->capacity==1&&web->capacity==1&&admin->browser&&admin->readBudget==64&&admin->writeBudget==256);
 admin->invoke("/cookie",2);assert(admin->out.find("HTTP/1.1 303")!=std::string::npos&&admin->out.find("Set-Cookie: flpadmin=test;")!=std::string::npos&&admin->out.find("Content-Length: 0")!=std::string::npos);
 admin->rawBody="payload="+String(130,'a')+"&token=abc";admin->invoke("/echo",2);assert(admin->out.find("Content-Length: 130")!=std::string::npos&&admin->out.find(String(130,'a'))!=std::string::npos);
 admin->invoke("/large",1);assert(admin->out.find("500:")==0);
 web->invoke("/",1);assert(web->stream==asset&&web->streamSize==22000&&web->out.size()<2048);
 fakeRoute=5;assert(settings.begin()&&project.begin());assert(admin->route==5&&web->route==5);
 assert(settings.begin(80));assert(WebServer::last&&WebServer::last->begun);WebServer::last->args["payload"]="ap-body";WebServer::last->invoke("/echo",HTTP_POST);assert(WebServer::last->output=="ap-body");WebServer::last->args.clear();WebServer::last->args["plain"]="payload=ap-raw-body&token=demo";WebServer::last->invoke("/echo",HTTP_POST);assert(WebServer::last->output=="ap-raw-body");
 puts("PASS actual HTTP facade with API doubles: routes8080/8081 W5500/RMII, cookie redirect,130hex body, bounded send,22KB Flash stream, recovery AP native backend");
}
