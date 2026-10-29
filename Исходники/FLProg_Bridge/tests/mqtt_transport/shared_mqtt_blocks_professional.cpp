#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include "FLProgMqttBridgeTransport.h"
#include "flprogMqttUserBlocks.h"
#include "FLProgBridgeResources.h"
#include "SharedFixture.h"
#include "BridgeTcpProxy.h"
#include <deque>
#include <vector>
#include <cassert>
#include <cstdio>
struct Port {std::deque<uint8_t>rx;Port*other=nullptr;int available(){return rx.size();}int read(){int b=rx.front();rx.pop_front();return b;}int availableForWrite(){return 11;}size_t write(const uint8_t*p,size_t n){if(n>7)n=7;for(size_t i=0;i<n;++i)other->rx.push_back(p[i]);return n;}};
struct Socket {
 SOCKET fd=INVALID_SOCKET;bool connecting=false,error=false;size_t writes=0;unsigned opens=0;
 void stop(){if(fd!=INVALID_SOCKET)closesocket(fd);fd=INVALID_SOCKET;connecting=false;error=false;}
 void open(const char*h,uint16_t port){stop();++opens;addrinfo hints{},*info=nullptr;hints.ai_family=AF_INET;hints.ai_socktype=SOCK_STREAM;char p[8];snprintf(p,sizeof(p),"%u",port);if(getaddrinfo(h,p,&hints,&info)){error=true;return;}fd=socket(AF_INET,SOCK_STREAM,0);u_long mode=1;ioctlsocket(fd,FIONBIO,&mode);int r=::connect(fd,info->ai_addr,(int)info->ai_addrlen);connecting=r!=0;if(connecting&&WSAGetLastError()!=WSAEWOULDBLOCK)error=true;freeaddrinfo(info);}
 bool connected(){if(fd==INVALID_SOCKET||error)return false;if(connecting){fd_set w,e;FD_ZERO(&w);FD_ZERO(&e);FD_SET(fd,&w);FD_SET(fd,&e);timeval t{};select(0,nullptr,&w,&e,&t);if(FD_ISSET(fd,&e)){error=true;return false;}if(!FD_ISSET(fd,&w))return false;int status=0,n=sizeof(status);getsockopt(fd,SOL_SOCKET,SO_ERROR,(char*)&status,&n);if(status){error=true;return false;}connecting=false;}char byte;int peek=recv(fd,&byte,1,MSG_PEEK);if(peek==0||(peek<0&&WSAGetLastError()!=WSAEWOULDBLOCK)){stop();return false;}return true;}
 bool failed(){return error;}
 int available(){u_long n=0;if(fd!=INVALID_SOCKET)ioctlsocket(fd,FIONREAD,&n);return n;}
 int read(){uint8_t b;return recv(fd,(char*)&b,1,0)==1?b:-1;}
 size_t write(const uint8_t*p,size_t n){if(n>7)n=7;int sent=send(fd,(const char*)p,(int)n,0);if(sent<0){error=WSAGetLastError()!=WSAEWOULDBLOCK;return 0;}writes+=sent;return sent;}
};

uint32_t millis(){return GetTickCount();}
unsigned FLProgNetworkTcpClient::nativeBegin=0,FLProgNetworkTcpClient::nativeConnect=0;
static String Broker="localhost",ClientID="PLC-blocks",User="plc-user",Password="test-only-password";static long PortNumber;
static void core(bool EN=true,bool CON=false,bool DIS=false){long NET_KIND=3,NET_NUM=1,SUB_LIMIT=0,POLL_MS=10,Port=PortNumber;bool Connected,Busy,Error;long ERR,State,Subscriptions,SubBytes;

{

FLProgNetworkInterface *mqttSelectedNetwork = nullptr;
#if defined(FLPROG_WIZNET_INTERFACE1)
if (NET_KIND == 1 && NET_NUM == 1) mqttSelectedNetwork = &FLPROG_WIZNET_INTERFACE1;
#endif
#if defined(FLPROG_WIZNET_INTERFACE2)
if (NET_KIND == 1 && NET_NUM == 2) mqttSelectedNetwork = &FLPROG_WIZNET_INTERFACE2;
#endif
#if defined(FLPROG_WIZNET_INTERFACE3)
if (NET_KIND == 1 && NET_NUM == 3) mqttSelectedNetwork = &FLPROG_WIZNET_INTERFACE3;
#endif
#if defined(FLPROG_WIZNET_INTERFACE4)
if (NET_KIND == 1 && NET_NUM == 4) mqttSelectedNetwork = &FLPROG_WIZNET_INTERFACE4;
#endif
#if defined(FLPROG_WIZNET_INTERFACE5)
if (NET_KIND == 1 && NET_NUM == 5) mqttSelectedNetwork = &FLPROG_WIZNET_INTERFACE5;
#endif
#if defined(FLPROG_WIZNET_INTERFACE6)
if (NET_KIND == 1 && NET_NUM == 6) mqttSelectedNetwork = &FLPROG_WIZNET_INTERFACE6;
#endif
#if defined(FLPROG_WIZNET_INTERFACE7)
if (NET_KIND == 1 && NET_NUM == 7) mqttSelectedNetwork = &FLPROG_WIZNET_INTERFACE7;
#endif
#if defined(FLPROG_WIZNET_INTERFACE8)
if (NET_KIND == 1 && NET_NUM == 8) mqttSelectedNetwork = &FLPROG_WIZNET_INTERFACE8;
#endif
#if defined(FLPROG_WIFI_INTERFACE1)
if (NET_KIND == 2 && NET_NUM == 1) mqttSelectedNetwork = &FLPROG_WIFI_INTERFACE1;
#endif
#if defined(FLPROG_WIFI_INTERFACE2)
if (NET_KIND == 2 && NET_NUM == 2) mqttSelectedNetwork = &FLPROG_WIFI_INTERFACE2;
#endif
#if defined(FLPROG_WIFI_INTERFACE3)
if (NET_KIND == 2 && NET_NUM == 3) mqttSelectedNetwork = &FLPROG_WIFI_INTERFACE3;
#endif
#if defined(FLPROG_WIFI_INTERFACE4)
if (NET_KIND == 2 && NET_NUM == 4) mqttSelectedNetwork = &FLPROG_WIFI_INTERFACE4;
#endif
#if defined(FLPROG_WIFI_INTERFACE5)
if (NET_KIND == 2 && NET_NUM == 5) mqttSelectedNetwork = &FLPROG_WIFI_INTERFACE5;
#endif
#if defined(FLPROG_WIFI_INTERFACE6)
if (NET_KIND == 2 && NET_NUM == 6) mqttSelectedNetwork = &FLPROG_WIFI_INTERFACE6;
#endif
#if defined(FLPROG_WIFI_INTERFACE7)
if (NET_KIND == 2 && NET_NUM == 7) mqttSelectedNetwork = &FLPROG_WIFI_INTERFACE7;
#endif
#if defined(FLPROG_WIFI_INTERFACE8)
if (NET_KIND == 2 && NET_NUM == 8) mqttSelectedNetwork = &FLPROG_WIFI_INTERFACE8;
#endif
if (NET_KIND == 0 && NET_NUM >= 0 && NET_NUM < 255)
    mqttSelectedNetwork = flprogNetworkDevices.getDevice((FLProgNetworkDeviceId)NET_NUM);
flpMqttBlocks().useExternalTransport(NET_KIND == 3 ? flprogMqttBridgeTransport(NET_NUM) : nullptr);
flpMqttBlocks().control(mqttSelectedNetwork, EN, CON, DIS, Broker, Port, ClientID, User, Password, SUB_LIMIT, POLL_MS);
Connected = flpMqttBlocks().mqtt.connected();
Busy = flpMqttBlocks().mqtt.busy();
ERR = flpMqttBlocks().error();
Error = ERR != 0;
State = flpMqttBlocks().mqtt.state();
Subscriptions = (long)flpMqttBlocks().mqtt.subscriptionCount();
SubBytes = (long)flpMqttBlocks().mqtt.subscriptionMemoryBytes();
}

}
static bool publish(const String&Topic,const String&Message,bool Send){static bool mqttPrevSend=false;bool Retain=false,Accepted=false;long ERR;

{
static bool mqttPrevSend = false;
Accepted = false;
if (Send && !mqttPrevSend) {
    Accepted = flpMqttBlocks().mqtt.publish(Topic.c_str(), Message.c_str(), Retain);
    ERR = flpMqttBlocks().mqtt.error();
}
mqttPrevSend = Send;
}

return Accepted;}
static bool subscribe(const String&Topic,bool Subscribe){static bool mqttPrevSub=false;static uint32_t mqttSeen=0;bool Accepted=false,Received=false,Retained=false;String Message,RxTopic;long ERR;

{
static bool mqttPrevSub = false;
static uint32_t mqttSeen = 0;
Accepted = false;
Received = false;
if (Subscribe && !mqttPrevSub) {
    Accepted = flpMqttBlocks().mqtt.subscribe(Topic.c_str());
    ERR = flpMqttBlocks().mqtt.error();
}
mqttPrevSub = Subscribe;
if (mqttSeen != flpMqttBlocks().sequence) {
    mqttSeen = flpMqttBlocks().sequence;
    if (flpMqttBlocks().matches(Topic.c_str(), flpMqttBlocks().topic.c_str())) {
        Received = true;
        RxTopic = flpMqttBlocks().topic;
        Message = flpMqttBlocks().message;
        Retained = flpMqttBlocks().retained;
    }
}
}

return Accepted;}
int main(int argc,char**argv){assert(argc>=3);PortNumber=atoi(argv[2]);Broker=argv[1];WSADATA data;assert(!WSAStartup(MAKEWORD(2,2),&data));
 flprog_bridge::Server server("{\"model\":\"PLC MQTT blocks stand\"}");FLProgMqttBridgeTransport transport;assert(transport.attach(server,1));::Port a,b;a.other=&b;b.other=&a;Socket socket;FLProgReadClient web;FLProgBridgeTcpProxy esp;FLProgBridgeSharedSession shared;web.bindSession(shared);esp.bindSession(shared);
 assert(server.add(1,[](void*,uint8_t op,const uint8_t*d,uint16_t n,uint8_t*out,uint16_t&size){using namespace flprog_bridge;if(op!=1||n!=1||d[0]!=101)return BadRequest;out[0]=1;putLE(out+1,42,4);size=5;return Ok;},nullptr));
 FLProgBridgeResources resources(SharedFixture,sizeof(SharedFixture),72634,SharedSha);assert(resources.attach(server));
 std::vector<uint8_t>downloaded;unsigned webReads=0,webChunks=0;bool webPending=false,chunk=false,helloSent=false,helloPending=false;uint32_t nextWeb=0;
 auto drive=[&](uint32_t now){
  if(webPending&&!web.busy()){assert(web.state()==FLProgReadClient::Done);if(helloPending){helloPending=false;}else if(chunk){uint32_t off=(webChunks%69)*224;uint16_t count=sizeof(SharedFixture)-off;if(count>224)count=224;assert(web.size()==4+count&&flprog_bridge::getLE(web.result(),4)==off);for(int i=0;i<count;++i)assert(web.result()[4+i]==SharedFixture[off+i]);if(webChunks<69)downloaded.insert(downloaded.end(),web.result()+4,web.result()+4+count);++webChunks;}else{assert(web.size()==5&&flprog_bridge::getLE(web.result()+1,4)==42);++webReads;}webPending=false;nextWeb=now+5;}
  if(!webPending&&(int32_t)(now-nextWeb)>=0){chunk=(webReads+webChunks)%4==3;uint32_t off=(webChunks%69)*224;uint16_t count=sizeof(SharedFixture)-off;if(count>224)count=224;if(!helloSent&&webReads>5){webPending=web.hello(999,now);helloPending=webPending;if(webPending)helloSent=true;}else webPending=chunk?web.resourceChunk(off,count,now):web.read(101,now);}
  if(web.busy()&&!esp.ownsUart()){esp.pool(socket,a,web,now,true,false,now+123456);web.pool(a,now,11);}else esp.pool(socket,a,web,now,true,false,now+123456);
  server.pool(b,now,11);
 };

 auto tick=[&](){uint32_t now=millis();drive(now);core();Sleep(0);};
 auto wait=[&](auto predicate){uint32_t start=millis();while(!predicate()&&millis()-start<15000)tick();assert(predicate());};
 {FLProgNetworkInterface net;FLProgNetworkMqttClient direct;assert(direct.begin(net));direct.setPollInterval(0);direct.setBroker("native.test");direct.setClientId("native-default");direct.connect();direct.pool();direct.pool();assert(FLProgNetworkTcpClient::nativeBegin==1&&FLProgNetworkTcpClient::nativeConnect==1);direct.end();FLProgNetworkTcpClient::nativeBegin=FLProgNetworkTcpClient::nativeConnect=0;}
 core();if(argc==4&&!strcmp(argv[3],"--refused")){wait([&](){return flpMqttBlocks().mqtt.error()==FLPROG_MQTT_ERROR_CONNACK_REFUSED;});assert(!flpMqttBlocks().mqtt.connected());flpMqttBlocks().mqtt.end();printf("PASS refused CONNACK, disconnected, native default path unchanged\n");return 0;}
 wait([&](){return flpMqttBlocks().mqtt.connected();});
 subscribe("plc/command",true);wait([&](){return flpMqttBlocks().mqtt.subscriptionCount()==1;});
 if(argc==4&&!strcmp(argv[3],"--many")){for(int i=0;i<6;++i){char topic[32];snprintf(topic,sizeof(topic),"plc/add%d",i);subscribe(topic,false);assert(subscribe(topic,true));wait([&](){return flpMqttBlocks().mqtt.subscriptionCount()==(size_t)i+2;});}}
 String message(400,'A');assert(publish("plc/value",message,true));publish("plc/value",message,false);
 wait([&](){return flpMqttBlocks().sequence==1;});assert(flpMqttBlocks().topic=="plc/command"&&flpMqttBlocks().message=="on!!!");
 wait([&](){return webChunks>=69;});assert(downloaded==std::vector<uint8_t>(SharedFixture,SharedFixture+sizeof(SharedFixture)));
 assert(FLProgNetworkTcpClient::nativeBegin==0&&FLProgNetworkTcpClient::nativeConnect==0);
 core(true,false,true);for(uint32_t started=millis();flpMqttBlocks().mqtt.connected()&&millis()-started<15000;){uint32_t now=millis();drive(now);flpMqttBlocks().mqtt.pool();Sleep(0);}assert(!flpMqttBlocks().mqtt.connected());
 assert(webReads>0&&webChunks>0);printf("SHARED web_reads=%u chunks=%u opens=%u\n",webReads,webChunks,socket.opens);
 flpMqttBlocks().mqtt.end();
 flpMqttBlocks().useExternalTransport(nullptr);
 flpMqttBlocks().control(nullptr,true,false,false,Broker,PortNumber,ClientID,User,Password,0,10);assert(flpMqttBlocks().error()==19&&FLProgNetworkTcpClient::nativeBegin==0);
 FLProgNetworkInterface nativeNet;flpMqttBlocks().control(&nativeNet,false,false,false,Broker,PortNumber,ClientID,User,Password,0,10);
 flpMqttBlocks().control(&nativeNet,true,false,false,Broker,PortNumber,ClientID,User,Password,0,10);assert(FLProgNetworkTcpClient::nativeBegin==1);flpMqttBlocks().mqtt.end();
 printf("PASS actual MQTT source + generated Core/Publish/Subscribe: CONNECT/auth/SUBSCRIBE/PUBLISH400/incoming/disconnect; native TCP untouched\n");
}
