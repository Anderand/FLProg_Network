#pragma once
#include "BridgeHttpReadJob.h"
#include "BridgeReadPage.h"
#include "BridgeViewerLease.h"
bool tcpBridgeBusy();
static FLProgHttpReadJob plcReadJob;
static FLProgViewerLease viewerLease;
template<class Http> static void plcReplyFor(Http &http,int code,const String &json){http.sendHeader("Cache-Control","no-store");http.send(code,"application/json; charset=utf-8",json);}
template<class Http> static bool plcAllowedFor(Http &http){
    if(setupMode || !bridgeNetworkReady()){plcReplyFor(http,503,F("{\"error\":\"Сеть моста пока недоступна\"}"));return false;}
    if(adminSession.length()!=32 || http.header("Cookie").indexOf("flpadmin="+adminSession)<0){plcReplyFor(http,403,F("{\"error\":\"Войдите в настройки ESP на порту8080\"}"));return false;}
    return true;
}
static String plcSessionHex(){String s;const char *hex="0123456789abcdef";uint64_t v=plcReadJob.client.session();for(int i=15;i>=0;--i)s+=hex[(v>>(i*4))&15];return s;}
static bool parseChannelList(const char *p,uint8_t *out,uint8_t &size){
    size=0;if(!p || !*p)return false;
    while(*p){if(size==16)return false;unsigned n=0;bool any=false;
        while(*p && *p!=','){if(*p<'0'||*p>'9')return false;n=n*10+(*p++-'0');if(n>255)return false;any=true;}
        if(!any)return false;for(uint8_t i=0;i<size;++i)if(out[i]==n)return false;out[size++]=(uint8_t)n;
        if(*p==','){++p;if(!*p)return false;}
    }return true;
}
static bool commandPermit=false;
static uint64_t permitSession=0;
static uint32_t lastCommandId=0;
static bool commandsEnabled(){return commandPermit && plcReadJob.client.hasSession() && permitSession==plcReadJob.client.session();}
static bool parseCommandHex(const String &s,uint8_t *out,uint8_t &size){
    if(s.length()<4 || s.length()>130 || s.length()%2)return false;size=s.length()/2;
    for(uint8_t i=0;i<size;++i){unsigned v=0;for(uint8_t j=0;j<2;++j){char c=s[i*2+j];int n=c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;if(n<0)return false;v=v*16+n;}out[i]=(uint8_t)v;}
    return FLProgReadClient::validCommand(out,size);
}
template<class Http> static void registerReadRpc(Http &http,const String &token,bool viewer=false){
    http.on("/plc-api/session",HTTP_GET,[&http,&token,viewer]{
        if(!plcAllowedFor(http))return;
        String json=F("{\"token\":\"");json+=token;json+=F("\",\"readOnly\":");json+=(viewer && commandsEnabled())?"false":"true";json+=F(",\"ready\":");json+=plcReadJob.client.hasSession()?"true":"false";
        json+=F(",\"session\":\"");json+=plcSessionHex();json+=F("\"}");plcReplyFor(http,200,json);
    });
    http.on("/plc-api/control",HTTP_POST,[&http,&token,viewer]{
        if(!plcAllowedFor(http))return;
        if(!viewer || http.arg("token")!=token){plcReplyFor(http,403,F("{\"error\":\"Управление доступно только из веба ПЛК\"}"));return;}
        String enabled=http.arg("enable");if(enabled!="0" && enabled!="1"){plcReplyFor(http,400,F("{\"error\":\"Требуется enable0/1\"}"));return;}
        if(enabled=="1" && (!plcReadJob.client.hasSession() || http.arg("session")!=plcSessionHex() || !viewerLease.touch(millis(),tcpBridgeBusy()))){plcReplyFor(http,409,F("{\"error\":\"Требуется свежий сеанс ПЛК и свободный UART\"}"));return;}
        commandPermit=enabled=="1";permitSession=commandPermit?plcReadJob.client.session():0;
        plcReplyFor(http,200,String(F("{\"enabled\":"))+(commandsEnabled()?"true":"false")+F(",\"nextId\":")+String(lastCommandId==0xffffffffUL?0:lastCommandId+1)+F("}"));
    });
    http.on("/plc-api/start",HTTP_POST,[&http,&token,viewer]{
        if(!plcAllowedFor(http))return;
        if(http.arg("token")!=token){plcReplyFor(http,403,F("{\"error\":\"Недействительный токен формы\"}"));return;}
        if(viewer ? !viewerLease.touch(millis(),tcpBridgeBusy()) : viewerLease.active(millis())){plcReplyFor(http,409,F("{\"error\":\"UART занят другим мостом\"}"));return;}
        String op=http.arg("op");uint8_t kind=op=="hello"?1:op=="read"?2:op=="meta"?3:op=="resources"?4:0;
        uint32_t channel=0;int code=400;
        if(kind && bridgeUnsigned(http.arg("channel").c_str(),channel) && channel<=255){
            uint64_t session=((uint64_t)esp_random()<<32)|esp_random();if(!session)session=1;
            code=plcReadJob.start(kind,(uint16_t)channel,millis(),session,tcpBridgeBusy());
        }else if(op=="write"){
            if(!viewer || !commandsEnabled()){plcReplyFor(http,403,F("{\"error\":\"Запись отключена; включите для текущего сеанса\"}"));return;}
            uint32_t id=0;uint8_t data[65],size=0;
            if(http.arg("session")!=plcSessionHex()){plcReplyFor(http,409,F("{\"error\":\"Сеанс ПЛК изменился; команда не отправлена\"}"));return;}
            if(!bridgeUnsigned(http.arg("requestId").c_str(),id) || !id || id<=lastCommandId){plcReplyFor(http,409,F("{\"error\":\"Повторный или устаревший номер команды; повтор запрещён\"}"));return;}
            if(parseCommandHex(http.arg("payload"),data,size)){code=plcReadJob.command(data,size,millis(),tcpBridgeBusy());if(code==202)lastCommandId=id;}
        }else if(op=="chunk"){
            uint32_t offset=0,count=0;
            if(bridgeUnsigned(http.arg("offset").c_str(),offset) && bridgeUnsigned(http.arg("count").c_str(),count) && count<=224)code=plcReadJob.chunk(offset,(uint16_t)count,millis(),tcpBridgeBusy());
        }else if(op=="batch"){
            uint8_t channels[16],size=0;if(parseChannelList(http.arg("channels").c_str(),channels,size))code=plcReadJob.batch(channels,size,millis(),tcpBridgeBusy());
        }
        if(code!=202){plcReplyFor(http,code,code==400?F("{\"error\":\"Неверная операция чтения или параметры\"}"):F("{\"error\":\"UART занят или требуется новая проверка ПЛК\"}"));return;}
        plcReplyFor(http,202,String(F("{\"ticket\":"))+String(plcReadJob.ticket)+F("}"));
    });
    http.on("/plc-api/result",HTTP_GET,[&http,viewer]{
        if(!plcAllowedFor(http))return;
        if(viewer && !viewerLease.touch(millis(),tcpBridgeBusy())){plcReplyFor(http,409,F("{\"error\":\"UART занят TCP\"}"));return;}
        uint32_t ticket=0;
        if(!bridgeUnsigned(http.arg("ticket").c_str(),ticket) || !ticket || ticket!=plcReadJob.ticket){plcReplyFor(http,409,F("{\"error\":\"Запрос уже заменён или ESP перезапущена\"}"));return;}
        String json;json.reserve(700);json=F("{\"ticket\":");json+=String(ticket);json+=F(",\"state\":");json+=String((int)plcReadJob.client.state());json+=F(",\"status\":");json+=String(plcReadJob.client.status());
        json+=F(",\"session\":\"");json+=plcSessionHex();json+=F("\",\"payloadHex\":\"");
        if(plcReadJob.client.state()==FLProgReadClient::Done){
            static const char hex[]="0123456789abcdef";const uint8_t *data=plcReadJob.client.result();
            for(uint16_t i=0;i<plcReadJob.client.size();++i){json+=hex[data[i]>>4];json+=hex[data[i]&15];}
        }
        json+=F("\"}");plcReplyFor(http,200,json);
    });
}
static void registerPlcReadHttpRoutes(){
    registerReadRpc(setupServer,setupToken);
    setupServer.on("/plc",HTTP_GET,[]{
        if(!authorizedSettings())return;if(!plcAllowedFor(setupServer))return;
        setupServer.sendHeader("Cache-Control","no-store");setupServer.send_P(200,"text/html; charset=utf-8",FLPROG_READ_PAGE);
    });
}
