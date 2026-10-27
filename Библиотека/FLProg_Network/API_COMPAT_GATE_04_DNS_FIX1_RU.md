# RC6-A dev.16-fix1 — DNS terminal-result latch

## Найденная проблема Gate 0.4.2

Native FLProgNetworkDns корректно получал DNS-ответ и переходил в SUCCESS.
Однако legacy FLProgDNSClient вызывал native resolve() раньше, чем считывал
терминальное состояние. Так как native cache для legacy-режима специально
отключён, resolve() немедленно запускал новый запрос и возвращал WAIT.

В результате SUCCESS постоянно терялся, а queryCount рос сотнями запросов.

## Исправление

Добавлен _activeHost — latch имени текущего legacy DNS-запроса.

Порядок getHostByName() теперь:
1. проверить legacy cache;
2. если native resolver завершил _activeHost — сначала снять SUCCESS/ERROR;
3. только если терминального результата нет, вызвать resolve();
4. при WAIT запомнить hostname как _activeHost;
5. при stop()/смене source очистить latch.

Native DNS/A3/UDP не изменялись.

## Повторный gate

Использовать без изменений:
API_COMPAT_GATE04_DNS_SEMANTIC_WIFI_ESP8266_COMMENTED.zip

Ожидаемый результат:
R1=1; R2=1; IP1==IP2; Q2==Q1; CACHE=1.
