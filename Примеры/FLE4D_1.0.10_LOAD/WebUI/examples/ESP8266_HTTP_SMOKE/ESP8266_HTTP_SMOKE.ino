#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <FLProgWebUi.h>
#include <adapters/FLProgWebUiEsp8266Http.h>

// Local test configuration. Do not publish this sketch with credentials.
const char *WIFI_SSID = "Ud721";
const char *WIFI_PASSWORD = "214365870916";
const IPAddress LOCAL_IP(192, 168, 100, 217);
const IPAddress DNS_IP(192, 168, 100, 1);
const IPAddress GATEWAY_IP(192, 168, 100, 1);
const IPAddress SUBNET_IP(255, 255, 255, 0);
static const FLProgWebUiChannelDescriptor channels[] = {{"temperature", FLPROG_WEBUI_FLOAT, FLPROG_WEBUI_PUBLISH}, {"light", FLPROG_WEBUI_BOOL, FLPROG_WEBUI_DUPLEX}};
static FLProgWebUiChannelSlot slots[2]; static FLProgWebUiModel model(channels, slots, 2);
static ESP8266WebServer server(80); static FLProgWebUiEsp8266Http webUi(model);
void setup() { WiFi.mode(WIFI_STA); WiFi.config(LOCAL_IP, GATEWAY_IP, SUBNET_IP, DNS_IP); WiFi.begin(WIFI_SSID, WIFI_PASSWORD); webUi.begin(server); }
void loop() { webUi.poll(); model.publishFloat(0, 12.2f); model.publishBool(1, false); }
