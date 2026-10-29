#pragma once
#include <flprogNetwork.h>
#include "BridgeNetworkConfig.h"
// Uses FLProg_Network's existing socket/transport backends; no Ethernet driver here.
inline bool configureBridgeNetwork(FLProgNetworkInterface&network,const FLProgBridgeNetworkConfig&c,const char*ssid="",const char*password=""){
 if(!bridgeNetworkValid(c))return false;
 if(c.kind==FLProgBridgeNetworkConfig::Wifi){network.networkMode(FLPROG_NETWORK_MODE_WIFI);network.setClientSsid(ssid);network.setClientPassword(password);}
 else{network.networkMode(FLPROG_NETWORK_MODE_ETHERNET);network.wiznetMode(c.kind==FLProgBridgeNetworkConfig::Wiznet);network.rmiiMode(c.kind==FLProgBridgeNetworkConfig::RmiiLan8720);
  if(c.kind==FLProgBridgeNetworkConfig::Wiznet){network.setPinCs(c.cs);network.setSpiPins(c.sck,c.miso,c.mosi);network.setDhcp();}
  else{network.setRmiiPhyAddress(c.phy);network.setRmiiMdcPin(c.mdc);network.setRmiiMdioPin(c.mdio);network.setRmiiPowerPin(c.power);network.setRmiiResetPin(c.reset);network.setRmiiClockMode(c.clock);network.rmiiDhcpMode(true);}
 }network.workMode(true);network.connect();return true;
}
class FLProgBridgeNetworkEndpoint {
 FLProgNetworkTcpServer server_;FLProgNetworkTcpServerClient *client_=nullptr;uint32_t generation_=0;
public:
 bool begin(FLProgNetworkInterface&network,const FLProgBridgeNetworkConfig&c){if(!bridgeNetworkValid(c))return false;uint8_t route=c.kind==FLProgBridgeNetworkConfig::Wifi?FLPROG_NETWORK_ROUTE_WIFI:c.kind==FLProgBridgeNetworkConfig::Wiznet?FLPROG_NETWORK_ROUTE_WIZNET:FLPROG_NETWORK_ROUTE_RMII;return server_.beginChild(network,c.port,route,1);}
 void pool(){server_.pool();if(client_&&!client_->connected()){client_=nullptr;++generation_;}if(auto next=server_.takeNewClient()){if(client_&&client_!=next)next->stop();else{client_=next;++generation_;}}}
 uint32_t generation()const{return generation_;}bool connected()const{return client_&&client_->connected();}
 int available(){return connected()?client_->available():0;}int read(){return connected()?client_->read():-1;}
 size_t read(uint8_t*p,size_t n){if(!connected())return 0;int done=client_->read(p,n);return done>0?(size_t)done:0;}
 int room(){return availableForWrite();}
 int availableForWrite(){return connected()?64:0;}size_t write(const uint8_t*p,size_t n){return connected()?client_->write(p,n):0;}
 void stop(){if(client_){client_->stop();client_=nullptr;++generation_;}}
};
