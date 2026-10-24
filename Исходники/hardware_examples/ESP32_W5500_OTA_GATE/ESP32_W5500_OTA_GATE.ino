/*
 * FLProg_Network W5500 OTA hardware gate for ESP32.
 * Uses the route-aware FLProgNetworkOtaWiznet service and Arduino espota.py
 * protocol, over FLProg_Network-managed UDP/TCP sockets.
 *
 * Default SPI wiring below matches a common ESP32 DevKit + W5500 module.
 * Adjust all four pins to match your actual board before flashing.
 */
#include <flprogNetwork.h>

#ifndef FLPROG_W5500_OTA_PASSWORD
#define FLPROG_W5500_OTA_PASSWORD "change-this-ota-password"
#endif

#ifndef FLPROG_W5500_CS_PIN
#define FLPROG_W5500_CS_PIN 5
#endif
#ifndef FLPROG_W5500_SCK_PIN
#define FLPROG_W5500_SCK_PIN 18
#endif
#ifndef FLPROG_W5500_MISO_PIN
#define FLPROG_W5500_MISO_PIN 19
#endif
#ifndef FLPROG_W5500_MOSI_PIN
#define FLPROG_W5500_MOSI_PIN 23
#endif

FLProgNetworkInterface network;
FLProgNetworkOtaWiznet ota;
static uint32_t lastReportAt = 0;

void setup()
{
    Serial.begin(115200);
    delay(200);
    Serial.println();
    Serial.println(F("FLProg_Network ESP32 W5500 OTA gate: start"));
    Serial.println(F("Wi-Fi and RMII are disabled; OTA uses W5500 only."));

    network.networkMode(FLPROG_NETWORK_MODE_ETHERNET);
    network.wiznetMode(true);
    network.rmiiMode(false);
    network.setPinCs(FLPROG_W5500_CS_PIN);
    network.setSpiPins(FLPROG_W5500_SCK_PIN, FLPROG_W5500_MISO_PIN, FLPROG_W5500_MOSI_PIN);
    network.dhcpMode(true);
    network.workMode(true);
    network.connect();

    const bool otaAttached = ota.begin(network, FLPROG_W5500_OTA_PASSWORD, 3232);
    Serial.print(F("W5500 OTA attached="));
    Serial.print(otaAttached ? 1 : 0);
    Serial.print(F(" supported="));
    Serial.println(ota.supported() ? 1 : 0);
}

void loop()
{
    network.pool();
    if ((uint32_t)(millis() - lastReportAt) >= 5000UL)
    {
        lastReportAt = millis();
        Serial.print(F("W5500 ready=")); Serial.print(network.wiznetIsReady() ? 1 : 0);
        Serial.print(F(" ip=")); Serial.print(network.wiznetIP());
        Serial.print(F(" OTA ready=")); Serial.print(ota.ready() ? 1 : 0);
        Serial.print(F(" updating=")); Serial.print(ota.updating() ? 1 : 0);
        Serial.print(F(" error=")); Serial.print(ota.error());
        Serial.print(F(" bytes=")); Serial.print(ota.bytesReceived());
        Serial.print(F(" starts=")); Serial.print(ota.updateStartCount());
        Serial.print(F(" ends=")); Serial.print(ota.updateEndCount());
        Serial.print(F(" updateErrors=")); Serial.println(ota.updateErrorCount());
    }
}
