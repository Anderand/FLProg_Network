# Архитектурный аудит PR26

Дата: 27.09.2026. Основание: handoff 22–24.09, roadmap 26.09, актуальная
установленная библиотека и аппаратные результаты PR22–PR28.

## Исходная цель и обязательные инварианты

Цель проекта не изменилась: один transport/network-manager слой для старых
сгенерированных FLProg-проектов и нового API, без ручной правки generated
`.ino`, с маршрутизацией через Wi-Fi STA/AP, W5500 и RMII.

Обязательные инварианты:

1. `route -> TransportIdentity -> generation -> socket/backend`; потеря
   транспорта закрывает и повторно открывает зависимые сокеты без reboot.
2. Один старый Web-проект не оплачивает крупный HTTP parser/context на каждый
   интерфейс.
3. Публичный high-level API остаётся совместимым (`API_LEVEL=10006`), а
   generated `.ino` не редактируется вручную.
4. Профили Wi-Fi/Wired существуют для исключения неиспользуемых transport
   backends; RAM/IRAM/Flash на ESP8266 являются архитектурным ограничением.
5. Platform-specific детали не должны выходить из transport/backend/service
   слоя в legacy-фасады.

## Соответствие фактической реализации

| Область | Оценка | Фактическое состояние |
|---|---|---|
| A3 transport/generation/socket | Соответствует | W5500 recovery, failover, STA/AP isolation и shared HTTP были подтверждены ранее. |
| Legacy Web без дублирования parser | Соответствует | Один context и shared listeners сохраняют ESP8266 RAM. PR26 честно фиксирует последовательную обработку. |
| Совместимость generated-кода | В целом соответствует | `flprogWebServer`, NTP и OTA фасады позволяют собирать старые проекты без правки `.ino`. |
| RAM-приоритет ESP8266 | Частично соответствует | Отказ от второго HTTP context верен; PR26 имеет 4008 байт free heap с OTA. IRAM-лимит и системная бюджетная политика не оформлены. |
| Сервисная граница | Соответствует принятому решению | HTTP, MQTT, NTP и OTA остаются в одной библиотеке ради совместимости generated-проектов; обещание отдельного пакета снято из архитектуры. |
| Legacy OTA | Соответствует | `FLProgOTA` — совместимый адаптер над `FLProgNetworkOta`; ESP8266 hardware-gate пройден. |
| Документы и версия | В процессе выравнивания | Актуальный статус вынесен в `CURRENT_RELEASE_STATUS_RU.md`; release identity синхронизирован как dev.17-pr28. |

## Зафиксированные расхождения и решения

### P0 — legacy OTA обходил network architecture — исправление ожидает hardware-gate

`src/flprogOTA.h` был добавлен, чтобы исправить отсутствующий include в
generated проекте. Фасад самостоятельно проверяет `WiFi.status()`, вызывает
`ArduinoOTA.begin()` и `ArduinoOTA.handle()`.

Это противоречит модели `FLProgNetworkOta`: service ownership, readiness,
network-loss/restart events, ограничение одного владельца и platform details
внутри service-слоя. Если в одном проекте появятся legacy `FLProgOTA` и
native `FLProgNetworkOta`, возможны конфликт владельцев singleton ArduinoOTA,
разная реакция на recovery и недиагностируемое двойное обслуживание.

**Исправление в рабочей библиотеке:** `FLProgOTA` теперь наследует
`FLProgNetworkOta`, сохраняя generated API без изменений. При первом `pool()`
он ожидает готовый Wi-Fi STA и привязывается к нему через внутренний список
живых `FLProgNetworkInterface`. `ArduinoOTA` остался только внутри
`service/flprogNetworkOta.cpp`; второй state machine удалён.

Это сохраняет ownership, обработку потери/восстановления сети, события и
счётчики service-слоя. Выбор именно ready STA обязателен для PR28: W5500
объекты создаются раньше Wi-Fi объекта. До отдельной проверки на ESP8266
статус исправления — **PASS: OTA upload и HTTP/W5500 regression подтверждены
пользователем на ESP8266**.

### P1 — граница сервисов зафиксирована

Ранняя схема обещала отдельную `FLProg_Network_Services`, тогда как
`flprogNetwork.h` экспортирует HTTP client/server, MQTT, NTP и OTA. Решение
принято: сервисы остаются в одной библиотеке. Это сохраняет совместимость
старых generated-проектов и не создаёт вторую матрицу профилей без
практической потребности. Обещание отдельной библиотеки удалено из
`ARCHITECTURE_RU/EN.md`.

### P1 — HTTP burst ограничение должно быть контрактом, а не скрытым дефектом

Один context — правильное следствие RAM-цели. На W5500 при `maxClients=1`
между закрытием соединения и переоткрытием LISTEN socket возможен TCP reject
следующего burst-запроса. Это не регресс нормального браузерного сценария,
но не эквивалентно многоклиентному HTTP server.

**Решение:** оставить default=1 на ESP8266; документировать это в API и
добавить диагностический счётчик/событие reject. Режим 2+ contexts разрешать
только явным opt-in после RAM/soak gate, не как скрытое изменение default.

### P2 — документация и release identity расходятся с рабочей веткой

- `STATUS_RU.md` уже PR26, но roadmap ещё заканчивается состоянием 26.09 и
  назначает следующий compile gate, хотя ESP32 и RP2040 уже собраны.
- `ARCHITECTURE_SHARED_HTTP_RU.md` правильно описывает AP, но PR26 без AP;
  это должна быть отмеченная test configuration, а не замена архитектуры.
- `FLPROG_NETWORK_VERSION_STRING` содержит `fix17`,
  `library.properties` — `fix33`; это не может быть идентификатором PR26.
- historical compact HTTP document сохранён правильно как снятый, но
  generator всё ещё генерирует устаревший define.

**Решение:** ввести один `CURRENT_RELEASE_STATUS_RU.md` как единственный
источник текущего статуса, обновлять roadmap только ссылкой на gate reports,
а version/property менять только при выпускном snapshot, не после каждого
аппаратного PR.

### P2 — generated warnings не должны диктовать библиотечную архитектуру

Повторный `#define FLPROG_WEB_INTERFACE_SERVER` создаёт генератор при трёх
WebServer. Библиотека уже использует object-based legacy merge и не должна
опираться на последнее значение этого macro. Предупреждение не является
library defect, но должно быть зарегистрировано у генератора FLProg.

## Что не является уходом от концепции

- Удаление compact HTTP profile: верное решение после нестабильности; память
  сохраняется архитектурно через один HTTP context, а не хрупкими лимитами.
- Отказ PR26 от SoftAP: это измерительная конфигурация для 4008 байт free
  heap, а не удаление AP transport. AP API и ранее подтверждённые AP gates
  остаются в библиотеке.
- Wi-Fi-only OTA: допустимое ограничение текущего service scope. OTA через
  W5500/RMII не нужно симулировать или объявлять готовым до отдельного
  transport design gate.
- Добавление `timeServer(const char *)`: additive compatibility fix, не
  ломает API freeze.

## Рекомендуемая последовательность возврата к строгой архитектуре

1. P0 legacy OTA adapter и его ESP8266 regression gate — закрыты.
2. Граница сервисов зафиксирована: одна библиотека, без отдельного service
   package и без обязательного feature-flag этапа.
3. HTTP single-context contract остаётся ограничением релиза; расширение
   допускается только отдельной задачей с RAM/soak gate.
4. Документация и release identity синхронизированы в dev.17-pr28.

## Вывод

Базовая концепция сохранена и доказана аппаратно: A3 transport model,
multi-W5500, shared HTTP и OTA service adapter решают исходную задачу.
Обязательных архитектурных долгов, блокирующих dev.17-pr28, не осталось.
