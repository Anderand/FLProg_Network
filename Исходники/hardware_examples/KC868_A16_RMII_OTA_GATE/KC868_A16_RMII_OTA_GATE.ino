/*
 * FLProg_Network OTA hardware gate: KinCony KC868-A16 + LAN8720/RMII.
 *
 * Wi-Fi is intentionally not configured. This verifies ArduinoOTA through
 * the ESP32 core's unified lwIP NetworkUDP/NetworkClient stack using RMII.
 * Upload target port: UDP 3232; the TCP data port is negotiated per upload.
 *
 * KC868-A16 RMII wiring:
 *   LAN8720 PHY address : 0
 *   MDC                 : GPIO23
 *   MDIO                : GPIO18
 *   50 MHz RMII clock   : GPIO17 output
 *
 * Change the temporary test password before flashing. Do not reuse a Wi-Fi
 * password. Keep the test controller on a trusted local network.
 */
#include <flprogNetwork.h>
#include <service/flprogNetworkOta.h>

#ifndef FLPROG_OTA_GATE_PASSWORD
#define FLPROG_OTA_GATE_PASSWORD "change-this-ota-password"
#endif

FLProgNetworkInterface network;
FLProgNetworkOta ota;

static uint32_t lastReportAt = 0;
static bool lastReady = false;
static bool lastOtaReady = false;
static bool lastLink = false;
static IPAddress lastIp;

void setup()
{
    Serial.begin(115200);
    delay(200);
    Serial.println();
    Serial.println(F("FLProg_Network KC868-A16 RMII OTA gate: start"));
    Serial.println(F("Wi-Fi is disabled; OTA must use native RMII only."));

    network.networkMode(FLPROG_NETWORK_MODE_ETHERNET);
    network.wiznetMode(false);
    network.rmiiMode(true);
    network.setWiredPriority(FLPROG_NETWORK_WIRED_PRIORITY_RMII);
    network.setRmiiPhyAddress(0);
    network.setRmiiMdcPin(23);
    network.setRmiiMdioPin(18);
    network.setRmiiClockMode(FLPROG_RMII_CLOCK_GPIO17_OUT);
    network.setRmiiHostname("kc868-a16-rmii-ota");
    network.rmiiDhcpMode(true);
    network.workMode(true);
    network.connect();

    ota.setHostname("kc868-a16-rmii-ota");
    ota.setPasswordValue(FLPROG_OTA_GATE_PASSWORD);
    ota.setRequirePassword(true);
    const bool otaAttached = ota.begin(network);

    Serial.print(F("OTA service attached="));
    Serial.print(otaAttached ? 1 : 0);
    Serial.print(F(" supported="));
    Serial.print(ota.supported() ? 1 : 0);
    Serial.print(F(" passwordRequired="));
    Serial.println(ota.requirePassword() ? 1 : 0);
}

void loop()
{
    // FLProgNetworkInterface::pool() cooperatively services registered OTA.
    network.pool();

    const bool ready = network.rmiiIsReady();
    const bool link = network.rmiiHardware().linkUp();
    const bool otaReady = ota.ready();
    const IPAddress ip = network.rmiiIP();
    if (ready != lastReady || link != lastLink || otaReady != lastOtaReady ||
        ip != lastIp || (uint32_t)(millis() - lastReportAt) >= 5000UL)
    {
        lastReportAt = millis();
        lastReady = ready;
        lastLink = link;
        lastOtaReady = otaReady;
        lastIp = ip;

        Serial.print(F("RMII ready=")); Serial.print(ready ? 1 : 0);
        Serial.print(F(" link=")); Serial.print(link ? 1 : 0);
        Serial.print(F(" ip=")); Serial.print(ip);
        Serial.print(F(" OTA ready=")); Serial.print(otaReady ? 1 : 0);
        Serial.print(F(" state=")); Serial.print(ota.state());
        Serial.print(F(" error=")); Serial.print(ota.error());
        Serial.print(F(" handles=")); Serial.print(ota.handleCount());
        Serial.print(F(" starts=")); Serial.print(ota.updateStartCount());
        Serial.print(F(" ends=")); Serial.print(ota.updateEndCount());
        Serial.print(F(" updateErrors=")); Serial.println(ota.updateErrorCount());
    }
}
