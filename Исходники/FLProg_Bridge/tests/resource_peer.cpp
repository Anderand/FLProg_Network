// Native peer: real bounded protocol and Flash-resource adapter, no hardware.
#include <iostream>
#include <deque>
#include <vector>
#include <cassert>
#include "FLProgBridgeResources.h"
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
struct Port {
    std::deque<uint8_t> input;std::vector<uint8_t> output;size_t reads=0,writes=0;
    int available(){return (int)input.size();}
    int read(){if(input.empty())return -1;int v=input.front();input.pop_front();reads++;return v;}
    int availableForWrite(){return 7;}
    size_t write(const uint8_t *p,size_t n){assert(n<=7);writes+=n;output.insert(output.end(),p,p+n);return n;}
};
int main(){
#ifdef _WIN32
    _setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);
#endif
    uint8_t data[512],sha[32]={0};for(unsigned i=0;i<512;i++)data[i]=(uint8_t)i;
    flprog_bridge::Server server("{\"projectId\":\"resources-test\"}");
    FLProgBridgeResources resources(data,512,1024,sha);bool attached=resources.attach(server);assert(attached);if(!attached)return 2;
    Port port;
    for(int c;(c=std::cin.get())!=EOF;){
        port.input.push_back((uint8_t)c);
        for(int j=0;j<50;j++){
            size_t rx=port.reads,tx=port.writes;server.pool(port,100,8);
            assert(port.reads-rx<=8 && port.writes-tx<=8);
        }
        for(auto v:port.output)std::cout.put((char)v);port.output.clear();std::cout.flush();
    }
}
