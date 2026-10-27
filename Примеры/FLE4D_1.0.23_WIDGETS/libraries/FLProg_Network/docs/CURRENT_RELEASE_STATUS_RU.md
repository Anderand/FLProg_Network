# Текущий релизный статус — dev.17-pr28

Дата: 27.09.2026. Это единственный документ текущего состояния; более ранние
roadmap, handoff и FIX33-отчёты остаются историей.

## Идентичность релиза

- Библиотека: `FLProg_Network`.
- Версия: `1.0.0-rc.6a.dev.17-pr28`.
- High-level API: `10006` (без изменения).
- Назначение: совместимый transport/network-manager слой для generated
  FLProg-проектов с Wi-Fi STA/AP, W5500 и RMII.

## Подтверждено

| Gate | Результат |
|---|---|
| ESP8266 PR26: HTTP | PASS: HTTP `200`, 4170 байт на Wi-Fi `.217` и W5500 `.218`/`.219`. |
| ESP8266 PR26: W5500 | PASS: paced TCP regression 10/10 на каждом W5500; единичный burst reject соответствует контракту одного HTTP context. |
| ESP8266 PR26: OTA | PASS: обнаружение, OTA upload и последующая HTTP/W5500 regression подтверждены. |
| ESP8266 память | 4008 байт free heap с включённым OTA; SoftAP исключён только из измерительной конфигурации PR26. |
| ESP MQTT runtime gate | PASS 28.09.2026: Wi-Fi STA, local broker, subscribe и loopback `self-test`; `connectSuccess=1`, `messages=1`, итоговый `error=0`. |
| ESP32 PR28 | Compile PASS: Flash 1 150 659 / 1 310 720 байт (87%), RAM 81 632 / 327 680 байт (24%). |
| RP2040 PR28 | Compile PASS: Flash 408 112 / 2 093 056 байт (19%), RAM 95 368 / 262 144 байт (36%). |

## Архитектурное решение

Legacy `FLProgOTA` сохраняет generated API без ручной правки `.ino`, но
делегирует работу `FLProgNetworkOta`. Вызовы `ArduinoOTA` находятся только в
service-слое. Фасад ожидает готовый Wi-Fi STA и только затем лениво
привязывается к соответствующему `FLProgNetworkInterface`; это корректно и
для проекта, где W5500 создаются раньше Wi-Fi.

## Ограничения, не являющиеся регрессией

- OTA доступна только через Wi-Fi STA; W5500/RMII OTA не реализована.
- Default shared HTTP context обслуживает один legacy-клиент последовательно.
  При burst возможен отказ соединения в окне переоткрытия W5500 LISTEN.
- Предупреждения generated `FLPROG_WEB_INTERFACE_SERVER` redefined и
  deprecated `BluetoothSerial` принадлежат генератору/Flprog_Utilites, не
  библиотеке сети.

## Следующий шаг

Релизный пакет можно считать закрытым. Новые изменения начинаются только с
отдельной задачи и собственного gate; обязательных незавершённых работ у
dev.17-pr28 нет.

## Документация исходников

28.09.2026: все 64 исходных файла `src/**/*.h` и `src/**/*.cpp`, а также оба
исполняемых примера получили расширенные комментарии на русском и английском.
Правило поддержки зафиксировано в `COMMENTING_STANDARD_RU_EN.md`. Это
documentation-only изменение: исполняемая логика и публичный API не менялись.
