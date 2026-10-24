/*
 * FLProg_Network gate: KC868-A16 LAN8720/RMII + Wi-Fi STA TCP/UDP.
 *
 * The same port numbers are deliberately bound to both physical routes:
 *   HTTP diagnostics: 80
 *   TCP echo:          5001
 *   UDP echo:          5002
 *
 * HTTP has one shared parser context. TCP and UDP have separate route-fixed
 * sockets, so a connection/packet proves which physical interface carried it.
 */
#include <flprogNetwork.h>
#include <service/flprogNetworkHttpServer.h>
#include <protocol/flprogNetworkTcpServer.h>
#include <protocol/flprogNetworkUdp.h>

static const char WIFI_SSID[] = "Ud721";
static const char WIFI_PASSWORD[] = "214365870916";
static const uint16_t TCP_PORT = 5001;
static const uint16_t UDP_PORT = 5002;

struct TrafficStats
{
    uint32_t tcpConnections = 0;
    uint32_t tcpRx = 0;
    uint32_t tcpTx = 0;
    uint32_t udpPackets = 0;
    uint32_t udpRx = 0;
    uint32_t udpTx = 0;
    uint32_t udpSendFailures = 0;
};

FLProgNetworkInterface network;
FLProgNetworkHttpServer httpServer(&network, 80);
FLProgNetworkTcpServer tcpRmii;
FLProgNetworkTcpServer tcpWifi;
FLProgNetworkUdp udpRmii;
FLProgNetworkUdp udpWifi;
TrafficStats rmiiStats;
TrafficStats wifiStats;

static bool wifiHttpConfigured = false;
static uint32_t lastStatusAt = 0;

static void appendStatsJson(String &json, const TrafficStats &stats)
{
    json += F("{\"connections\":"); json += String(stats.tcpConnections);
    json += F(",\"tcpRx\":"); json += String(stats.tcpRx);
    json += F(",\"tcpTx\":"); json += String(stats.tcpTx);
    json += F(",\"udpPackets\":"); json += String(stats.udpPackets);
    json += F(",\"udpRx\":"); json += String(stats.udpRx);
    json += F(",\"udpTx\":"); json += String(stats.udpTx);
    json += F(",\"udpSendFailures\":"); json += String(stats.udpSendFailures); json += F("}");
}

static void sendStatus(FLProgNetworkHttpServer *server)
{
    String json;
    json.reserve(600);
    json += F("{\"rmii\":{\"ready\":"); json += network.rmiiIsReady() ? F("true") : F("false");
    json += F(",\"link\":"); json += network.rmiiHardware().linkUp() ? F("true") : F("false");
    json += F(",\"ip\":\""); json += network.rmiiIP().toString(); json += F("\",\"traffic\":"); appendStatsJson(json, rmiiStats); json += F("}");
    json += F(",\"wifi\":{\"ready\":"); json += network.wifiIsReady() ? F("true") : F("false");
    json += F(",\"ip\":\""); json += network.wifiIP().toString(); json += F("\",\"traffic\":"); appendStatsJson(json, wifiStats); json += F("}");
    json += F(",\"httpShared\":"); json += String(httpServer.sharedListenerCount());
    json += F(",\"tcpPort\":"); json += String(TCP_PORT);
    json += F(",\"udpPort\":"); json += String(UDP_PORT);
    json += F(",\"error\":"); json += String(network.getError()); json += F("}");
    server->send(200, "application/json; charset=utf-8", json.c_str());
}

static void addStatsRows(String &page, const char *name, const TrafficStats &stats)
{
    page += F("<tr><td>"); page += name; page += F(" TCP connections / RX / TX</td><td>");
    page += String(stats.tcpConnections); page += F(" / "); page += String(stats.tcpRx); page += F(" / "); page += String(stats.tcpTx); page += F(" B</td></tr>");
    page += F("<tr><td>"); page += name; page += F(" UDP packets / RX / TX</td><td>");
    page += String(stats.udpPackets); page += F(" / "); page += String(stats.udpRx); page += F(" / "); page += String(stats.udpTx); page += F(" B</td></tr>");
}

static void sendPage(FLProgNetworkHttpServer *server)
{
    String page;
    page.reserve(1550);
    page += F("<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>KC868 dual TCP UDP gate</title>"
              "<style>body{font:16px system-ui;margin:2rem;background:#101827;color:#e7edf8}h1{font-size:1.45rem}table{border-collapse:collapse;min-width:31rem}td{padding:.45rem .8rem;border-bottom:1px solid #334155}.ok{color:#4ade80}code{padding:.16rem .38rem;background:#1e293b;border-radius:.25rem}</style>");
    page += F("<h1>KC868-A16: RMII + Wi-Fi TCP/UDP gate</h1><p>TCP echo <code>:5001</code>; UDP echo <code>:5002</code> on both interfaces.</p><table>");
    page += F("<tr><td>RMII / link / IP</td><td class=ok>"); page += network.rmiiIsReady() ? F("ready") : F("waiting"); page += F(" / "); page += network.rmiiHardware().linkUp() ? F("up") : F("down"); page += F(" / "); page += network.rmiiIP().toString(); page += F("</td></tr>");
    page += F("<tr><td>Wi-Fi STA / IP</td><td class=ok>"); page += network.wifiIsReady() ? F("ready") : F("waiting"); page += F(" / "); page += network.wifiIP().toString(); page += F("</td></tr>");
    addStatsRows(page, "RMII", rmiiStats);
    addStatsRows(page, "Wi-Fi", wifiStats);
    page += F("<tr><td>HTTP shared listener / error</td><td>"); page += String(httpServer.sharedListenerCount()); page += F(" / "); page += String(network.getError()); page += F("</td></tr></table><p><a href=/api/status>JSON status</a></p>");
    server->send(200, "text/html; charset=utf-8", page.c_str());
}

static void processTcp(FLProgNetworkTcpServer &tcp, TrafficStats &stats)
{
    const uint8_t events = tcp.takeEvents();
    if ((events & FLPROG_TCP_SERVER_EVENT_NEW_CLIENT) != 0) ++stats.tcpConnections;
    uint8_t buffer[192];
    for (uint8_t slot = 0; slot < tcp.maxClients(); ++slot)
    {
        FLProgNetworkTcpServerClient *client = tcp.client(slot);
        if (client == nullptr || !client->active()) continue;
        const int received = client->read(buffer, sizeof(buffer));
        if (received <= 0) continue;
        stats.tcpRx += (uint32_t)received;
        stats.tcpTx += (uint32_t)client->write(buffer, (size_t)received);
    }
}

static void processUdp(FLProgNetworkUdp &udp, TrafficStats &stats)
{
    const int packetSize = udp.parsePacket();
    if (packetSize <= 0) return;
    const IPAddress peerIp = udp.remoteIP();
    const uint16_t peerPort = udp.remotePort();
    uint8_t buffer[256];
    const int received = udp.read(buffer, (size_t)min(packetSize, (int)sizeof(buffer)));
    if (received <= 0) return;
    ++stats.udpPackets;
    stats.udpRx += (uint32_t)received;
    if (udp.beginPacket(peerIp, peerPort) == FLPROG_UDP_RESULT_SUCCESS)
    {
        const size_t buffered = udp.write(buffer, (size_t)received);
        if (buffered == (size_t)received && udp.endPacket() == FLPROG_UDP_RESULT_SUCCESS)
        {
            stats.udpTx += (uint32_t)buffered;
        }
        else
        {
            ++stats.udpSendFailures;
        }
    }
    else
    {
        ++stats.udpSendFailures;
    }
}

static void printStatus()
{
    Serial.print(F("RMII ip=")); Serial.print(network.rmiiIP());
    Serial.print(F(" link=")); Serial.print(network.rmiiHardware().linkUp());
    Serial.print(F(" tcp=")); Serial.print(tcpRmii.listening());
    Serial.print(F(" udp=")); Serial.print(rmiiStats.udpPackets);
    Serial.print(F(" | WiFi ip=")); Serial.print(network.wifiIP());
    Serial.print(F(" tcp=")); Serial.print(tcpWifi.listening());
    Serial.print(F(" udp=")); Serial.print(wifiStats.udpPackets);
    Serial.print(F(" | httpShared=")); Serial.print(httpServer.sharedListenerCount());
    Serial.print(F(" error=")); Serial.println(network.getError());
}

void setup()
{
    Serial.begin(115200);
    delay(200);
    Serial.println();
    Serial.println(F("FLProg_Network KC868-A16 dual TCP/UDP gate: start"));

    network.networkMode(FLPROG_NETWORK_MODE_BOTH);
    network.wiznetMode(false);
    network.rmiiMode(true);
    network.setWiredPriority(FLPROG_NETWORK_WIRED_PRIORITY_RMII);
    network.setRmiiPhyAddress(0);
    network.setRmiiMdcPin(23);
    network.setRmiiMdioPin(18);
    network.setRmiiClockMode(FLPROG_RMII_CLOCK_GPIO17_OUT);
    network.setRmiiHostname("flprog-kc868-a16-dual");
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
    httpServer.begin(network, 80, FLPROG_NETWORK_ROUTE_RMII, 1);
    tcpRmii.begin(network, TCP_PORT, FLPROG_NETWORK_ROUTE_RMII, 1);
    tcpWifi.begin(network, TCP_PORT, FLPROG_NETWORK_ROUTE_WIFI, 1);
    udpRmii.begin(network, FLPROG_NETWORK_ROUTE_RMII, UDP_PORT);
    udpWifi.begin(network, FLPROG_NETWORK_ROUTE_WIFI, UDP_PORT);
    Serial.println(F("RMII/Wi-Fi TCP :5001 and UDP :5002 requested."));
}

void loop()
{
    network.pool();
    httpServer.pool();
    if (!wifiHttpConfigured && httpServer.listening())
    {
        wifiHttpConfigured = httpServer.addSharedListener(network, FLPROG_NETWORK_ROUTE_WIFI);
        if (wifiHttpConfigured) Serial.println(F("HTTP Wi-Fi shared listener=1"));
    }
    processTcp(tcpRmii, rmiiStats);
    processTcp(tcpWifi, wifiStats);
    processUdp(udpRmii, rmiiStats);
    processUdp(udpWifi, wifiStats);
    if (millis() - lastStatusAt >= 5000)
    {
        lastStatusAt = millis();
        printStatus();
    }
}
