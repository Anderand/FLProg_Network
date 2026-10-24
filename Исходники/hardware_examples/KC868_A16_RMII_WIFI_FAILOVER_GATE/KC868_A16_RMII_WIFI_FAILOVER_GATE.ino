/*
 * FLProg_Network hardware gate: KinCony KC868-A16 LAN8720 RMII + Wi-Fi STA.
 *
 * One HTTP diagnostic application is shared between two physical interfaces:
 *   - RMII/LAN8720 (DHCP), fixed listener on route RMII;
 *   - Wi-Fi STA (DHCP), shared listener on route Wi-Fi.
 *
 * The serial console prints both addresses every five seconds.  The Wi-Fi
 * password is intentionally never sent over HTTP or written to the console.
 */
#include <flprogNetwork.h>
#include <service/flprogNetworkHttpServer.h>

static const char WIFI_SSID[] = "Ud721";
static const char WIFI_PASSWORD[] = "214365870916";

FLProgNetworkInterface network;
FLProgNetworkHttpServer httpServer(&network, 80);

static bool rmiiListenerConfigured = false;
static bool wifiListenerConfigured = false;
static uint32_t lastStatusAt = 0;

static void sendStatus(FLProgNetworkHttpServer *server)
{
    String json;
    json.reserve(430);
    json += F("{\"rmii\":{\"ready\":");
    json += network.rmiiIsReady() ? F("true") : F("false");
    json += F(",\"link\":");
    json += network.rmiiHardware().linkUp() ? F("true") : F("false");
    json += F(",\"ip\":\"");
    json += network.rmiiIP().toString();
    json += F("\"},\"wifi\":{\"ready\":");
    json += network.wifiIsReady() ? F("true") : F("false");
    json += F(",\"ip\":\"");
    json += network.wifiIP().toString();
    json += F("\"},\"bothReady\":");
    json += network.bothInterfacesReady() ? F("true") : F("false");
    json += F(",\"error\":");
    json += String(network.getError());
    json += F(",\"http\":{\"listening\":");
    json += httpServer.listening() ? F("true") : F("false");
    json += F(",\"sharedListeners\":");
    json += String(httpServer.sharedListenerCount());
    json += F("}}");
    server->send(200, "application/json; charset=utf-8", json.c_str());
}

static void sendPage(FLProgNetworkHttpServer *server)
{
    String page;
    page.reserve(1150);
    page += F("<!doctype html><meta charset=utf-8>"
              "<meta name=viewport content='width=device-width,initial-scale=1'>"
              "<title>KC868-A16 dual network gate</title>"
              "<style>body{font:16px system-ui;margin:2rem;background:#101827;color:#e7edf8}"
              "h1{font-size:1.45rem}table{border-collapse:collapse;min-width:22rem}"
              "td{padding:.45rem .8rem;border-bottom:1px solid #334155}"
              ".ok{color:#4ade80}.wait{color:#fbbf24}code{padding:.16rem .38rem;background:#1e293b;border-radius:.25rem}</style>");
    page += F("<h1>KC868-A16: RMII + Wi-Fi gate</h1><p>One FLProg_Network HTTP server, two physical routes.</p><table>");
    page += F("<tr><td>RMII / link / IP</td><td class=");
    page += network.rmiiIsReady() ? F("ok>") : F("wait>");
    page += network.rmiiIsReady() ? F("ready") : F("waiting");
    page += F(" / "); page += network.rmiiHardware().linkUp() ? F("up") : F("down");
    page += F(" / "); page += network.rmiiIP().toString(); page += F("</td></tr>");
    page += F("<tr><td>Wi-Fi STA / IP</td><td class=");
    page += network.wifiIsReady() ? F("ok>") : F("wait>");
    page += network.wifiIsReady() ? F("ready") : F("waiting");
    page += F(" / "); page += network.wifiIP().toString(); page += F("</td></tr>");
    page += F("<tr><td>Both interfaces</td><td>");
    page += network.bothInterfacesReady() ? F("<span class=ok>ready</span>") : F("<span class=wait>waiting</span>");
    page += F("</td></tr><tr><td>HTTP listeners</td><td>");
    page += httpServer.listening() ? F("active") : F("waiting");
    page += F(" / shared: "); page += String(httpServer.sharedListenerCount());
    page += F("</td></tr><tr><td>Network error</td><td>"); page += String(network.getError());
    page += F("</td></tr></table><p><a href=/api/status>JSON status</a></p>");
    server->send(200, "text/html; charset=utf-8", page.c_str());
}

static void printStatus()
{
    Serial.print(F("RMII ready=")); Serial.print(network.rmiiIsReady());
    Serial.print(F(" link=")); Serial.print(network.rmiiHardware().linkUp());
    Serial.print(F(" ip=")); Serial.print(network.rmiiIP());
    Serial.print(F(" | WiFi ready=")); Serial.print(network.wifiIsReady());
    Serial.print(F(" ip=")); Serial.print(network.wifiIP());
    Serial.print(F(" | both=")); Serial.print(network.bothInterfacesReady());
    Serial.print(F(" http=")); Serial.print(httpServer.listening());
    Serial.print(F(" shared=")); Serial.print(httpServer.sharedListenerCount());
    Serial.print(F(" error=")); Serial.println(network.getError());
}

void setup()
{
    Serial.begin(115200);
    delay(200);
    Serial.println();
    Serial.println(F("FLProg_Network KC868-A16 RMII + Wi-Fi gate: start"));

    network.networkMode(FLPROG_NETWORK_MODE_BOTH);
    network.wiznetMode(false);
    network.rmiiMode(true);
    network.setWiredPriority(FLPROG_NETWORK_WIRED_PRIORITY_RMII);
    network.setRmiiPhyAddress(0);
    network.setRmiiMdcPin(23);
    network.setRmiiMdioPin(18);
    network.setRmiiClockMode(FLPROG_RMII_CLOCK_GPIO17_OUT);
    network.setRmiiHostname("flprog-kc868-a16-rmii");
    network.rmiiDhcpMode(true);

    network.clientMode(true);
    network.setAutoConnect(true);
    network.setAutoReconnect(true);
    network.setClientSsid(WIFI_SSID);
    network.setClientPassword(WIFI_PASSWORD);

    network.workMode(true);
    network.connect();

    httpServer.setBrowserHeaderCompatibility(true);
    httpServer.addHandler("/", sendPage, FLPROG_WEB_SERVER_GET);
    httpServer.addHandler("/api/status", sendStatus, FLPROG_WEB_SERVER_GET);
    // Shared listeners reuse one parser context and therefore require exactly
    // one client slot on the primary listener.
    rmiiListenerConfigured = httpServer.begin(network, 80, FLPROG_NETWORK_ROUTE_RMII, 1);
    Serial.print(F("HTTP routes configured: RMII=")); Serial.print(rmiiListenerConfigured);
    Serial.println(F("; Wi-Fi listener waits for the RMII listener to start."));
    Serial.println(F("Both interfaces request DHCP. Open either IP printed below."));
}

void loop()
{
    network.pool();
    httpServer.pool();

    // The primary HTTP listener is started lazily by pool().  A shared route
    // may be attached only after that listener is live.
    if (!wifiListenerConfigured && httpServer.listening())
    {
        wifiListenerConfigured = httpServer.addSharedListener(network, FLPROG_NETWORK_ROUTE_WIFI);
        Serial.print(F("HTTP Wi-Fi shared listener="));
        Serial.println(wifiListenerConfigured);
    }

    if (millis() - lastStatusAt >= 5000)
    {
        lastStatusAt = millis();
        printStatus();
    }
}
