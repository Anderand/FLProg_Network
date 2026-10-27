// Test-only: executes the production decoder on the target MCU.
#pragma once
#include <FLProgWebUiPlatformDiagnostics.h>
inline int32_t platformDiagnosticsSelfTest()
{
    using namespace FLProgWebUiPlatformDiagnostics;
    struct Vector { uint32_t flags; const char *expected; };
    const Vector vectors[] = {
        {0,"Флаги не сохранены"},{1,"Флаги не сохранены"},
        {0x02000000UL,"Просадка питания (BOR)"},
        {0x04000000UL,"Сброс через NRST"},
        {0x08000000UL,"Включение питания (POR)"},
        {0x10000000UL,"Программный сброс"},
        {0x20000000UL,"Watchdog IWDG"},{0x40000000UL,"Watchdog WWDG"},
        {0x80000000UL,"Сброс энергосбережения"},
        {0x1C000000UL,"Несколько флагов сброса"},
        {0x10000001UL,"Программный сброс"}
    };
    int32_t count=0;
    for(const auto &v:vectors) {
        const char *actual=resetDescription(v.flags);
        if(strcmp(actual,v.expected)||strlen(actual)>63) return -1;
        ++count;
    }
    const char *ids[]={"reset_flags","reset_cause","heap_used","heap_arena_free"};
    for(const char *id:ids) { if(!readonlyChannel(id))return -2; ++count; }
    if(readonlyChannel(nullptr)||readonlyChannel("my_heap_used"))return -3;
    count+=2;
    int32_t used,free; if(!readHeap(used,free)||used<0||free<0)return -4; ++count;
    uint32_t flags; if(!readResetFlags(flags)||(flags&0x01FFFFFFUL))return -5; ++count;
    return count; // 19 on STM32F1/F4 with enabled diagnostics.
}
