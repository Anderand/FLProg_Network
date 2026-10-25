# MQTT runtime gate

## Цель

Подтвердить на реальном ESP8266 или ESP32, что `FLProgNetworkMqttClient`
работает поверх штатного `FLProgNetworkInterface` без прямого обращения к
WiFiClient/EthernetClient и без блокировки `loop()`.

## Пример

Используйте `examples/MQTT_Runtime_Gate_RU` или английский аналог. Внести
локальные SSID, пароль, IP/имя broker, порт и при необходимости credentials.
Не сохранять эти значения в библиотеке.

## Минимальный стенд

- MQTT 3.1.1 broker, доступный тестовой плате, обычно TCP `1883`.
- ПК с двумя клиентами broker или одним клиентом, который одновременно
  subscribe/publish.
- ESP8266/ESP32 в той же сети. Первую проверку проводить через Wi-Fi STA.

Пример для Mosquitto CLI:

```text
mosquitto_sub -h <broker> -t flprog/network/gate/out -v
mosquitto_pub -h <broker> -t flprog/network/gate/in -m test
```

## PASS

1. `connectSuccessCount() >= 1`, `connected() == true`, `error() == 0`.
2. Пример подписывается на `flprog/network/gate/in`.
3. Публикация `test` вызывает Serial `MQTT RX` и ответ `echo` на
   `flprog/network/gate/out`.
4. Каждые 15 секунд приходит `alive`.
5. После краткой потери broker или Wi-Fi client переходит в backoff и
   восстанавливает соединение/подписку без reset MCU.

## Фактический результат стенда

28.09.2026 gate пройден на ESP через Wi-Fi STA с локальным MQTT 3.1.1 broker
`192.168.100.7:1883`. Подтверждены `WiFiReady=1`, MQTT connection,
`connectSuccessCount()=1`, успешная подписка и loopback `self-test`:
`MQTT RX topic=flprog/network/gate/in payload=self-test`. После обработки
очереди `error()=0`, `messages=1`. Проверка reconnect после отключения сети,
TLS, W5500/RMII и soak остаётся за границами этого gate.

## FAIL и диагностика

Записать `state()`, `error()`, `connackCode()`, `tcpClientError()`,
`dnsError()`, `connectAttemptCount()`, `connectSuccessCount()`,
`reconnectScheduleCount()`, `protocolErrorCount()` и `oversizedPacketCount()`.
Не менять библиотеку, пока результат не отделён от DNS, broker credentials,
маршрутизации или прикладной MQTT семантики.

## Границы gate

Это native service gate, а не проверка будущего визуального блока FLProg.
QoS подписки в текущем baseline фиксирован на 0. TLS, W5500/RMII MQTT и
многоклиентский broker soak не объявляются PASS этим сценарием.
