# FLProg_Network — исправление сборки ESP8266, 13.11.2026

## Симптом

При компиляции FLProg 9.8.6 для `Generic ESP8266 Module`:

```text
src/service/flprogNetworkOtaWiznet.h:57:5: error: 'IPAddress' does not name a type
```

Скетч подключает `flprogUtilites.h` и `flprogEthernet.h`, но заголовки скетча **не распространяются автоматически** на отдельно компилируемые `.cpp` файлы Arduino-библиотеки.

## Причина

`flprogNetworkOtaWiznet.h` использует поле типа `IPAddress`, полагаясь на транзитивное подключение из `Arduino.h` или более общего `flprogNetwork.h`. В ESP8266 это не гарантировано. При этом сервис Wiznet OTA для ESP32 отключён на ESP8266 условной компиляцией, но объявление поля в классе всё равно разбирается компилятором.

## Исправление

Только в `src/service/flprogNetworkOtaWiznet.h` добавлен прямой `#include <IPAddress.h>`. Сигнатуры, публичный API, протокол OTA, логика RT_HW/Wiznet/Wi-Fi и генерируемый скетч не изменялись.

## Контроль

- GCC и Clang, C++11, конфигурация `ESP8266`, отключены исключения и RTTI: PASS на минимальном Arduino-стабе, который **не объявляет** `IPAddress` сам.
- Повторная компиляция отдельного `flprogNetworkOtaWiznet.cpp`: PASS.
- Остальные заголовки с `IPAddress` проверены на наличие явного include; пропуск найден только в исправленном заголовке.
- Дополнительно запускаются автономные тесты типизированного реестра и RT_HW SPI.

**Ограничение:** это автономная проверка, не реальная сборка Arduino ESP8266 core. Необходимо проверить компиляцию в FLProg на `Generic ESP8266 Module` и затем на STM32/ESP32.
