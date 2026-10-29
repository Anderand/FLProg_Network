#include "BridgeNetworkEndpoint.h"
#include <cassert>
#include <cstdio>
int main(){for(int kind=0;kind<3;kind++){FLProgBridgeNetworkConfig c;c.kind=(FLProgBridgeNetworkConfig::Kind)kind;FLProgNetworkInterface network;
 assert(configureBridgeNetwork(network,c,"test-ssid","not-a-real-password"));assert(network.work&&network.connected);
 if(kind==0)assert(network.mode==0&&network.ssid=="test-ssid");
 if(kind==1)assert(network.mode==1&&network.wiz&&!network.rmii&&network.dhcp&&network.cs==5&&network.sck==18&&network.miso==19&&network.mosi==23);
 if(kind==2)assert(network.mode==1&&!network.wiz&&network.rmii&&network.dhcp&&network.phy==0&&network.mdc==23&&network.mdio==18&&network.clock==0);
 FLProgBridgeNetworkEndpoint endpoint;assert(endpoint.begin(network,c));auto server=FLProgNetworkTcpServer::last;assert(server->port==502&&server->route==(kind==0?1:kind==1?4:5)&&server->capacity==1);
 assert(!endpoint.connected());server->peer.live=true;server->pending=true;endpoint.pool();assert(endpoint.connected()&&endpoint.generation()==1);assert(endpoint.available()==1&&endpoint.read()==42);uint8_t b[64]{};assert(endpoint.write(b,64)==3);server->peer.live=false;endpoint.pool();assert(!endpoint.connected()&&endpoint.generation()==2);
 c.uartRx=c.uartTx;assert(!configureBridgeNetwork(network,c));}
 FLProgBridgeNetworkConfig raw;raw.service=FLProgBridgeNetworkConfig::RawBridge;raw.port=3234;assert(bridgeNetworkValid(raw));
 FLProgBridgeNetworkConfig c;c.kind=FLProgBridgeNetworkConfig::RmiiLan8720;c.mdc=19;assert(!bridgeNetworkValid(c));c.mdc=23;c.clock=2;c.uartRx=16;assert(!bridgeNetworkValid(c));
 puts("PASS actual endpoint/config adapter with network API double: WiFi/Wiznet/RMII routes, DHCP, pins, one client, partial write, disconnect generation, conflicts");
}
