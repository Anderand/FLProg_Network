#pragma once
#include <stdint.h>
struct IPAddress{uint8_t p[4];IPAddress(uint8_t a=0,uint8_t b=0,uint8_t c=0,uint8_t d=0):p{a,b,c,d}{};uint8_t operator[](int i)const{return p[i];}};
