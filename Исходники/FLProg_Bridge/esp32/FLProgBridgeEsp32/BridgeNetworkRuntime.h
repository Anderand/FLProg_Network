#pragma once
#include <WiFi.h>
#include "BridgeNetworkEndpoint.h"
static FLProgNetworkInterface bridgeNetwork;
static FLProgBridgeNetworkConfig::Kind activeNetworkKind=FLProgBridgeNetworkConfig::Wifi;
inline uint8_t bridgeNetworkRoute(){return activeNetworkKind==FLProgBridgeNetworkConfig::Wifi?FLPROG_NETWORK_ROUTE_WIFI:activeNetworkKind==FLProgBridgeNetworkConfig::Wiznet?FLPROG_NETWORK_ROUTE_WIZNET:FLPROG_NETWORK_ROUTE_RMII;}
inline bool bridgeNetworkReady(){return activeNetworkKind==FLProgBridgeNetworkConfig::Wifi?bridgeNetwork.wifiIsReady():activeNetworkKind==FLProgBridgeNetworkConfig::Wiznet?bridgeNetwork.wiznetIsReady():bridgeNetwork.rmiiHardware().isReady();}
inline String bridgeNetworkIPString(){return (activeNetworkKind==FLProgBridgeNetworkConfig::Wifi?bridgeNetwork.wifiIP():activeNetworkKind==FLProgBridgeNetworkConfig::Wiznet?bridgeNetwork.ethernetIP():bridgeNetwork.rmiiIP()).toString();}

inline const char*bridgeActiveNetworkName(){return activeNetworkKind==FLProgBridgeNetworkConfig::Wifi?"Wi-Fi":activeNetworkKind==FLProgBridgeNetworkConfig::Wiznet?"LAN · Wiznet SPI":"LAN · RMII LAN8720";}
