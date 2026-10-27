# RC6-A dev.16-fix2 — DNS single-transaction guard

## Что показал Gate 0.4.2 после fix1

queryCount продолжал расти сотнями за секунду. Значит одной проверки terminal
SUCCESS/ERROR было недостаточно: legacy polling всё ещё мог повторно заходить
в native resolve() во время активной транзакции.

## Изменение fix2

Если `_activeHost` совпадает с запрошенным hostname:

1. SUCCESS — результат снимается и кладётся в legacy cache.
2. ERROR — ошибка переводится в legacy код.
3. BUSY — `resolve()` НЕ вызывается вообще; сразу возвращается FLPROG_WAIT.
4. IDLE без результата — latch снимается и разрешается новый чистый запрос.

Таким образом compatibility слой явно гарантирует:
`один legacy request = один native DNS transaction`.

Native FLProgNetworkDns, UDP, A3 и transport lifecycle не изменялись.
