#include <flprogEthernet.h>
#include "flprogUtilites.h"
FLProgWiznetInterface wiz(10);
void setup() {
  flprog::specialSetup();
  wiz.mac(0x02, 0, 0, 0, 0, 1);
  wiz.setSkippingEvents(0);
  wiz.setDhcp();
  flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)1, &wiz);
}
void loop() {
  wiz.pool();
  flprog::specialPool();
}
