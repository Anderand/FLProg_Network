#pragma once
#include "BridgeProjectPage.h"
static BridgeWebServer projectServer(8081);
static String viewerToken;
static bool projectServerStarted=false;
static void beginProjectServer(){
    char value[17];snprintf(value,sizeof(value),"%08lx%08lx",(unsigned long)esp_random(),(unsigned long)esp_random());viewerToken=value;
    const char* headers[]={"Cookie"};projectServer.collectHeaders(headers,1);
    registerReadRpc(projectServer,viewerToken,true);
    projectServer.on("/",HTTP_GET,[]{
        if(!plcAllowedFor(projectServer))return;
        projectServer.sendHeader("Cache-Control","no-store");projectServer.send_P(200,"text/html; charset=utf-8",FLPROG_PROJECT_PAGE);
    });
    projectServerStarted=projectServer.begin();
}
static void pollProjectServer(){if(!projectServerStarted && bridgeNetworkReady())beginProjectServer();if(projectServerStarted)projectServer.handleClient();}
