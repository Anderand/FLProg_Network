// Optional RT_HW adapter. Pins stay in the FLProg project; this file never sets them.
#pragma once
#include <flprogUtilites.h>
#include "FLProgBridgeUartBlock.h"
struct FLProgBridgeRtUart {
    bool valid(uint8_t n){return RT_HW_Base.uartCheckNum(n);}
    bool occupied(uint8_t n){return RT_HW_Base.uartGetStatus(n)!=0;}
    bool begin(uint8_t n,uint32_t speed){RT_HW_Base.uartSetSpeed(speed,n);RT_HW_Base.uartBegin(n);return RT_HW_Base.uartGetCodeErr(n)==0 && RT_HW_Base.uartGetStatus(n)==1;}
    void end(uint8_t n){RT_HW_Base.uartEnd(n);}
    int available(uint8_t n){return RT_HW_Base.uartAvailable(n);}
    int read(uint8_t n){return RT_HW_Base.uartRead(n);}
    int room(uint8_t n){return RT_HW_Base.uartAvailableForWrite(n);}
    bool write(uint8_t n,uint8_t b){return RT_HW_Base.uartWrite(b,n)!=0;}
};
inline flprog_bridge::UartBlock<FLProgBridgeRtUart>& flpBridgeUartBlocks(){
    static FLProgBridgeRtUart port;static flprog_bridge::UartBlock<FLProgBridgeRtUart> block(port);return block;
}
