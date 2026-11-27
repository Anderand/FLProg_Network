#include <cassert>
#include <cstdio>
#include <flprogNetwork.h>
uint32_t fakeNow=0;
EthernetClass Ethernet;

static void testColdStartStatusAndExplicitBusZero() {
  Ethernet=EthernetClass{}; fakeNow=100;
  FLProgWiznetInterface wiz(10,0);
  assert(wiz.begin(IPAddress(192,168,1,50),IPAddress(192,168,1,1),IPAddress(192,168,1,1),IPAddress(255,255,255,0))==FLPROG_NETWORK_SUCCESS);
  assert(wiz.getStatus()==FLProgWiznetInterface::STATUS_READY);
  assert(wiz.isReady());
  assert(Ethernet.initCalls>=1);
  assert(Ethernet.beginCalls==1);
}
static void testAbsentHardwareWaitsAndRetries() {
  Ethernet=EthernetClass{}; Ethernet.physical=false; fakeNow=100;
  FLProgWiznetInterface wiz(10,0);
  assert(wiz.begin()==FLPROG_NETWORK_ERROR);
  assert(wiz.getStatus()==FLProgWiznetInterface::STATUS_ERROR);
  assert(wiz.getError()==FLProgWiznetInterface::ERROR_HARDWARE);
  int starts=Ethernet.beginCalls;
  for(int i=0;i<100;i++) { ++fakeNow; assert(wiz.pool()==FLPROG_NETWORK_ERROR); }
  assert(Ethernet.beginCalls==starts);
  Ethernet.physical=true; fakeNow+=15000;
  assert(wiz.pool()==FLPROG_NETWORK_SUCCESS);
  assert(Ethernet.beginCalls==starts+1);
}
static void testLinkRetryDoesNotBusyLoop() {
  Ethernet=EthernetClass{}; fakeNow=100;
  FLProgWiznetInterface wiz(10,0);
  wiz.resetDhcp(); wiz.localIP(IPAddress(192,168,1,50));
  assert(wiz.begin()==FLPROG_NETWORK_SUCCESS);
  Ethernet.carrier=false; fakeNow+=1000;
  assert(wiz.pool()==FLPROG_NETWORK_WAIT);
  int starts=Ethernet.beginCalls;
  int linkChecks=Ethernet.linkCalls;
  for(int i=0;i<20;i++) assert(wiz.pool()==FLPROG_NETWORK_WAIT);
  assert(Ethernet.linkCalls==linkChecks);
  assert(Ethernet.beginCalls==starts);
  Ethernet.carrier=true; fakeNow+=15000;
  assert(wiz.pool()==FLPROG_NETWORK_SUCCESS);
  assert(Ethernet.beginCalls==starts+1);
}
static void testDhcpRetryAndMaintainSemantics() {
  Ethernet=EthernetClass{}; Ethernet.dhcpSuccess=false; fakeNow=100;
  FLProgWiznetInterface wiz(10,0); wiz.setDhcp();
  assert(wiz.begin()==FLPROG_NETWORK_ERROR);
  int starts=Ethernet.beginCalls;
  for(int i=0;i<100;i++) { ++fakeNow; assert(wiz.pool()==FLPROG_NETWORK_ERROR); }
  assert(Ethernet.beginCalls==starts);
  fakeNow+=15000; Ethernet.dhcpSuccess=true;
  assert(wiz.pool()==FLPROG_NETWORK_SUCCESS);
  assert(Ethernet.beginCalls==starts+1);
  fakeNow+=1000; Ethernet.maintainResult=1; // renewal failed; lease remains usable
  assert(wiz.pool()==FLPROG_NETWORK_SUCCESS);
  assert(Ethernet.maintainCalls==1 && wiz.isReady());
  fakeNow+=1000; Ethernet.maintainResult=3; // rebind failed; lease must be discarded
  assert(wiz.pool()==FLPROG_NETWORK_WAIT);
  assert(!wiz.isReady());
  assert(Ethernet.ip[0]==0 && Ethernet.ip[1]==0 && Ethernet.ip[2]==0 && Ethernet.ip[3]==0);
  starts=Ethernet.beginCalls;
  for(int i=0;i<100;i++) { ++fakeNow; assert(wiz.pool()==FLPROG_NETWORK_WAIT); }
  assert(Ethernet.beginCalls==starts);
  fakeNow+=15000;
  assert(wiz.pool()==FLPROG_NETWORK_SUCCESS);
  assert(Ethernet.beginCalls==starts+1);
}
int main() {
  testColdStartStatusAndExplicitBusZero();
  testAbsentHardwareWaitsAndRetries();
  testLinkRetryDoesNotBusyLoop();
  testDhcpRetryAndMaintainSemantics();
  std::puts("AVR-lite fake behavior checks passed");
}

