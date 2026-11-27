#include <flprogEthernet.h>
#include <Ethernet.h>
#include <EthernetUdp.h>

FLProgWiznetInterface wiznet(10);
EthernetServer tcpServer(8080);
EthernetUDP udp;
static uint8_t udpBuffer[32];

void setup() {
  wiznet.mac(0x02, 0x00, 0x00, 0x00, 0x00, 0x01);
  wiznet.begin(IPAddress(192, 168, 1, 50), IPAddress(192, 168, 1, 1),
               IPAddress(192, 168, 1, 1), IPAddress(255, 255, 255, 0));
  tcpServer.begin();
  udp.begin(8888);
}

void loop() {
  wiznet.pool();
  EthernetClient client = tcpServer.available();
  if (client) {
    while (client.available()) client.write((uint8_t)client.read());
    if (!client.connected()) client.stop();
  }
  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    int count = udp.read(udpBuffer, sizeof(udpBuffer));
    if (count > 0 && udp.beginPacket(udp.remoteIP(), udp.remotePort())) {
      udp.write(udpBuffer, (size_t)count);
      udp.endPacket();
    }
  }
}
