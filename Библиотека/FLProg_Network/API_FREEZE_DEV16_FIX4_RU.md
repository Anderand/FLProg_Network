# API FREEZE DEV16 FIX4 RU

FLProg_Network RC6-A dev.16-fix4 — API FREEZE

Основа: RC6-A dev.16-fix3.

Изменения относительно dev.16-fix3:
1. Сетевая логика НЕ изменялась.
2. FLPROG_NETWORK_VERSION_DEV: 34 -> 16 (приведение метаданных к имени ветки).
3. FLPROG_NETWORK_VERSION_STRING:
   1.0.0-rc.6a.dev.14-fix2-legacy-server
   -> 1.0.0-rc.6a.dev.16-fix4-api-freeze
4. FLPROG_NETWORK_HIGH_LEVEL_API_FROZEN: 0 -> 1.
5. FLPROG_NETWORK_API_LEVEL остаётся 10006.
6. Обновлены только metadata в library.properties.

Основание для заморозки:
- Legacy DNS semantic/single-transaction: PASS
- Legacy TCP Client lifecycle: PASS
- Legacy UDP semantic: PASS
- Legacy TCP Server lifecycle Gate 0.5-fix1: PASS
- Legacy API Compile/Link Gate 0.6: PASS

Что означает API freeze:
- проверенные публичные legacy-классы, конструкторы и сигнатуры не менять без
  отдельного решения о новом API level;
- исправления внутренней реализации допускаются, если внешний контракт сохраняется;
- новые transport backend (W5500, RMII, optical) должны подключаться под этот
  внешний контракт, а не ломать его.

Следующий этап после контрольной пересборки: W5500.
После W5500: Wi-Fi AP, включая ESP8266/ESP32 и RP2040/RP2350 платы с Wi-Fi.
