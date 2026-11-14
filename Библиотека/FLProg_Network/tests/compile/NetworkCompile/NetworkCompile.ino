#include <flprogEthernet.h>
static_assert(FLPROG_NETWORK_VERSION_DEV == 20, "Expected dev20");
FLProgWiznetInterface wired(5, 0);
FLProgOnBoardWifiInterface wifi;
#if defined(ESP32)
FLProgNetworkInterface rmii;
#endif
volatile uint8_t result = 0;
void setup() {
 flprogNetworkDevices.registerDevice(1, wired);
 flprogNetworkDevices.registerDevice(2, wifi);
 result = wired.setPinRST(255);
 result = wired.setSpeedSPI(20000000UL);
 result = ethSetStartupDelay(1, 500);
 result = flprogNetworkDevices.existsWiznet(1);
 result = flprogNetworkDevices.existsWifi(2);
 auto *w = flprogNetworkDevices.getWiznet(1);
 auto *f = flprogNetworkDevices.getWifi(2);
 result = (w != nullptr && f != nullptr);
#if defined(ESP32)
 rmii.networkMode(FLPROG_NETWORK_MODE_ETHERNET);
 rmii.wiznetMode(false); rmii.rmiiMode(true);
 rmii.setRmiiPhyAddress(0); rmii.setRmiiMdcPin(23); rmii.setRmiiMdioPin(18);
 rmii.setRmiiClockMode(FLPROG_RMII_CLOCK_GPIO17_OUT);
#endif
}
void loop() { wired.pool(); wifi.pool();
#if defined(ESP32)
rmii.pool();
#endif
}
