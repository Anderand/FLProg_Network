/*
 * FLProg_Network hardware gate: KinCony KC868-A16 + LAN8720 (RMII).
 *
 * Purpose: hardware verification of the native ESP32 RMII transport without
 * Wi-Fi, W5500, FLProg-generated code or application I/O.  The test obtains
 * an address by DHCP, exposes a small HTTP diagnostics page, and reports
 * link/IP/MAC changes to Serial.
 *
 * Board wiring is fixed by KC868-A16:
 *   LAN8720 PHY address : 0
 *   MDC                : GPIO23
 *   MDIO               : GPIO18
 *   50 MHz RMII clock  : GPIO17 output
 */
#include <flprogNetwork.h>
#include <service/flprogNetworkHttpServer.h>

FLProgNetworkInterface network;
FLProgNetworkHttpServer httpServer(&network, 80);

static uint32_t lastReportAt = 0;
static bool lastReady = false;
static bool lastLink = false;
static IPAddress lastIp;

static String ipText(IPAddress value)
{
    return value.toString();
}

static void sendStatusPage(FLProgNetworkHttpServer *server)
{
    const FLProgRmiiEthernet &rmii = network.rmiiHardware();
    String page;
    page.reserve(1100);
    page += F("<!doctype html><meta charset=utf-8><title>FLProg RMII gate</title>");
    page += F("<style>body{font:16px system-ui;margin:2rem;background:#101827;color:#e7edf8}"
              "table{border-collapse:collapse}td{padding:.45rem 1rem;border-bottom:1px solid #334155}"
              "b{color:#7dd3fc}</style><h1>KC868-A16 — RMII/LAN8720</h1><table>");
    page += F("<tr><td>RMII ready</td><td><b>"); page += network.rmiiIsReady() ? F("yes") : F("no"); page += F("</b></td></tr>");
    page += F("<tr><td>Link</td><td><b>"); page += rmii.linkUp() ? F("up") : F("down"); page += F("</b></td></tr>");
    page += F("<tr><td>IP</td><td>"); page += ipText(network.rmiiIP()); page += F("</td></tr>");
    page += F("<tr><td>Gateway</td><td>"); page += ipText(rmii.currentGateway()); page += F("</td></tr>");
    page += F("<tr><td>DNS</td><td>"); page += ipText(rmii.currentDns()); page += F("</td></tr>");
    page += F("<tr><td>MAC</td><td>"); page += rmii.macAddress(); page += F("</td></tr>");
    page += F("<tr><td>Speed</td><td>"); page += String(rmii.linkSpeed()); page += F(" Mbps</td></tr>");
    page += F("<tr><td>Duplex</td><td>"); page += rmii.fullDuplex() ? F("full") : F("half"); page += F("</td></tr>");
    page += F("<tr><td>Network error</td><td>"); page += String(network.getError()); page += F("</td></tr>");
    page += F("</table><p>Refresh the page after plugging or unplugging the Ethernet cable.</p>");
    server->send(200, "text/html; charset=utf-8", page.c_str());
}

static void sendStatusJson(FLProgNetworkHttpServer *server)
{
    const FLProgRmiiEthernet &rmii = network.rmiiHardware();
    String json;
    json.reserve(420);
    json += F("{\"ready\":"); json += network.rmiiIsReady() ? F("true") : F("false");
    json += F(",\"link\":"); json += rmii.linkUp() ? F("true") : F("false");
    json += F(",\"ip\":\""); json += ipText(network.rmiiIP());
    json += F("\",\"gateway\":\""); json += ipText(rmii.currentGateway());
    json += F("\",\"dns\":\""); json += ipText(rmii.currentDns());
    json += F("\",\"mac\":\""); json += rmii.macAddress();
    json += F("\",\"speedMbps\":"); json += String(rmii.linkSpeed());
    json += F(",\"fullDuplex\":"); json += rmii.fullDuplex() ? F("true") : F("false");
    json += F(",\"error\":"); json += String(network.getError()); json += F("}");
    server->send(200, "application/json", json.c_str());
}

void setup()
{
    Serial.begin(115200);
    delay(200);
    Serial.println();
    Serial.println(F("FLProg_Network KC868-A16 RMII gate: start"));

    network.networkMode(FLPROG_NETWORK_MODE_ETHERNET);
    network.wiznetMode(false);
    network.rmiiMode(true);
    network.setWiredPriority(FLPROG_NETWORK_WIRED_PRIORITY_RMII);
    network.setRmiiPhyAddress(0);
    network.setRmiiMdcPin(23);
    network.setRmiiMdioPin(18);
    network.setRmiiClockMode(FLPROG_RMII_CLOCK_GPIO17_OUT);
    network.setRmiiHostname("flprog-kc868-a16");
    network.rmiiDhcpMode(true);
    network.workMode(true);
    network.connect();

    httpServer.addHandler("/", sendStatusPage, FLPROG_WEB_SERVER_GET);
    httpServer.addHandler("/api/status", sendStatusJson, FLPROG_WEB_SERVER_GET);
    Serial.println(F("RMII DHCP requested; wait for link and IP."));
}

void loop()
{
    network.pool();
    httpServer.pool();

    const bool ready = network.rmiiIsReady();
    const bool link = network.rmiiHardware().linkUp();
    const IPAddress ip = network.rmiiIP();
    if (ready != lastReady || link != lastLink || ip != lastIp || millis() - lastReportAt >= 5000UL)
    {
        lastReportAt = millis();
        lastReady = ready;
        lastLink = link;
        lastIp = ip;
        Serial.print(F("RMII ready=")); Serial.print(ready);
        Serial.print(F(" link=")); Serial.print(link);
        Serial.print(F(" ip=")); Serial.print(ip);
        Serial.print(F(" error=")); Serial.println(network.getError());
    }
}
