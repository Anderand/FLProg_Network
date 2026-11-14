// Automatic, read-only-by-default project binding. No HTTP/network dependency.
#pragma once
#include "FLProgWebUiBridge.h"
#include "FLProgBridgeResources.h"

namespace flprog_bridge {
class ProjectBinding {
public:
    ProjectBinding(FLProgWebUiModel &model,const FLProgWebUiThemeDescriptor &theme,
                   const char *id,const char *hash,const uint8_t *bytes,uint32_t size,
                   uint32_t plain,const uint8_t *sha):server(identity),model(model),theme(theme),
        id(id),hash(hash),web(model),resources(bytes,size,plain,sha) {
        attached=web.attach(server)&&resources.attach(server);
    }
    // Identity is frozen while enabled. Disable before applying new metadata.
    bool configure(const char *version,const char *controller) {
        if(configured)return true;
        if(!attached || !version || !*version || !controller)return false;
        size_t at=0;identity[0]=0;
        if(!literal(at,"{\"projectId\":") || !quoted(at,id) || !literal(at,",\"model\":") ||
           !quoted(at,*controller?controller:"FLProg controller") ||
           !literal(at,",\"firmware\":") || !quoted(at,version) ||
           !literal(at,",\"webApi\":1,\"webHash\":") || !quoted(at,hash) || !literal(at,"}"))return false;
        const size_t envelope=strlen("{\"protocol\":1,\"services\":[1,4],\"identity\":")+1;
        if(at+envelope>MaxPayload-1){identity[0]=0;return false;}
        configured=FLProgWebUiRuntime::configure(model,theme);return configured;
    }
    void clearIdentity(){configured=false;identity[0]=0;server.resetTransport();}
    // Optional project hooks; no permissive write policy is installed implicitly.
    void setHooks(FLProgWebUiBridge::WritePolicy policy,FLProgWebUiBridge::BeforeRead refresh=nullptr){web.setHooks(policy,refresh);}
    Server server;
private:
    char identity[MaxPayload]{};
    FLProgWebUiModel &model;const FLProgWebUiThemeDescriptor &theme;
    const char *id,*hash;FLProgWebUiBridge web;FLProgBridgeResources resources;
    bool attached=false,configured=false;
    bool literal(size_t &at,const char *text){
        size_t n=strlen(text);if(at+n>=sizeof(identity))return false;
        memcpy(identity+at,text,n);at+=n;identity[at]=0;return true;
    }
    bool quoted(size_t &at,const char *text){
        if(!text || !literal(at,"\""))return false;
        for(const uint8_t *p=(const uint8_t*)text;*p;++p){
            char one[2]={(char)*p,0};
            if(*p=='"'||*p=='\\'){if(!literal(at,"\\")||!literal(at,one))return false;}
            else if(*p<32){const char hex[]="0123456789abcdef";char escape[7]={'\\','u','0','0',hex[*p>>4],hex[*p&15],0};if(!literal(at,escape))return false;}
            else if(!literal(at,one))return false;
        }
        return literal(at,"\"");
    }
};
}
