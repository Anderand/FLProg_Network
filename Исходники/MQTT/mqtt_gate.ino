#include <flprogEthernet.h>
#include <flprogMqttUserBlocks.h>
FLProgWiznetInterface mqttEthernet(PB12,0);
#define FLPROG_WIZNET_INTERFACE1 mqttEthernet
bool EN=false, CON=false, DIS=false, Connected, Busy, Error;
long NET_KIND=1,NET_NUM=1,SUB_LIMIT=0, Port=1883,ERR,State,Subscriptions,SubBytes;
String Broker="127.0.0.1",ClientID="compile-only",User="",Password="";
bool Send=false,Retain=false,Accepted,Subscribe=false,Received,Retained;
String Topic="home/+/value",Message="42",RxTopic;
bool mqttPrevSend=false,mqttPrevSub=false;uint32_t mqttSeen=0;
void setup() { }
void loop() {
 mqttEthernet.pool();
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
flpMqttBlocks().control(mqttSelectedNetwork, EN, CON, DIS, Broker, Port, ClientID, User, Password, SUB_LIMIT);
Connected = flpMqttBlocks().mqtt.connected();
Busy = flpMqttBlocks().mqtt.busy();
ERR = flpMqttBlocks().error();
Error = ERR != 0;
State = flpMqttBlocks().mqtt.state();
Subscriptions = (long)flpMqttBlocks().mqtt.subscriptionCount();
SubBytes = (long)flpMqttBlocks().mqtt.subscriptionMemoryBytes();
Accepted = false;
if (Send && !mqttPrevSend) {
    Accepted = flpMqttBlocks().mqtt.publish(Topic.c_str(), Message.c_str(), Retain);
    ERR = flpMqttBlocks().mqtt.error();
}
mqttPrevSend = Send;
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
