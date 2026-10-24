#include <Arduino.h>
#include "flprogStm32OtaFlash.h"
#include <string.h>

namespace
{
constexpr uint32_t kBootStart = 0x08000000UL;
constexpr uint32_t kAppStart = FlprogOtaFlash::app;
constexpr uint32_t kAppEnd = FlprogOtaFlash::stage;
constexpr uint32_t kAppCapacity = kAppEnd - kAppStart;
constexpr uint32_t kStageStart = FlprogOtaFlash::stage;
constexpr uint32_t kStageData = kStageStart + 0x100UL;
constexpr uint32_t kStageEnd = FlprogOtaFlash::end;
constexpr uint8_t kMagic[8] = {'F','L','P','O','T','A','1',0};

struct StageHeader
{
    uint8_t magic[8];
    uint32_t imageSize;
    uint32_t imageCrc32;
    uint32_t reserved;
};

uint32_t crc32(const uint8_t *data, uint32_t length)
{
    uint32_t crc = 0xFFFFFFFFUL;
    for (uint32_t i = 0; i < length; ++i)
    {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit)
        {
            crc = (crc >> 1) ^ ((crc & 1U) ? 0xEDB88320UL : 0U);
        }
    }
    return ~crc;
}

bool readValidHeader(StageHeader &header)
{
    memcpy(&header, reinterpret_cast<const void *>(kStageStart), sizeof(header));
    return memcmp(header.magic, kMagic, sizeof(kMagic)) == 0 &&
           (header.reserved == FLPROG_STM32_OTA_LAYOUT ||
            (FLPROG_STM32_OTA_LAYOUT == 1 && header.reserved == 0xFFFFFFFFUL)) &&
           FlprogOtaFlash::vectorValid(kStageData, header.imageSize) &&
           header.imageSize >= 8 && header.imageSize <= kAppCapacity &&
           kStageData + header.imageSize <= kStageEnd &&
           crc32(reinterpret_cast<const uint8_t *>(kStageData), header.imageSize) == header.imageCrc32;
}

bool eraseApplication()
{
    return FlprogOtaFlash::erase(false);
}

bool programApplication(uint32_t imageSize)
{
    for (uint32_t offset = 0; offset < imageSize; offset += 4)
    {
        uint32_t word = 0xFFFFFFFFUL;
        const uint32_t remaining = imageSize - offset;
        memcpy(&word, reinterpret_cast<const void *>(kStageData + offset), remaining < 4 ? remaining : 4);
        if (!FlprogOtaFlash::programWord(kAppStart + offset, word))
        {
            return false;
        }
    }
    return crc32(reinterpret_cast<const uint8_t *>(kAppStart), imageSize) ==
           crc32(reinterpret_cast<const uint8_t *>(kStageData), imageSize);
}

bool clearStageMarker()
{
    return FlprogOtaFlash::programWord(kStageStart, 0);
}

bool applicationVectorValid()
{
    return FlprogOtaFlash::vectorValid(kAppStart, kAppCapacity);
}

[[noreturn]] void branchToApplication(uint32_t stack, uint32_t reset)
{
    // Do not call the application's Reset_Handler as an ordinary C function.
    // Reset_Handler is an entry point, not a function that can return to this
    // bootloader. Switch to its stack and branch without creating a return
    // frame on the application's initial stack.
    const uint32_t threadMode = 0;
    __asm volatile(
        "msr control, %0\n"
        "isb\n"
        "msr msp, %1\n"
        "dsb\n"
        "isb\n"
        // The application Reset_Handler expects the reset-state PRIMASK=0.
        // Leaving interrupts masked freezes HAL timekeeping and can stall the
        // network stack after a bootloader-to-application handoff.
        "cpsie i\n"
        "bx %2\n"
        :
        : "r"(threadMode), "r"(stack), "r"(reset)
        : "memory");
    __builtin_unreachable();
}

void jumpToApplication()
{
    if (!applicationVectorValid())
    {
        return;
    }

    const uint32_t stack = *reinterpret_cast<const volatile uint32_t *>(kAppStart);
    const uint32_t reset = *reinterpret_cast<const volatile uint32_t *>(kAppStart + 4);
    __disable_irq();
    SysTick->CTRL = 0;
    SysTick->LOAD = 0;
    SysTick->VAL = 0;
    SCB->ICSR = SCB_ICSR_PENDSTCLR_Msk | SCB_ICSR_PENDSVCLR_Msk;
    for (uint32_t bank = 0; bank < 8; ++bank)
    {
        NVIC->ICER[bank] = 0xFFFFFFFFUL;
        NVIC->ICPR[bank] = 0xFFFFFFFFUL;
    }
    HAL_RCC_DeInit();
    HAL_DeInit();
    SCB->VTOR = kAppStart;
    __DSB();
    __ISB();
    branchToApplication(stack, reset);
}

bool installStagedApplication()
{
    StageHeader header = {};
    if (!readValidHeader(header))
    {
        return true;
    }

    if (HAL_FLASH_Unlock() != HAL_OK)
    {
        return false;
    }
    const bool erased = eraseApplication();
    const bool programmed = erased && programApplication(header.imageSize);
    const bool invalidated = programmed && clearStageMarker();
    HAL_FLASH_Lock();

    // On any failure leave the staged marker intact. A reset retries the copy.
    return invalidated;
}
}

void setup()
{
    HAL_Init();
    if (!FlprogOtaFlash::hardwareMatches()) while (true) delay(1000);
    if (!installStagedApplication())
    {
        // A valid staged update exists but could not be installed. Never jump
        // into a partially erased/programmed application; power-cycle retries.
        while (true) delay(1000);
    }
    jumpToApplication();
}

void loop()
{
    // No valid application or a failed install: remain here for SWD recovery.
    delay(1000);
}
