"""Compile the actual MQTT header and all implementation methods with platform stubs."""
from pathlib import Path
import re, subprocess, argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library',type=Path,default=Path(__file__).resolve().parent/'FLProg_Network')
parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'host')
parser.add_argument('--compiler',type=Path,default=Path(r'E:\FLP\Flprog_network\audit\host-tools\ziglang\zig.exe'))
args=parser.parse_args()
W=args.output.parent;L=args.library;T=args.output;T.mkdir(parents=True,exist_ok=True)
h=(L/'src/service/flprogNetworkMqttClient.h').read_text()
cpp=(L/'src/service/flprogNetworkMqttClient.cpp').read_text()
helper=(L/'src/flprogMqttUserBlocks.h').read_text(encoding='utf-8-sig')
helper=re.sub(r'^#include.*$','',helper,flags=re.M)
h=re.sub(r'^#include.*$', '', h, flags=re.M).replace('private:','public:')
cpp=re.sub(r'^#include.*$', '', cpp, flags=re.M)
pre=r'''
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <cassert>
#include <string>
#include <vector>
using String=std::string;
struct IPAddress { uint8_t bytes[4]; IPAddress(int a=0,int b=0,int c=0,int d=0):bytes{(uint8_t)a,(uint8_t)b,(uint8_t)c,(uint8_t)d}{} uint8_t operator[](int i)const{return bytes[i];} };
static uint32_t ticks=0; uint32_t millis(){return ticks;}
class FLProgNetworkInterface {};
class FLProgNetworkService {public: virtual ~FLProgNetworkService(){} virtual void pool(){} bool attach(FLProgNetworkInterface&){return true;} bool isAttached(){return true;} void detach(){} FLProgNetworkInterface* network(){static FLProgNetworkInterface n; return &n;} };
#define FLPROG_TCP_HOSTNAME_MAX_LENGTH 127
#define FLPROG_TCP_DNS_POLICY_PRIVATE 0
#define FLPROG_TCP_STATE_ERROR 9
#define FLPROG_TCP_ERROR_NONE 0
#define FLPROG_TCP_CLIENT_ERROR_NONE 0
#define FLPROG_SOCKET_STATE_ERROR 9
#define FLPROG_SOCKET_STATE_UNSUPPORTED 10
class FLProgNetworkTcpClient {public:
 bool begin(FLProgNetworkInterface&,uint8_t){return true;} void end(){} void setRoute(uint8_t){} void setAutoReconnect(bool){} void setReconnectOnInitialFailure(bool){} void setDnsPolicy(int){} void setNoDelay(bool){} void setTimeout(uint32_t){}
 bool connect(const char*,uint16_t){return true;} bool connect(IPAddress,uint16_t){return true;} bool connected(){return true;} bool busy(){return false;} uint8_t state(){return 0;} uint8_t error(){return 0;} uint8_t clientError()const{return 0;} void clearClientError(){} uint8_t dnsError()const{return 0;} void stop(){} void cancel(){} int available(){return 0;} int read(){return -1;} size_t write(const uint8_t*,size_t n){return n;}
};
static bool failAllocation=false;
static size_t allocatedBytes=0;
static void* testRealloc(void *p,size_t n){if(failAllocation)return nullptr;void* q=std::realloc(p,n);if(q)allocatedBytes=n;return q;}
static void testFree(void*p){if(p)allocatedBytes=0;std::free(p);}
#define realloc testRealloc
#define free testFree
'''
tests=r'''
void session(FLProgNetworkMqttClient& c){c._sessionConnected=true;c._state=FLPROG_MQTT_STATE_CONNECTED;}
void ack(FLProgNetworkMqttClient& c,uint8_t result=0){c._state=FLPROG_MQTT_STATE_WAIT_SUBACK;uint8_t b[]={(uint8_t)(c._waitingPacketId>>8),(uint8_t)c._waitingPacketId,result};assert(c.handleSuback(b,3));}
int main(){
 {
 FLProgNetworkMqttClient c; session(c);
 assert(c.subscriptionLimit()==0 && c.subscriptionMemoryBytes()==0);
 for(int i=0;i<300;i++){char name[40];std::snprintf(name,sizeof(name),"home/sensor/%d",i); assert(c.subscribe(name));ack(c);}
 assert(c.subscriptionCount()==300 && c.subscriptionMemoryBytes()==300*128);
 assert(!strcmp(c.subscription(299),"home/sensor/299"));
 assert(c.subscribe("home/sensor/1"));ack(c);assert(c.subscriptionCount()==300 && c.subscriptionMemoryBytes()==300*128);
 assert(!c.setSubscriptionLimit(299) && c.error()==17);assert(c.subscriptionLimit()==0);
 assert(c.setSubscriptionLimit(300));assert(!c.subscribe("extra") && c.error()==17);assert(c.subscribe("home/sensor/1"));ack(c);
 assert(c.setSubscriptionLimit(0));failAllocation=true;
 assert(!c.subscribe("oom") && c.error()==18 && c.subscriptionCount()==300);assert(!strcmp(c.subscription(299),"home/sensor/299"));
 failAllocation=false;assert(c.subscribe("retry"));assert(!c.setSubscriptionLimit(300));ack(c);assert(c.subscriptionCount()==301);
 for(int i=0;i<100;i++){assert(c.subscribe("rejected"));ack(c,0x80);assert(c.error()==11 && c.subscriptionCount()==301);}
 // Failed filter is never restored, retained memory is at most one spare slot.
 assert(c.subscriptionMemoryBytes()==302*128);
 c._state=FLPROG_MQTT_STATE_WAIT_CONNACK;uint8_t connack[]={0,0};assert(c.handleConnack(connack,2));assert(c._resubscribeActive);
 for(size_t i=0;i<301;i++){assert(c._resubscribeIndex==i);c.serviceConnectedIdle();assert(c._pendingSubscribeIsResubscribe);assert(!strcmp(c._pendingSubscribe,c.subscription(i)));ack(c);}
 assert(!c._resubscribeActive && c.subscriptionCount()==301);
 assert(!c.clearSubscriptions() && c.error()==1);
 c.end();assert(c.subscriptionCount()==301);assert(c.clearSubscriptions());assert(c.subscriptionCount()==0 && c.subscriptionMemoryBytes()==0 && allocatedBytes==0);
 session(c);assert(!c.subscribe("bad/#/x") && c.error()==14);assert(!c.subscribe("") && c.error()==14);
 assert(c.subscribe("+/sensor/#"));ack(c);
 }
 assert(allocatedBytes==0); // destructor frees retained filters
 {
 FLProgMqttUserBlocks b;FLProgNetworkInterface n;
 b.control(nullptr,true,false,false,"127.0.0.1",1883,"id","","",0);assert(b.error()==19);
 b.control(&n,true,true,false,"127.0.0.1",1883,"id","","",0);assert(b.error()==0);
 b.control(&n,false,false,false,"127.0.0.1",1883,"id","","",0);
 b.control(&n,true,false,false,"127.0.0.1",0,"id","","",0);assert(b.error()==20);
 assert(b.matches("home/+/temp","home/room/temp"));assert(!b.matches("home/+/temp","home/room/humidity"));
 assert(!b.matches("#","$SYS/broker"));assert(b.matches("home/#","home"));
 }
 puts("PASS: 300 subscriptions, duplicate, optional limit, pending limit, OOM/retry, SUBACK rejection, 301 reconnect filters, clear/end/destructor, invalid filters");
 puts("PASS: Core missing interface, reconnect configuration, invalid port, MQTT wildcard matching");
}
'''
(T/'tests.cpp').write_text(pre+'\n'+h+'\n'+cpp+'\n'+helper+'\n'+tests,encoding='utf-8')
zig=args.compiler
subprocess.run([str(zig),'c++','-std=c++11','-O0','-Wall','-Wextra',str(T/'tests.cpp'),'-o',str(T/'tests.exe')],check=True)
r=subprocess.run([str(T/'tests.exe')],capture_output=True,text=True);print(r.stdout,r.stderr)
(W/'MQTT_HOST_RESULTS.md').write_text('# Host-проверка MQTT\n\n```\n'+r.stdout+r.stderr+'```\n',encoding='utf-8')
raise SystemExit(r.returncode)
