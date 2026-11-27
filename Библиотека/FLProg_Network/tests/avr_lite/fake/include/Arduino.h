#pragma once
#include <stdint.h>
#include <stddef.h>
extern uint32_t fakeNow;
inline uint32_t millis() { return fakeNow; }
inline uint32_t micros() { return fakeNow * 1000UL + 17UL; }
#ifndef NUM_DIGITAL_PINS
#define NUM_DIGITAL_PINS 20
#endif
class IPAddress {
public:
  IPAddress() : b{0,0,0,0} {}
  IPAddress(uint8_t a,uint8_t c,uint8_t d,uint8_t e) : b{a,c,d,e} {}
  explicit IPAddress(uint32_t v) : b{(uint8_t)(v>>24),(uint8_t)(v>>16),(uint8_t)(v>>8),(uint8_t)v} {}
  uint8_t &operator[](int i) { return b[i]; }
  uint8_t operator[](int i) const { return b[i]; }
private: uint8_t b[4];
};
