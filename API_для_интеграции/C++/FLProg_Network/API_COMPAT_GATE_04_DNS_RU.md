# API Compatibility Gate 0.4 — FLProgDNSClient

Точка старта: RC6-A dev.15 COMMENTED, где Legacy UDP Gate 0.3 уже прошёл
compile/link, реальный Wi-Fi echo и server loss/return.

## Что добавлено

Тонкий legacy-адаптер `FLProgDNSClient` поверх `FLProgNetworkDns`.

Сохраняется старый публичный контракт:
- `setSourse()`;
- `getHostByName(host, uint8_t[4], timeout)`;
- `setDnsCacheStorageTime()` / `getDnsCacheStorageTime()`;
- `stop()`;
- legacy status/error/change flags.

## Что принципиально НЕ возвращено

- ручное формирование DNS packet из старой библиотеки;
- прямой socket index;
- старый UDP raw-socket backend.

Реальный путь остаётся:
`FLProgDNSClient -> FLProgNetworkDns -> FLProgNetworkUdp -> A3`.

## Legacy cache

Старый DNS держал один hostname/IP ровно заданное время в миллисекундах.
Native resolver учитывает DNS TTL, поэтому для adapter его internal cache отключён,
а старый one-entry cache воспроизведён отдельно. Это исключает скрытое изменение
поведения старых проектов.

## Retry/timeout

Старый код фактически делал initial attempt + три retry. Adapter задаёт native
resolver `attempts=4`, а `timeout` из `getHostByName()` применяется к каждой попытке.

## Gate 0.4.1

Первый тест — ESP8266 compile/link only. Сеть и реальный DNS запрос не запускаются.
После PASS будет отдельный semantic Wi-Fi DNS test, включая cache-hit.
