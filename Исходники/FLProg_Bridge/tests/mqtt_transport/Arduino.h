#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string>
#include <cstring>
#include <cstdio>
class String:public std::string{public:using std::string::string;String():std::string(){};void concat(const char*p,unsigned n){append(p,n);}};
uint32_t millis();
