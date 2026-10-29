// Compile-only prototype: native FLProg_Network Wi-Fi OR Wiznet OR RMII.
// No network credentials or PLC project are embedded. No physical flashing authorized.
#include <flprogNetwork.h>
#include <Preferences.h>
static_assert(FLPROG_NETWORK_COMPILE_WIFI && FLPROG_NETWORK_COMPILE_WIRED,"Full network profile required");
static_assert(FLPROG_NETWORK_COMPILED_RMII,"Classic ESP32 EMAC/LAN8720 support required");
#include "BridgeNetworkEndpoint.h"
#include "BridgeModbusTcp.h"
#include "BoundedRelay.h"
FLProgNetworkInterface bridgeNetwork;
FLProgBridgeNetworkConfig bridgeConfig;
FLProgBridgeNetworkEndpoint bridgeEndpoint;
FLProgModbusClient bridgeClient;
FLProgModbusTcpSession gateway(bridgeClient);
HardwareSerial plc(2);
FLProgBoundedRelay rawRelay;
struct UartRelayPort{int available(){return plc.available();}size_t read(uint8_t*p,size_t n){size_t at=0;while(at<n&&plc.available()>0){int b=plc.read();if(b<0)break;p[at++]=b;}return at;}int room(){return plc.availableForWrite();}size_t write(const uint8_t*p,size_t n){return plc.write(p,n);}} rawUart;
bool started=false;
void setup(){
 Preferences preferences;preferences.begin("flpbridge-lan",true);
 bridgeConfig.service=(FLProgBridgeNetworkConfig::Service)preferences.getUChar("service",1);
 bridgeConfig.port=bridgeConfig.service==FLProgBridgeNetworkConfig::RawBridge?3234:502;
 bridgeConfig.kind=(FLProgBridgeNetworkConfig::Kind)preferences.getUChar("network",1);
 bridgeConfig.sck=preferences.getChar("sck",18);bridgeConfig.miso=preferences.getChar("miso",19);bridgeConfig.mosi=preferences.getChar("mosi",23);bridgeConfig.cs=preferences.getChar("cs",5);
 bridgeConfig.uartRx=preferences.getUChar("rx",32);bridgeConfig.uartTx=preferences.getUChar("tx",33);bridgeConfig.baud=preferences.getUInt("baud",115200);
 bridgeConfig.mdc=preferences.getChar("mdc",23);bridgeConfig.mdio=preferences.getChar("mdio",18);bridgeConfig.power=preferences.getChar("power",-1);bridgeConfig.reset=preferences.getChar("reset",-1);bridgeConfig.phy=preferences.getUChar("phy",0);bridgeConfig.clock=preferences.getUChar("clock",0);
 String ssid=preferences.getString("ssid",""),password=preferences.getString("password","");preferences.end();
 uint64_t id=ESP.getEfuseMac();uint8_t mac[6]={2,(uint8_t)id,(uint8_t)(id>>8),(uint8_t)(id>>16),(uint8_t)(id>>24),(uint8_t)(id>>32)};bridgeNetwork.mac(mac);
 if(!configureBridgeNetwork(bridgeNetwork,bridgeConfig,ssid.c_str(),password.c_str()))return;
 plc.begin(bridgeConfig.baud,SERIAL_8N1,bridgeConfig.uartRx,bridgeConfig.uartTx);started=bridgeEndpoint.begin(bridgeNetwork,bridgeConfig);
}
void loop(){
 if(!started)return;bridgeNetwork.pool();bridgeEndpoint.pool();
 static uint32_t generation=0;if(generation!=bridgeEndpoint.generation()){gateway.disconnect();rawRelay.reset();generation=bridgeEndpoint.generation();if(bridgeEndpoint.connected())gateway.begin(millis());}
 if(!bridgeEndpoint.connected())return;
 if(bridgeConfig.service==FLProgBridgeNetworkConfig::RawBridge){rawRelay.poll(bridgeEndpoint,rawUart);return;}
 uint64_t nonce=((uint64_t)esp_random()<<32)|esp_random();if(!nonce)nonce=1;
 // In combined firmware uartFree must also account for WebUI/raw ownership.
 gateway.pool(bridgeEndpoint,plc,millis(),true,nonce);
}
