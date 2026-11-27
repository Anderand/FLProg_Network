/*
 * FLProg_Network — flprogNetworkProfile.h
 *
 * RC6-A dev.16-fix6-profiles
 *
 * One code base, three compile-time profiles:
 *   UNIVERSAL  = built-in Wi-Fi + wired backends
 *   WIFI_ONLY  = built-in Wi-Fi, wired backends excluded
 *   WIRED_ONLY = wired backends, built-in Wi-Fi excluded
 *
 * IMPORTANT:
 * The profile is compile-time and therefore applies to every translation
 * unit of the library. Runtime clientOff()/wiznetMode() alone cannot remove
 * code/data from the firmware.
 * Расширенный контракт сопровождения:
 * - Это публичная или межмодульная декларация: комментарии описывают владельца состояния и допустимый порядок вызовов.
 * - Конфигурация применяется до начала работы; runtime-методы обслуживаются из общего network.pool().
 * - При изменении API учитывать legacy generated-код и frozen API level 10006.
 * Extended maintenance contract:
 * - This declaration defines a public or cross-module boundary; document state ownership and call order here.
 * - Apply configuration before start; service runtime through the shared network.pool() lifecycle.
 * - Any API change must account for legacy generated code and frozen API level 10006.
 */
#pragma once

// Compact Arduino Ethernet backend for the memory-constrained Uno/Nano class.
// Select globally from the compiler's MCU target, so Arduino's generated
// prototype translation unit and every library translation unit agree.
// Set FLPROG_NETWORK_AVR_LITE=0 in the build flags to retain the full API.
#ifndef FLPROG_NETWORK_AVR_LITE
  #if defined(ARDUINO_ARCH_AVR) && defined(__AVR_ATmega328P__) && \
      (defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_NANO))
    #define FLPROG_NETWORK_AVR_LITE 1
  #else
    #define FLPROG_NETWORK_AVR_LITE 0
  #endif
#endif

#define FLPROG_NETWORK_BUILD_UNIVERSAL  0
#define FLPROG_NETWORK_BUILD_WIFI_ONLY  1
#define FLPROG_NETWORK_BUILD_WIRED_ONLY 2

#ifndef FLPROG_NETWORK_BUILD_PROFILE
#define FLPROG_NETWORK_BUILD_PROFILE 0
#endif

#if (FLPROG_NETWORK_BUILD_PROFILE < FLPROG_NETWORK_BUILD_UNIVERSAL) || \
    (FLPROG_NETWORK_BUILD_PROFILE > FLPROG_NETWORK_BUILD_WIRED_ONLY)
#error "FLProg_Network: invalid FLPROG_NETWORK_BUILD_PROFILE"
#endif

#define FLPROG_NETWORK_PROFILE_WIFI_ONLY \
    (FLPROG_NETWORK_BUILD_PROFILE == FLPROG_NETWORK_BUILD_WIFI_ONLY)

#define FLPROG_NETWORK_PROFILE_WIRED_ONLY \
    (FLPROG_NETWORK_BUILD_PROFILE == FLPROG_NETWORK_BUILD_WIRED_ONLY)

#define FLPROG_NETWORK_PROFILE_UNIVERSAL \
    (FLPROG_NETWORK_BUILD_PROFILE == FLPROG_NETWORK_BUILD_UNIVERSAL)

#ifndef FLPROG_NETWORK_COMPILE_WIFI
  #if FLPROG_NETWORK_PROFILE_WIRED_ONLY
    #define FLPROG_NETWORK_COMPILE_WIFI 0
  #else
    #define FLPROG_NETWORK_COMPILE_WIFI 1
  #endif
#endif

#ifndef FLPROG_NETWORK_COMPILE_WIRED
  #if FLPROG_NETWORK_PROFILE_WIFI_ONLY
    #define FLPROG_NETWORK_COMPILE_WIRED 0
  #else
    #define FLPROG_NETWORK_COMPILE_WIRED 1
  #endif
#endif

// Optional ESP32 internal-MAC/RMII backend gate. Keep the historical default;
// external SPI Ethernet and the Arduino-Pico Wi-Fi backends are independent.
#ifndef FLPROG_NETWORK_COMPILE_RMII
  #define FLPROG_NETWORK_COMPILE_RMII 1
#endif

// Optional compile-time exclusion for the full Wiznet/W5500 DHCP client.
// Keep the default for source and behavior compatibility; static-IP builds
// may set this to 0. Built-in Wi-Fi and RMII DHCP are independent.
#ifndef FLPROG_NETWORK_COMPILE_WIZNET_DHCP
  #define FLPROG_NETWORK_COMPILE_WIZNET_DHCP 1
#endif

// This switch gates ESP-family OTA (ArduinoOTA and ESP32 Update backends).
// ArduinoOTA is Wi-Fi-specific on ESP8266; ESP32 core 3.x uses the unified
// NetworkUDP/NetworkClient stack and can also serve native RMII. External SPI
// Ethernet (for example W5500) is not covered. STM32 staged OTA has its own
// board/layout switch and is intentionally independent of this option.
#ifndef FLPROG_NETWORK_COMPILE_OTA
  #if defined(ESP8266)
    #define FLPROG_NETWORK_COMPILE_OTA FLPROG_NETWORK_COMPILE_WIFI
  #elif defined(ESP32)
    #define FLPROG_NETWORK_COMPILE_OTA (FLPROG_NETWORK_COMPILE_WIFI || FLPROG_NETWORK_COMPILE_WIRED)
  #else
    #define FLPROG_NETWORK_COMPILE_OTA 0
  #endif
#endif

#if !FLPROG_NETWORK_COMPILE_WIFI && !FLPROG_NETWORK_COMPILE_WIRED
#error "FLProg_Network: at least one backend family must be compiled"
#endif
