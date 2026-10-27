#pragma once
#include <stdint.h>
#include <string.h>
// Bounded ASCII whole-value matcher. No heap, recursion or backtracking.
namespace flprog_webui_pattern {
struct Token { uint64_t low, high; uint8_t min, max; };
inline void add(Token &t, unsigned c) { if(c<64)t.low|=1ULL<<c;else if(c<128)t.high|=1ULL<<(c-64); }
inline bool has(const Token &t,unsigned c){return c<64?(t.low&(1ULL<<c))!=0:c<128&&(t.high&(1ULL<<(c-64)))!=0;}
inline bool atom(const char *&p,Token &t,int &single,bool inclass=false){
 unsigned c=(unsigned char)*p++;single=-1;if(!c)return false;
 if(c=='\\'){
  c=(unsigned char)*p++;if(!c)return false;
  if(c=='d'||c=='w'||c=='s'){
   for(unsigned i=0;i<128;i++)if((c=='d'&&i>='0'&&i<='9')||(c=='w'&&((i>='0'&&i<='9')||(i>='A'&&i<='Z')||(i>='a'&&i<='z')||i=='_'))||(c=='s'&&(i==32||(i>=9&&i<=13))))add(t,i);
   return true;
  }
  if(!strchr("\\.^$[]{}()*+?|-/",c))return false;
 }else if((!inclass&&strchr("\\.^$[]{}()*+?|",c))||(inclass&&c=='['))return false;
 if(c<32||c>126)return false;add(t,c);single=(int)c;return true;
}
inline bool number(const char *&p,unsigned &n){n=0;unsigned count=0;while(*p>='0'&&*p<='9'){n=n*10+(*p++-'0');if(++count>2)return false;}return count&&n<=63;}
inline bool token(const char *&p,Token &t){
 t={0,0,1,1};
 if(*p=='['){
  ++p;bool neg=*p=='^';if(neg)++p;bool any=false;
  while(*p&&*p!=']'){
   Token a={0,0,0,0};int first;if(!atom(p,a,first,true))return false;
   if(*p=='-'&&p[1]&&p[1]!=']'){
    ++p;Token b={0,0,0,0};int last;if(!atom(p,b,last,true)||first<0||last<first)return false;
    for(int c=first;c<=last;c++)add(t,(unsigned)c);
   }else{t.low|=a.low;t.high|=a.high;}
   any=true;
  }
  if(!any||*p!=']')return false;++p;if(neg){t.low=~t.low;t.high=~t.high;}
 }else if(*p=='.'){++p;t.low=~0ULL;t.high=~0ULL;t.low&=~((1ULL<<10)|(1ULL<<13));}
 else{int single;if(!atom(p,t,single))return false;}
 if(*p=='?'||*p=='*'||*p=='+'){char q=*p++;t.min=q=='+'?1:0;t.max=q=='?'?1:63;}
 else if(*p=='{'){
  ++p;unsigned lo,hi;if(!number(p,lo))return false;hi=lo;
  if(*p==','){++p;if(!number(p,hi))return false;}
  if(*p!='}'||lo>hi)return false;++p;t.min=(uint8_t)lo;t.max=(uint8_t)hi;
 }
 return true;
}
inline bool matches(const char *pattern,const char *text){
 if(!text)return false;if(!pattern||!*pattern)return true;
 const size_t n=strlen(text),length=strlen(pattern);if(n>63||length>63)return false;
 for(size_t i=0;i<length;i++)if((unsigned char)pattern[i]<32||(unsigned char)pattern[i]>126)return false;
 for(size_t i=0;i<n;i++)if((unsigned char)text[i]>127)return false;
 const char *p=pattern;if(*p=='^')++p;uint64_t positions=1;
 while(*p){
  if(*p=='$'&&!p[1]){++p;break;}
  Token t;if(!token(p,t))return false;uint64_t out=0;
  for(size_t start=0;start<=n;start++)if(positions&(1ULL<<start)){
   if(!t.min)out|=1ULL<<start;size_t end=start;
   for(unsigned count=1;count<=t.max&&end<n;count++){
    if(!has(t,(unsigned char)text[end]))break;++end;if(count>=t.min)out|=1ULL<<end;
   }
  }
  positions=out;
 }
 return (positions&(1ULL<<n))!=0;
}
}
