#pragma once
#include <string>
#include <algorithm>
#include <cstdint>
#define FLPROG_WEB_SERVER_HEAD 2
class String {
 std::string s;
public:
 String(const char *v=""):s(v){} String(std::string v):s(v){}
 unsigned length()const{return s.size();}
 void toLowerCase(){std::transform(s.begin(),s.end(),s.begin(),[](unsigned char c){return std::tolower(c);});}
 int indexOf(char c,unsigned from=0)const{auto p=s.find(c,from);return p==s.npos?-1:p;}
 String substring(unsigned a,unsigned b=~0U)const{return s.substr(a,b==~0U?b:b-a);}
 void trim(){auto a=s.find_first_not_of(" \t");if(a==s.npos){s.clear();return;}s=s.substr(a,s.find_last_not_of(" \t")-a+1);}
 bool startsWith(const char *v)const{return s.rfind(v,0)==0;}
 const char *c_str()const{return s.c_str();}
 bool operator==(const char *v)const{return s==v;}
};
class FLProgNetworkHttpServer {
public:
 std::string bytes;String accept;int verb=0;
 String headerValueAtKey(const char*){return accept;}
 int method(){return verb;}
 void print(const char *v){bytes+=v;}
 void print(unsigned long v){bytes+=std::to_string(v);}
 void write(uint8_t v){bytes.push_back((char)v);}
};
