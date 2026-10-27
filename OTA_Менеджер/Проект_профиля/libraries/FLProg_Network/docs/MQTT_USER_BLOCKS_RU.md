# MQTT: комплект пользовательских блоков FLProg

## Назначение и состав

Комплект строится поверх `FLProgNetworkMqttClient`, а не `PubSubClient` или
`AsyncMqttClient`. Поэтому MQTT использует тот же неблокирующий transport,
DNS, socket registry и `network.pool()`, что HTTP, NTP и OTA библиотеки.

В первой версии используются три блока. На контроллер допускается ровно один
экземпляр **MQTT Подключение** и произвольное число **MQTT Публикация** и
**MQTT Подписка**, связанных с ним внутри одного generated-проекта.

| Блок | Входы | Выходы |
|---|---|---|
| MQTT Подключение | `EN`, `Connect`, `Disconnect`, `Broker`, `Port`, `Client ID`, `User`, `Password` | `Connected`, `Busy`, `Error`, `Error code`, `State`, `Connect success`, `Messages received` |
| MQTT Публикация | `Send`, `Topic`, `Message`, `Retain` | `Accepted` |
| MQTT Подписка | `Subscribe`, `Topic` | `Accepted`, `Received`, `Received topic`, `Received message`, `Retained` |

`Send`, `Connect`, `Disconnect` и `Subscribe` являются фронтовыми командами:
длительная единица не создаёт поток повторных операций. `Accepted` означает,
что операция поставлена в очередь MQTT-клиента; QoS 0 не даёт отдельного
подтверждения доставки от broker.

## Автоматическая привязка к сети

Блок подключения использует `FLProgNetworkMqttBlockBridge`. Bridge ожидает
готовый Wi-Fi STA, автоматически находит соответствующий
`FLProgNetworkInterface` и лишь затем привязывает service. Пользователь не
вводит в блок C++-имя Wi-Fi-интерфейса, которое генератор FLProg меняет от
проекта к проекту. `network.pool()` остаётся обязательным и вызывается
обычным сетевым блоком проекта.

## WQTT.RU

Для WQTT указывать server, normal MQTT port, user и password из личного
кабинета. TLS port в версии первого комплекта не использовать: native MQTT
baseline — MQTT 3.1.1/QoS 0 по обычному TCP. Учётные данные хранить только в
локальном проекте FLProg, не в `.ubi`, примере или отчёте.

## Границы первого выпуска

- MQTT 3.1.1, publish/subscribe QoS 0;
- Wi-Fi STA; W5500/RMII и TLS будут отдельными hardware gates;
- Last Will, QoS 1/2, unsubscribe и несколько независимых MQTT clients не
  включаются до отдельного API и runtime теста.

## Проверка после импорта

1. Разместить сетевой Wi-Fi блок и один блок MQTT Подключение.
2. Настроить тестовый или WQTT broker и дождаться `Connected=1`.
3. Добавить MQTT Подписка на тестовый topic.
4. MQTT Публикация в этот же topic должна дать `Received=1` и исходный текст
   в `Received message`.
5. Отключить Wi-Fi, дождаться `Connected=0`, включить снова и проверить
   повторное подключение.
