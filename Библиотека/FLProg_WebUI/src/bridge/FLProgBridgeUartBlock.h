// UART lifecycle for FLProg Basic/Professional blocks. No network dependency.
#pragma once
#include "FLProgBridgeProtocol.h"

namespace flprog_bridge {
// Backend supplies check/begin/end/available/read/room/write; never flush or wait.
template<class Backend> class UartBlock {
public:
    enum Error { None=0, InvalidUart=1, InvalidBaud=2, InvalidBudget=3, StartFailed=4, UartOccupied=5, ChangeWhileEnabled=6 };
    explicit UartBlock(Backend &backend):io(backend) {}
    void pool(Server &server,bool enable,long uart,long baud,long budget,uint32_t now) {
        if(!enable) {
            if(active){server.resetTransport();io.end(number);active=false;}
            error=None;return;
        }
        if(active && (uart!=number || baud!=speed)) {
            // Do not silently redirect traffic or steal another UART.
            error=ChangeWhileEnabled;return;
        }
        if(budget<1 || budget>128){error=InvalidBudget;return;}
        if(!active) {
            if(uart<0 || uart>255 || !io.valid((uint8_t)uart)){error=InvalidUart;return;}
            if(baud<1200 || baud>1000000){error=InvalidBaud;return;}
            if(io.occupied((uint8_t)uart)){error=UartOccupied;return;}
            number=(uint8_t)uart;speed=baud;
            if(!io.begin(number,(uint32_t)speed)){io.end(number);error=StartFailed;return;}
            server.resetTransport();active=true;
        }
        error=None;
        Port port{io,number,rx,tx};server.pool(port,now,(uint8_t)budget);
    }
    bool ready()const{return active && error==None;}
    bool connected(const Server &server,uint32_t now)const{return ready()&&server.sessionAlive(now);}
    uint8_t fault()const{return error;}
    uint32_t received()const{return rx;}
    uint32_t sent()const{return tx;}
private:
    Backend &io;bool active=false;uint8_t number=0,error=None;long speed=0;
    uint32_t rx=0,tx=0;
    struct Port {
        Backend &io;uint8_t number;uint32_t &rx,&tx;
        int available(){return io.available(number);}
        int read(){if(io.available(number)<=0)return -1;int v=io.read(number);if(v>=0)++rx;return v;}
        int availableForWrite(){return io.room(number);}
        size_t write(const uint8_t *p,size_t n){
            size_t at=0;while(at<n && io.room(number)>0){if(!io.write(number,p[at]))break;++at;++tx;}return at;
        }
    };
};
}
