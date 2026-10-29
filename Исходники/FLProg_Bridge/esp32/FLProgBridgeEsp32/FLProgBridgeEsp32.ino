// Universal bridge0.12: WebUI/settings/raw TCP through FLProg_Network Wi-Fi or LAN.
#include <Preferences.h>
#include "BridgeNetworkRuntime.h"
#include "BridgeHttpAdapter.h"
#include "BoundedRelay.h"
#include "BridgeSetup.h"
#include "BridgeModbusRuntime.h"
#include "BridgeTcpProxy.h"
struct ProxySocket {
 FLProgNetworkTcpClient tcp;
 bool begin(){bool ok=tcp.begin(bridgeNetwork,bridgeNetworkRoute());tcp.setAutoReconnect(false);tcp.setReconnectOnInitialFailure(false);tcp.setTimeout(8000);return ok;}
 void open(const char*h,uint16_t p){tcp.connect(h,p);}
 bool failed(){return tcp.clientError()!=0;}bool connected(){return tcp.connected();}
 int available(){return tcp.available();}int read(){return tcp.read();}
 size_t write(const uint8_t*p,size_t n){return tcp.write(p,n);}
 void stop(){tcp.stop();tcp.clearClientError();}
} proxySocket;
FLProgBridgeTcpProxy tcpProxy;
FLProgBridgeSharedSession uartSession;
#if !defined(CONFIG_IDF_TARGET_ESP32)
#error "Select classic ESP32 WROOM; RMII requires EMAC"
#endif
static_assert(FLPROG_NETWORK_COMPILE_WIFI && FLPROG_NETWORK_COMPILE_WIRED && FLPROG_NETWORK_COMPILED_RMII,"Full Wi-Fi/Wired/EMAC profile required");
HardwareSerial plc(2);
FLProgBridgeNetworkEndpoint rawEndpoint;
FLProgBoundedRelay relay;
FLProgBridgeModbusRuntime modbusRuntime;
bool tcpBridgeBusy(){return rawEndpoint.connected();}
uint32_t lastProgress=0;
struct NetworkEnd{
 size_t moved=0;int available(){return rawEndpoint.available();}size_t read(uint8_t*p,size_t n){size_t done=rawEndpoint.read(p,n);moved+=done;return done;}int room(){return rawEndpoint.room();}size_t write(const uint8_t*p,size_t n){size_t done=rawEndpoint.write(p,n);moved+=done;return done;}
};
struct UartEnd{int available(){return plc.available();}size_t read(uint8_t*p,size_t n){size_t at=0;while(at<n&&plc.available()>0){int b=plc.read();if(b<0)break;p[at++]=b;}return at;}int room(){return plc.availableForWrite();}size_t write(const uint8_t*p,size_t n){return plc.write(p,n);}};
void setup(){
 Serial.begin(115200);pinMode(0,INPUT_PULLUP);bool configured=loadConfig(),requested=false;uint32_t held=0,started=millis();Serial.println("FLProg Bridge universal0.12 Wi-Fi/LAN. Hold BOOT after normal boot for recovery AP.");
 while(configured&&(uint32_t)(millis()-started)<5000){if(digitalRead(0)==LOW){if(!held)held=millis();if((uint32_t)(millis()-held)>=1000){requested=true;break;}}else held=0;delay(10);}
 if(!configured||requested){if(!configured)config=FLProgBridgeConfig();beginSetup();return;}
 const uint32_t formats[]={SERIAL_8N1,SERIAL_8N2,SERIAL_8E1,SERIAL_8E2,SERIAL_8O1,SERIAL_8O2};plc.begin(config.baud,formats[config.format],config.rx,config.tx);
 if(config.network.service==FLProgBridgeNetworkConfig::PlcTcpClient){tcpProxy.bindSession(uartSession);plcReadJob.client.bindSession(uartSession);}
 activeNetworkKind=config.network.kind;auto selected=bridgeTransportConfig(config);uint64_t id=ESP.getEfuseMac();uint8_t mac[6]={2,(uint8_t)id,(uint8_t)(id>>8),(uint8_t)(id>>16),(uint8_t)(id>>24),(uint8_t)(id>>32)};bridgeNetwork.mac(mac);
 if(!configureBridgeNetwork(bridgeNetwork,selected,config.ssid,config.password)||!(selected.service==FLProgBridgeNetworkConfig::PlcTcpClient?proxySocket.begin():rawEndpoint.begin(bridgeNetwork,selected))){beginSetup();return;}
}
void loop(){
 if(setupMode){pollSettings();return;}
 bridgeNetwork.pool();pollSettings();pollProjectServer();rawEndpoint.pool();
 static NetworkEnd net;static UartEnd uart;static uint32_t generation=0;static String lastIP;static uint32_t ipChecked=0;
 if(!bridgeNetworkReady()){rawEndpoint.stop();modbusRuntime.stop();tcpProxy.stop(proxySocket);relay.reset();plcReadJob.client.cancel();viewerLease.clear();commandPermit=false;return;}
 if((uint32_t)(millis()-ipChecked)>=1000){ipChecked=millis();String ip=bridgeNetworkIPString();if(ip!=lastIP){Serial.println(ip);lastIP=ip;}}
 if(config.network.service==FLProgBridgeNetworkConfig::PlcTcpClient){if(plcReadJob.client.busy()&&!tcpProxy.ownsUart()){tcpProxy.pool(proxySocket,plc,plcReadJob.client,millis(),true,false,1);plcReadJob.client.pool(plc,millis(),64);return;}uint64_t nonce=((uint64_t)esp_random()<<32)|esp_random();tcpProxy.pool(proxySocket,plc,plcReadJob.client,millis(),true,false,nonce?nonce:1);return;}
 if(plcReadJob.client.busy()){rawEndpoint.stop();modbusRuntime.stop();relay.reset();plcReadJob.client.pool(plc,millis(),64);return;}
 if(viewerLease.active(millis())){rawEndpoint.stop();modbusRuntime.stop();relay.reset();for(int i=0;i<64&&plc.available()>0;++i)plc.read();return;}
 if(config.network.service==FLProgBridgeNetworkConfig::ModbusTcp){uint64_t nonce=((uint64_t)esp_random()<<32)|esp_random();modbusRuntime.pool(rawEndpoint,plc,plcReadJob.client,millis(),true,false,nonce?nonce:1);return;}
 if(generation!=rawEndpoint.generation()){generation=rawEndpoint.generation();relay.reset();plcReadJob.client.invalidateSession();lastProgress=millis();}
 if(!rawEndpoint.connected()){relay.reset();for(int i=0;i<64&&plc.available()>0;++i)plc.read();return;}
 size_t before=net.moved;relay.poll(net,uart);if(before!=net.moved)lastProgress=millis();if(config.idleMs&&(uint32_t)(millis()-lastProgress)>config.idleMs){rawEndpoint.stop();modbusRuntime.stop();relay.reset();}
}
