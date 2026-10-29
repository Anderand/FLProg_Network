#include "BridgeReadClient.h"
#include <cassert>
#include <cstdio>
struct Port{int available(){return 0;}int read(){return -1;}int availableForWrite(){return 64;}size_t write(const uint8_t*,size_t n){return n;}};
int main(){FLProgBridgeSharedSession s;FLProgReadClient a,b;a.bindSession(s);b.bindSession(s);s.hello=true;s.session=7;uint32_t now=0xfffffff0u;
 assert(a.read(101,now));assert(!b.read(101,now));assert(s.owner&&s.waiter);a.cancelLocal();assert(a.hasSession()&&b.hasSession());
 // Abandoned caller reservation expires across millis wrap; no queued request exists.
 assert(!a.read(101,now+19));assert(a.read(101,now+21));assert(s.sequence==2);assert(!b.read(101,now+22));
 Port p;a.pool(p,now+1522);assert(a.state()==FLProgReadClient::Timeout&&!a.hasSession()&&!b.hasSession()&&!s.owner);assert(!b.command((const uint8_t*)"x",1,now+1523));
 assert(b.hello(99,now+1523));assert(s.sequence==1&&s.epoch==1&&s.session==99);b.cancel();assert(!s.owner&&!s.waiter&&!s.hello);
 s.hello=true;s.sequence=0xffffffffu;assert(!a.read(101,now+1545));a.invalidateSession();assert(a.hello(100,now+1545));assert(s.sequence==1&&s.epoch==2);
 printf("PASS shared context: owner exclusion, abandoned reservation/wrap, timeout invalidates both, cancel releases owner, sequence overflow requires HELLO\n");}
