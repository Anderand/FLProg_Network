// Two bounded queues, one client, no replay and no waiting for output room.
#pragma once
#include <stdint.h>
#include <stddef.h>
class FLProgBoundedRelay {
public:
    static const size_t Capacity=64,Budget=64;
    template<class Net,class Uart> void poll(Net &net,Uart &uart){
        move(net,uart,toUart,uartAt,uartSize);
        move(uart,net,toNet,netAt,netSize);
    }
    void reset(){uartAt=uartSize=netAt=netSize=0;}
private:
    uint8_t toUart[Capacity]{},toNet[Capacity]{};
    size_t uartAt=0,uartSize=0,netAt=0,netSize=0;
    template<class In,class Out> static void move(In &in,Out &out,uint8_t *buf,size_t &at,size_t &size){
        if(at==size){at=size=0;int n=in.available();if(n>0){size_t count=(size_t)n;if(count>Budget)count=Budget;size=in.read(buf,count);if(size>count)size=count;}}
        if(at<size){int room=out.room();if(room<=0)return;size_t n=size-at;if(n>Budget)n=Budget;if(n>(size_t)room)n=(size_t)room;size_t sent=out.write(buf+at,n);if(sent>n)sent=n;at+=sent;}
    }
};
