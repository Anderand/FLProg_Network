#include "lan_web_native_adapter.h"
int main(){
 static_assert(sizeof(FLProgBridgeConfigV1)==120,"Legacy record");
 FLProgBridgeConfigV1 old;strcpy(old.ssid,"stand-wifi");strcpy(old.password,"saved-demo-pass");Preferences p;p.begin("flpbridge",false);p.putBytes("config",&old,sizeof(old));p.putString("setupKey","demo12345");p.end();auto legacy=fakePrefs.blobs["flpbridge/config"];int writes=fakePrefs.writes;
 assert(loadConfig()&&config.version==2&&config.network.kind==FLProgBridgeNetworkConfig::Wifi);assert(fakePrefs.writes==writes&&fakePrefs.blobs["flpbridge/config"]==legacy&&fakePrefs.blobs["flpbridge/config2"].empty());
 beginSettingsWeb(false);setupServer.invoke("/config",HTTP_GET);assert(setupServer.code==200&&setupServer.body.find("type=password")!=std::string::npos);
 setupServer.headers["Cookie"]="flpadmin="+adminSession;setupServer.invoke("/config",HTTP_GET);assert(setupServer.code==200&&setupServer.body.find("saved-demo-pass")==std::string::npos&&setupServer.body.find("passwordStored\":true")!=std::string::npos);
 setupServer.args={{"token","wrong"},{"network","1"},{"rx","16"},{"tx","17"},{"baud","115200"},{"format","0"},{"port","3234"},{"idle","60000"}};writes=fakePrefs.writes;setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==403&&fakePrefs.writes==writes);
 setupServer.args["token"]=setupToken;setupServer.args["sck"]="16";setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==400&&fakePrefs.writes==writes);
 setupServer.args["sck"]="18";setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==200&&restartPending&&fakePrefs.blobs["flpbridge/config"]==legacy);assert(loadConfig()&&config.network.kind==FLProgBridgeNetworkConfig::Wiznet&&!strcmp(config.password,"saved-demo-pass"));
 activeNetworkKind=config.network.kind;WiFi.value=0;assert(bridgeNetworkReady());beginProjectServer();projectServer.headers["Cookie"]="flpadmin="+adminSession;projectServer.invoke("/",HTTP_GET);assert(projectServer.code==200&&projectServer.body.size()>20000);
 wiredReady[1]=false;projectServer.invoke("/plc-api/session",HTTP_GET);assert(projectServer.code==503);wiredReady[1]=true;
 setupServer.args={{"token",setupToken},{"network","2"},{"rx","16"},{"tx","17"},{"baud","115200"},{"format","0"},{"port","3234"},{"idle","60000"},{"clock","2"}};writes=fakePrefs.writes;setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==400&&fakePrefs.writes==writes);
 setupServer.args["rx"]="32";setupServer.args["tx"]="33";setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==200&&loadConfig()&&config.network.kind==FLProgBridgeNetworkConfig::RmiiLan8720);activeNetworkKind=config.network.kind;assert(bridgeNetworkReady());
 // Respect stored service; same schema and record size remain backward-compatible.
 setupServer.args["service"]="1";setupServer.args["port"]="502";setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==200&&loadConfig()&&config.network.service==FLProgBridgeNetworkConfig::ModbusTcp&&bridgeTransportConfig(config).service==FLProgBridgeNetworkConfig::ModbusTcp&&config.port==502);
 setupServer.invoke("/config",HTTP_GET);assert(setupServer.body.find("service\":1")!=std::string::npos);
 for(unsigned kind=0;kind<3;++kind){setupServer.args["network"]=String(kind);setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==200&&loadConfig()&&config.network.service==FLProgBridgeNetworkConfig::ModbusTcp&&config.network.kind==kind&&!strcmp(config.password,"saved-demo-pass"));}
 setupServer.args["service"]="3";writes=fakePrefs.writes;setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==400&&fakePrefs.writes==writes);
 setupServer.args["service"]="0";setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==400); // raw cannot use privileged port502
 setupServer.args["service"]="1";setupServer.args["port"]="8081";setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==400);
 setupServer.args["service"]="0";setupServer.args["port"]="3234";
 setupServer.args["service"]="2";setupServer.args["port"]="3234";setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==200&&loadConfig()&&config.network.service==FLProgBridgeNetworkConfig::PlcTcpClient);
 setupServer.args["service"]="0";
 fakePrefs.fail=true;setupServer.args["network"]="0";setupServer.args.erase("clock");writes=fakePrefs.writes;setupServer.invoke("/save",HTTP_POST);assert(setupServer.code==500&&fakePrefs.writes==writes);fakePrefs.fail=false;
 setupMode=true;projectServer.invoke("/plc-api/session",HTTP_GET);assert(projectServer.code==503);setupMode=false;
 printf("PASS settings V1->V2 migration without write, auth/CSRF, no password echo, WiFi preserved across LAN saves, GPIO conflicts, W5500/RMII readiness without WiFi, Flash8081, NVS failure; V1=%zu V2=%zu\n",sizeof(old),sizeof(config));
}
