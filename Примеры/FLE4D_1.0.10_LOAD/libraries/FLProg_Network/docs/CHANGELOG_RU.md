# Изменения

## dev.17-pr28 — 27.09.2026

- Синхронизирована релизная идентичность `library.properties` и
  `FLPROG_NETWORK_VERSION_STRING`.
- Подтверждён shared HTTP на ESP8266 одновременно через Wi-Fi STA и 2×W5500.
- Legacy `FLProgOTA` переведён на адаптер над `FLProgNetworkOta`; OTA upload
  и регрессия HTTP/W5500 после него пройдены на устройстве.
- ESP32 и RP2040 PR28 собраны успешно.

## EXP-2A-fix4 (историческое)

- Сохранена закрытая A3 архитектура TransportIdentity/NET NUM/socket lifecycle.
- Добавлен Wi-Fi-only compile-time профиль.
- Удалены W5500/RMII/DHCP wired объекты из FLProgNetworkInterface в Wi-Fi-only профиле.
- Исключены wired DNS/UDP/socket backend ветки из Wi-Fi-only линковки.
- Исправлен `dhcpMode()` для Wi-Fi-only: больше не требует Wiznet DHCP.
- TCP Client в Wi-Fi-only больше не требует `wiznetHardware()`.
- Удалены физические WIZnet/RMII backend-поля из TCP/UDP Wi-Fi-only пути.
- Подтверждены реальные TCP echo и reconnect тесты.
