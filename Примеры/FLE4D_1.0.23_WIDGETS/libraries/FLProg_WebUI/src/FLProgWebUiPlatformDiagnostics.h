// Optional, read-only platform measurements. No heap allocation or reset-flag clearing.
#pragma once
#include <stdint.h>
#include <string.h>
#if defined(ARDUINO_ARCH_STM32) && !defined(FLPROG_WEBUI_DISABLE_PLATFORM_DIAGNOSTICS)
#include <malloc.h>
extern "C" {
extern char LD_MAX_SIZE __attribute__((weak)), LD_MAX_DATA_SIZE __attribute__((weak)), LD_FLASH_OFFSET __attribute__((weak));
extern char _sdata __attribute__((weak)), _edata __attribute__((weak)), _sbss __attribute__((weak)), _ebss __attribute__((weak));
extern char _sidata __attribute__((weak)), _estack __attribute__((weak)), _Min_Stack_Size __attribute__((weak));
extern void *_sbrk(int);
}
#endif

namespace FLProgWebUiPlatformDiagnostics {
struct Memory {
    uint32_t flashTotal, flashCapacity, flashUsed, ramTotal, ramCapacity, ramStatic, ramAvailable, ccmTotal;
    bool physicalFlash, flashLayout, physicalRam, ramLayout, availableEstimate, ccm;
};
inline Memory readMemory()
{
    Memory m={};
#if defined(ARDUINO_ARCH_STM32) && !defined(FLPROG_WEBUI_DISABLE_PLATFORM_DIAGNOSTICS)
    const uintptr_t ram=(uintptr_t)&LD_MAX_DATA_SIZE, stack=(uintptr_t)&_estack;
    const uintptr_t ds=(uintptr_t)&_sdata, de=(uintptr_t)&_edata, bs=(uintptr_t)&_sbss, be=(uintptr_t)&_ebss;
    if(ram>0 && ram<=0x1000000UL && ds && de>=ds && bs>=de && be>=bs && stack>=be && be-ds<=ram) {
        m.ramCapacity=ram; m.ramStatic=(de-ds)+(be-bs); m.ramLayout=true;
        // Conservative malloc headroom: preserve the linker stack reserve and
        // also respect the current main stack. No RTOS/process-stack estimate.
        if(!(__get_CONTROL() & 2U)) {
            const void *heapEnd=_sbrk(0);
            const uintptr_t top=heapEnd==(void*)-1?0:(uintptr_t)heapEnd;
            const uintptr_t reserve=(uintptr_t)&_Min_Stack_Size, sp=__get_MSP();
            const uintptr_t limit=reserve<ram && stack>reserve ? stack-reserve : 0;
            const uintptr_t ceiling=sp<limit?sp:limit;
            const struct mallinfo info=mallinfo();
            if(top>=be && ceiling>=top && (uint64_t)info.fordblks<=INT32_MAX && ceiling-top+(uint32_t)info.fordblks<=ram) {
                m.ramAvailable=ceiling-top+(uint32_t)info.fordblks; m.availableEstimate=true;
            }
        }
    }
#if defined(FLASHSIZE_BASE) && defined(FLASH_BASE)
    m.flashTotal=(uint32_t)(*reinterpret_cast<volatile const uint16_t*>(FLASHSIZE_BASE))*1024UL;
    m.physicalFlash=m.flashTotal>=16384 && m.flashTotal<=0x1000000UL;
    const uintptr_t capacity=(uintptr_t)&LD_MAX_SIZE, offset=(uintptr_t)&LD_FLASH_OFFSET;
    const uintptr_t imageStart=FLASH_BASE+offset, imageData=(uintptr_t)&_sidata;
    if(m.physicalFlash && capacity && capacity<=m.flashTotal && offset+capacity<=m.flashTotal &&
       de>=ds && imageData>=imageStart && imageData-imageStart+(de-ds)<=capacity) {
        m.flashCapacity=capacity; m.flashUsed=imageData-imageStart+(de-ds); m.flashLayout=true;
    }
#endif
#if defined(STM32F407xx)
    // STM32F407 CMSIS map: SRAM1 112 KiB + SRAM2 16 KiB + CCM 64 KiB.
    m.ramTotal=192UL*1024; m.physicalRam=true;
#endif
#if defined(CCMDATARAM_BASE) && defined(CCMDATARAM_END)
    m.ccmTotal=CCMDATARAM_END-CCMDATARAM_BASE+1; m.ccm=true;
#endif
#endif
    return m;
}
// STM32F1/F4 CSR reset bits. Multiple flags can accumulate until RMVF is set.
inline const char *resetDescription(uint32_t flags)
{
    flags &= 0xFE000000UL;
    if (!flags) return "Флаги не сохранены";
    if (flags & (flags - 1)) return "Несколько флагов сброса";
    switch (flags) {
    case 0x02000000UL: return "Просадка питания (BOR)";
    case 0x04000000UL: return "Сброс через NRST";
    case 0x08000000UL: return "Включение питания (POR)";
    case 0x10000000UL: return "Программный сброс";
    case 0x20000000UL: return "Watchdog IWDG";
    case 0x40000000UL: return "Watchdog WWDG";
    case 0x80000000UL: return "Сброс энергосбережения";
    default: return "Флаги не сохранены";
    }
}

inline bool readResetFlags(uint32_t &flags)
{
    flags = 0;
#if defined(ARDUINO_ARCH_STM32) && (defined(STM32F1xx) || defined(STM32F4xx)) && defined(RCC_CSR_SFTRSTF) && !defined(FLPROG_WEBUI_DISABLE_PLATFORM_DIAGNOSTICS)
    uint32_t mask = RCC_CSR_PINRSTF | RCC_CSR_PORRSTF | RCC_CSR_SFTRSTF |
                    RCC_CSR_IWDGRSTF | RCC_CSR_WWDGRSTF | RCC_CSR_LPWRRSTF;
#ifdef RCC_CSR_BORRSTF
    mask |= RCC_CSR_BORRSTF;
#endif
    flags = RCC->CSR & mask; // Never write CSR or clear flags owned by the application.
    return true;
#else
    return false;
#endif
}

inline bool readHeap(int32_t &used, int32_t &arenaFree)
{
    used = arenaFree = 0;
#if defined(ARDUINO_ARCH_STM32) && !defined(FLPROG_WEBUI_DISABLE_PLATFORM_DIAGNOSTICS)
    const struct mallinfo info = mallinfo();
    if ((uint64_t)info.uordblks > INT32_MAX || (uint64_t)info.fordblks > INT32_MAX) return false;
    used = info.uordblks;
    arenaFree = info.fordblks; // Free blocks in the malloc arena, NOT total free SRAM.
    return true;
#else
    return false;
#endif
}

inline bool readonlyChannel(const char *id)
{
    return id && (!strcmp(id,"reset_flags") || !strcmp(id,"reset_cause") ||
                  !strcmp(id,"heap_used") || !strcmp(id,"heap_arena_free") ||
                  !strcmp(id,"system_uptime") || !strcmp(id,"flash_total") ||
                  !strcmp(id,"flash_app_capacity") || !strcmp(id,"flash_app_used") || !strcmp(id,"flash_app_free") ||
                  !strcmp(id,"ram_total") || !strcmp(id,"ram_app_capacity") || !strcmp(id,"ram_static_used") ||
                  !strcmp(id,"ram_available_estimate") || !strcmp(id,"ram_used_estimate") ||
                  !strcmp(id,"ccm_total") || !strcmp(id,"ccm_used"));
}
}
