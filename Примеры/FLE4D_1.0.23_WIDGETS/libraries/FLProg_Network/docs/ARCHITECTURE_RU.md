# Целевая архитектура

## FLProg_Network
### Core
NET NUM, Device Registry, TransportIdentity, Routing, SocketManager, Socket.

### Transport
WiFi, W5500, RMII/LAN8720 — compile-time модульные.

### Protocol
TCP Client/Server, UDP, DHCP, DNS, ARP, MACRAW — подключаются только когда нужны профилю.

### Hardware
SPI backend/arbiter, W5500 hardware, RMII hardware.

## Сервисы
HTTP Client/Server, MQTT, NTP и OTA являются частью `FLProg_Network`.
Они используют общий transport/network-manager слой и не образуют отдельную
библиотеку. Это принятое решение для текущего API `10006`.

## Ключевой принцип
Конкретная прошивка должна оплачивать RAM/IRAM/Flash только за реально
используемые транспорты и протоколы. Для сервисов сохранён один общий
пакет ради совместимости generated FLProg-проектов; неиспользуемые
реализации исключаются линкером, когда это возможно.
