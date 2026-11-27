# FLProg_Network dev.17-pr28

Дата релизного snapshot: 27.09.2026.

Библиотека реализует единый transport/network-manager слой для generated
FLProg-проектов с Wi-Fi STA/AP, W5500 и RMII. API level: `10006`.

## Что уже подтверждено на ESP8266

- NET NUM / Device Registry — PASS.
- TransportIdentity — PASS.
- A1 + A2 Wi-Fi DHCP — PASS.
- TCP Client через Wi-Fi — PASS.
- TCP echo TX/RX — PASS.
- Потеря TCP echo-сервера и повторное подключение — PASS.
- Shared HTTP одновременно работает через Wi-Fi STA и два W5500.
- Wi-Fi OTA работает через совместимый фасад над `FLProgNetworkOta`.

## Важное ограничение

OTA реализована только через Wi-Fi STA. Для legacy shared HTTP с одним
context burst-запрос в окне переоткрытия W5500 LISTEN может получить отказ;
это задокументированное ограничение последовательной обработки.

## Проверенный результат

ESP8266: HTTP `200` на Wi-Fi `.217` и W5500 `.218`/`.219`, OTA upload и
последующая регрессия подтверждены. ESP32 и RP2040 PR28 собраны успешно.
Подробности: `docs/CURRENT_RELEASE_STATUS_RU.md`.

## Комментарии в исходниках

Все `.h/.cpp` в `src` и исполняемые примеры содержат расширенные комментарии
на русском и английском. Правило обновления описано в
`docs/COMMENTING_STANDARD_RU_EN.md`.

## Политика комментариев в исходниках

- Изменения поведения проходят отдельный gate и фиксируются в документации.
- Platform-specific обходы сопровождаются назначением и границами применения.

## Компактный профиль Uno/Nano

Для Arduino AVR Uno/Nano на `__AVR_ATmega328P__` автоматически включается
`FLPROG_NETWORK_AVR_LITE`: оба публичных заголовка `flprogEthernet.h` и
`flprogNetwork.h` открывают компактный Wiznet API на стандартной Arduino
библиотеке Ethernet. Lite реализует один Wiznet интерфейс; legacy
`FLProgEthernetClient/Server`, DNS и прочие сетевые службы недоступны. Для
TCP/UDP используйте обычные классы `EthernetClient`, `EthernetServer` и
`EthernetUDP`, установив Arduino Ethernet 2.0.0 или совместимую 2.x версию.
DHCP выполняется синхронно при первом `pool()`; поддержание/повторная попытка
обслуживается последующими вызовами `pool()`. Чтобы сохранить полный API,
глобально задайте `FLPROG_NETWORK_AVR_LITE=0` в build flags (не в скетче).
На Mega, ESP и прочих целях поведение прежнее. Прямое подключение full-only
`flprogNetworkPlatform.h` выдаёт понятную ошибку сборки с указанием override.
