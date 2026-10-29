#pragma once
// Small form decoder for bridge-owned text/plain POST bodies (max1024 bytes).
inline int bridgeHexDigit(char c){return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:-1;}
inline String bridgeFormDecode(const char*p,size_t n){String out;for(size_t i=0;i<n;++i){char c=p[i];if(c=='+')c=' ';else if(c=='%'){if(i+2>=n)return String();int a=bridgeHexDigit(p[++i]),b=bridgeHexDigit(p[++i]);if(a<0||b<0||(a==0&&b==0))return String();c=(char)(a*16+b);}if(c==0)return String();out+=c;}return out;}
inline bool bridgeFormFind(const char*body,const char*key,String&value){
 if(!body||strlen(body)>1024)return false;const char*at=body;
 while(*at){const char*end=strchr(at,'&');if(!end)end=at+strlen(at);const char*eq=(const char*)memchr(at,'=',end-at);const char*kend=eq?eq:end;
  if(bridgeFormDecode(at,kend-at)==key){value=eq?bridgeFormDecode(eq+1,end-eq-1):String();return true;}at=*end?end+1:end;
 }return false;
}
