#include <deque>
#include <vector>
#include <cassert>
#include <cstdio>
#include "BoundedRelay.h"
struct End {
    std::deque<uint8_t> in;std::vector<uint8_t> out;int capacity=64,shortWrite=64;size_t reads=0,writes=0;
    int available(){return in.size();}
    size_t read(uint8_t *p,size_t n){size_t i=0;while(i<n&&!in.empty()){p[i++]=in.front();in.pop_front();}reads+=i;return i;}
    int room(){return capacity;}
    size_t write(const uint8_t *p,size_t n){if(n>(size_t)shortWrite)n=shortWrite;out.insert(out.end(),p,p+n);writes+=n;return n;}
};
int main(){
    End net,uart;FLProgBoundedRelay relay;
    for(int i=0;i<1000;i++){net.in.push_back(i%256);uart.in.push_back(255-i%256);}
    uart.capacity=0;relay.poll(net,uart);assert(uart.out.empty() && net.reads==64);
    for(int i=0;i<20;i++)relay.poll(net,uart);assert(net.reads==64);
    uart.capacity=64;uart.shortWrite=3;net.shortWrite=5;
    for(int i=0;i<500;i++){auto nr=net.reads,ur=uart.reads,nw=net.writes,uw=uart.writes;relay.poll(net,uart);assert(net.reads-nr<=64&&uart.reads-ur<=64&&net.writes-nw<=64&&uart.writes-uw<=64);}
    assert(uart.out.size()==1000&&net.out.size()==1000);
    for(int i=0;i<1000;i++){assert(uart.out[i]==i%256);assert(net.out[i]==255-i%256);}
    net.in.push_back(42);uart.capacity=0;relay.poll(net,uart);relay.reset();uart.capacity=64;relay.poll(net,uart);assert(uart.out.size()==1000);
    printf("PASS: duplex, bounded work, no overflow, zero/short writes, order, disconnect reset; relay size=%zu bytes\n",sizeof(relay));
}
