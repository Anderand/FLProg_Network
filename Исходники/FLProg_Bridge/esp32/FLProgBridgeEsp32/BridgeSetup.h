#pragma once
// Platform supplies BridgeWebServer, Preferences, WiFi, Serial, ESP and network helpers.
#include "BridgeConfig.h"
#include "BridgeSetupPage.h"
static FLProgBridgeConfig config;
static BridgeWebServer setupServer(80);
static bool setupMode=false,adminStarted=false;
static String setupToken,adminPassword,adminSession;
static bool authorizedSettings(){
 if(setupMode || (adminSession.length()==32&&setupServer.header("Cookie").indexOf("flpadmin="+adminSession)>=0))return true;
 setupServer.sendHeader("Cache-Control","no-store");
 if(setupServer.method()!=HTTP_GET){setupServer.send(403,"text/plain; charset=utf-8","Войдите в настройки ESP");return false;}
 setupServer.send(200,"text/html; charset=utf-8","<!doctype html><html lang=ru><meta charset=utf-8><meta name=viewport content=width=device-width><title>Настройки ESP</title><h1>FLProg Bridge · вход</h1><form method=post action=/login><label>Пароль настроек ESP<input name=password type=password required autocomplete=current-password></label><button>Войти</button></form></html>");return false;
}
#include "BridgePlcHttp.h"
#include "BridgeProjectHttp.h"
static uint32_t restartAt=0;static bool restartPending=false;
static bool loadConfig(){
 Preferences p;if(!p.begin("flpbridge",true))return false;bool ok=false;
 if(p.getBytesLength("config2")){ok=p.getBytesLength("config2")==sizeof(config)&&p.getBytes("config2",&config,sizeof(config))==sizeof(config)&&bridgeConfigValid(config,psramFound());}
 else{FLProgBridgeConfigV1 legacy;if(p.getBytesLength("config")==sizeof(legacy)&&p.getBytes("config",&legacy,sizeof(legacy))==sizeof(legacy)&&legacy.version==1){FLProgBridgeConfig next;static_cast<FLProgBridgeConfigV1&>(next)=legacy;next.version=2;if(bridgeConfigValid(next,psramFound())){config=next;ok=true;}}}
 p.end();return ok;
}
static String bridgeJsonQuote(const char*p){String s="\"";for(;*p;++p){unsigned char c=*p;if(c=='"'||c=='\\'){s+='\\';s+=(char)c;}else if(c<32){char code[7];snprintf(code,sizeof(code),"\\u%04x",(unsigned)c);s+=code;}else s+=(char)c;}s+='"';return s;}
static String bridgeSettingsJson(){
 String s="{\"token\":"+bridgeJsonQuote(setupToken.c_str())+",\"ssid\":"+bridgeJsonQuote(config.ssid)+",\"passwordStored\":"+(strlen(config.password)?"true":"false")+",\"setupMode\":"+(setupMode?"true":"false")+",\"activeName\":"+bridgeJsonQuote(setupMode?"Точка настройки":bridgeActiveNetworkName())+",\"ip\":"+bridgeJsonQuote((setupMode?WiFi.softAPIP().toString():bridgeNetworkIPString()).c_str())+",\"projectPort\":8081";
 auto number=[&](const char*k,long v){s+=",\"";s+=k;s+="\":";s+=String(v);};
 number("service",config.network.service);number("network",config.network.kind);number("rx",config.rx);number("tx",config.tx);number("baud",config.baud);number("format",config.format);number("port",config.port);number("idle",config.idleMs);
 number("sck",config.network.sck);number("miso",config.network.miso);number("mosi",config.network.mosi);number("cs",config.network.cs);number("mdc",config.network.mdc);number("mdio",config.network.mdio);number("power",config.network.power);number("reset",config.network.reset);number("phy",config.network.phy);number("clock",config.network.clock);s+='}';return s;
}
static bool bridgeOptionalPin(const char*key,int8_t&value,bool optional=false){if(!setupServer.hasArg(key))return true;String s=setupServer.arg(key);if(optional&&s=="-1"){value=-1;return true;}uint32_t n;if(!bridgeUnsigned(s.c_str(),n)||n>39)return false;value=(int8_t)n;return true;}
static void beginSettingsWeb(bool ap){
 setupMode=ap;if(ap)WiFi.mode(WIFI_AP);
 Preferences p;p.begin("flpbridge",false);String password=p.getString("setupKey","");if(password.length()<8||password.length()>63){char value[17];snprintf(value,sizeof(value),"%08lx%08lx",(unsigned long)esp_random(),(unsigned long)esp_random());password=value;p.putString("setupKey",password);}p.end();adminPassword=password;
 char session[33];snprintf(session,sizeof(session),"%08lx%08lx%08lx%08lx",(unsigned long)esp_random(),(unsigned long)esp_random(),(unsigned long)esp_random(),(unsigned long)esp_random());adminSession=session;
 char token[17];snprintf(token,sizeof(token),"%08lx%08lx",(unsigned long)esp_random(),(unsigned long)esp_random());setupToken=token;
 char name[32];snprintf(name,sizeof(name),"FLProgBridge-%06lx",(unsigned long)(ESP.getEfuseMac()&0xffffff));if(ap&&!WiFi.softAP(name,password.c_str(),1,false,1))return;
 if(ap)Serial.printf("Setup Wi-Fi: %s\nSetup password: %s\nOpen http://192.168.4.1/\n",name,password.c_str());
 const char*headers[]={"Cookie"};setupServer.collectHeaders(headers,1);
 setupServer.on("/login",HTTP_POST,[]{if(setupServer.arg("password")!=adminPassword){setupServer.send(403,"text/plain; charset=utf-8","Неверный пароль настроек ESP");return;}setupServer.sendHeader("Cache-Control","no-store");setupServer.sendHeader("Set-Cookie","flpadmin="+adminSession+"; Path=/; HttpOnly; SameSite=Strict");setupServer.sendHeader("Location","/");setupServer.send(303);});
 setupServer.on("/",HTTP_GET,[]{if(!authorizedSettings())return;setupServer.send_P(200,"text/html; charset=utf-8",FLPROG_SETTINGS_PAGE);});
 setupServer.on("/config",HTTP_GET,[]{if(!authorizedSettings())return;setupServer.sendHeader("Cache-Control","no-store");setupServer.send(200,"application/json; charset=utf-8",bridgeSettingsJson());});
 setupServer.on("/save",HTTP_POST,[]{
  if(!authorizedSettings())return;if(setupServer.arg("token")!=setupToken){setupServer.send(403,"text/plain; charset=utf-8","Недействительный сеанс настройки");return;}
  auto error=[](const char*text){setupServer.send(400,"text/plain; charset=utf-8",text);};
  String apPassword=setupServer.arg("setupPassword");if(apPassword.length()&&(apPassword.length()<8||apPassword.length()>63)){error("Пароль точки настройки: от 8 до 63 байт");return;}
  FLProgBridgeConfig next=config;uint32_t kind=next.network.kind,service=next.network.service,rx,tx,baud,format,port,idle;
  if((setupServer.hasArg("service")&&(!bridgeUnsigned(setupServer.arg("service").c_str(),service)||service>2))||(setupServer.hasArg("network")&&(!bridgeUnsigned(setupServer.arg("network").c_str(),kind)||kind>2))||!bridgeUnsigned(setupServer.arg("rx").c_str(),rx)||!bridgeUnsigned(setupServer.arg("tx").c_str(),tx)||!bridgeUnsigned(setupServer.arg("baud").c_str(),baud)||!bridgeUnsigned(setupServer.arg("format").c_str(),format)||!bridgeUnsigned(setupServer.arg("port").c_str(),port)||!bridgeUnsigned(setupServer.arg("idle").c_str(),idle)||rx>255||tx>255||format>5||port>65535){error("Неверные числовые настройки");return;}
  next.network.service=(FLProgBridgeNetworkConfig::Service)service;next.network.kind=(FLProgBridgeNetworkConfig::Kind)kind;next.rx=rx;next.tx=tx;next.baud=baud;next.format=format;next.port=port;next.idleMs=idle;
  if(!bridgeOptionalPin("sck",next.network.sck)||!bridgeOptionalPin("miso",next.network.miso)||!bridgeOptionalPin("mosi",next.network.mosi)||!bridgeOptionalPin("cs",next.network.cs)||!bridgeOptionalPin("mdc",next.network.mdc)||!bridgeOptionalPin("mdio",next.network.mdio)||!bridgeOptionalPin("power",next.network.power,true)||!bridgeOptionalPin("reset",next.network.reset,true)){error("Неверные GPIO сети");return;}
  uint32_t phy=next.network.phy,clock=next.network.clock;if((setupServer.hasArg("phy")&&(!bridgeUnsigned(setupServer.arg("phy").c_str(),phy)||phy>31))||(setupServer.hasArg("clock")&&(!bridgeUnsigned(setupServer.arg("clock").c_str(),clock)||clock>3))){error("Неверные параметры PHY");return;}next.network.phy=phy;next.network.clock=clock;
  if(setupServer.hasArg("ssid")){String ssid=setupServer.arg("ssid"),pass=setupServer.arg("password");if(ssid.length()>32||pass.length()>63){error("Неверная длина сети или пароля");return;}if(setupServer.hasArg("open"))pass="";else if(pass.isEmpty()&&ssid==config.ssid)pass=config.password;else if(pass.isEmpty()){error("Укажите пароль или отметьте открытую сеть");return;}ssid.toCharArray(next.ssid,sizeof(next.ssid));pass.toCharArray(next.password,sizeof(next.password));}
  if(!bridgeConfigValid(next,psramFound())){error("Недопустимые GPIO или их пересечение с UART/сетью, скорость, порт либо пароль");return;}
  Preferences store;bool ok=store.begin("flpbridge",false);if(ok){ok=store.putBytes("config2",&next,sizeof(next))==sizeof(next);if(ok&&apPassword.length())ok=store.putString("setupKey",apPassword)==apPassword.length();store.end();}
  if(!ok){setupServer.send(500,"text/plain; charset=utf-8","Не удалось сохранить настройки");return;}
  setupServer.send(200,"text/plain; charset=utf-8","Сохранено. После перезапуска мост подключится к выбранной сети. Адрес LAN выдаст DHCP. Найдите новый IP в роутере или USB-консоли.");restartAt=millis()+1500;restartPending=true;
 });
 registerPlcReadHttpRoutes();adminStarted=setupServer.begin(ap?80:8080);
}
static void beginSetup(){beginSettingsWeb(true);}
static void pollSettings(){if(!adminStarted&&bridgeNetworkReady())beginSettingsWeb(false);if(adminStarted)setupServer.handleClient();if(restartPending&&(int32_t)(millis()-restartAt)>=0)ESP.restart();}
