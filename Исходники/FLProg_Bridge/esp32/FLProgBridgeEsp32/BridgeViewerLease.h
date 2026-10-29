#pragma once
#include <stdint.h>
class FLProgViewerLease {
    uint32_t last_=0;bool held_=false;
public:
    bool active(uint32_t now){if(held_ && (uint32_t)(now-last_)>=5000)held_=false;return held_;}
    bool touch(uint32_t now,bool tcpBusy){if(tcpBusy)return false;held_=true;last_=now;return true;}
    void clear(){held_=false;}
};
