// Host-only real C++ protocol + actual WebUI model. No hardware pins.
#include <iostream>
#include <deque>
#include <cassert>
#include <vector>
#include "FLProgWebUiBridge.h"
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
struct Port {
    std::deque<uint8_t> input; std::vector<uint8_t> output;
    size_t reads=0,writes=0; int capacity=7;
    int available(){return (int)input.size();}
    int read(){if(input.empty())return -1;int x=input.front();input.pop_front();reads++;return x;}
    int availableForWrite(){return capacity;}
    size_t write(const uint8_t *p,size_t n){assert(n<=(size_t)capacity);output.insert(output.end(),p,p+n);writes+=n;return n;}
};
static bool permit(uint8_t ch,const uint8_t *p,uint16_t n) {
    if(ch==101 && n==5 && p[0]==FLPROG_WEBUI_INT32) {int32_t v=(int32_t)flprog_bridge::getLE(p+1,4);return v>=0&&v<=100;}
    return ch==102 || ch==103;
}
static FLProgWebUiModel *refreshModel=nullptr;
static void refresh(uint8_t channel) {
    if(channel==10 && refreshModel)refreshModel->publishInt(0,456);
}
int main() {
#ifdef _WIN32
    _setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);
#endif
    FLProgWebUiChannelDescriptor desc[]={
        {"uptime",FLPROG_WEBUI_INT32,FLPROG_WEBUI_PUBLISH,10},
        {"setpoint",FLPROG_WEBUI_INT32,FLPROG_WEBUI_DUPLEX,101},
        {"output",FLPROG_WEBUI_BOOL,FLPROG_WEBUI_DUPLEX,102},
        {"text",FLPROG_WEBUI_TEXT,FLPROG_WEBUI_DUPLEX,103},
        {"secret",FLPROG_WEBUI_TEXT,FLPROG_WEBUI_COMMAND,104}};
    FLProgWebUiChannelSlot slots[5]; FLProgWebUiModel model(desc,slots,5);
    refreshModel=&model;
    model.publishInt(0,123);model.publishInt(1,25);model.publishText(4,"must-not-be-read");
    flprog_bridge::Server server("{\"projectId\":\"host-test\",\"model\":\"C++ HOST\",\"firmware\":\"0.1\"}");
    FLProgWebUiBridge web(model,permit,refresh);bool attached=web.attach(server);assert(attached);assert(!web.attach(server));
    Port port; uint32_t clock=0xfffffff0;
    for(int c;(c=std::cin.get())!=EOF;) {
        port.input.push_back((uint8_t)c);
        for(int i=0;i<45;i++) {
            size_t rx=port.reads,tx=port.writes;server.pool(port,clock,8);
            assert(port.reads-rx<=8);assert(port.writes-tx<=8);
        }
        // Use one timestamp per input byte to cross millis rollover naturally.
        clock++;
        for(uint8_t b:port.output)std::cout.put((char)b);
        port.output.clear();std::cout.flush();
    }
    return 0;
}
