# Target Architecture

## FLProg_Network
### Core
NET NUM, Device Registry, TransportIdentity, Routing, SocketManager, Socket.

### Transport
WiFi, W5500, RMII/LAN8720 — compile-time modular.

### Protocol
TCP Client/Server, UDP, DHCP, DNS, ARP, MACRAW — included only when required by the selected profile.

### Hardware
SPI backend/arbiter, W5500 hardware, RMII hardware.

## Services
HTTP Client/Server, MQTT, NTP and OTA are part of `FLProg_Network`. They use
the common transport/network-manager layer and are not a separate library.
This is the adopted API level 10006 decision.

## Core principle
A firmware image should spend RAM/IRAM/Flash only on the transports and
protocols it actually uses. Services remain one compatibility-oriented package
for generated FLProg projects; unused implementations are linker-eliminated
where possible.
