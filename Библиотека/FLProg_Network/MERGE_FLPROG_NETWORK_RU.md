# FLProg_Network — объединение dev.20 и EIS 1.6.2 с безопасным типизированным поиском

Дата: 2026-11-13. Статус: **КАНДИДАТ для компиляции и аппаратной проверки**, не подтверждён как официальная версия разработчика.

## Исходные ветки

1. Базовый эталон `libraries_исходный_эталон_2026-11-10.zip` из папки OneDrive `04_Библиотеки FLProg/04_Материалы` (локальная подтверждённая копия `/mnt/data/libraries.zip`). `FLProg_Network`: 145 файлов, `library.properties` = `1.0.0-rc.6a.dev.20-ntp-timezones`.
2. Присланный пользователем 2026-11-13 архив `FLProg_Network.zip`: 87 файлов, `library.properties` = `1.0.0-rc.6a.dev.17-pr28`. В журнале `0900_Развитие` описаны локальные изменения EIS от 2026-11-05, включая RT_HW SPI 1.6.2. Архив содержит только часть материалов последующей ветки dev.20.

Варианты **не являются последовательными полными релизами**. Простая замена dev.20 на присланный ZIP удалила бы 69 файлов и откатила бы более новые MQTT/NTP/HTTP/OTA. Поэтому использовано выборочное функциональное объединение; полный автоматический merge без конфликтов невозможен.

## Что интегрировано из ветки EIS

- `src/flprogEthernet.h`: расширенный фасад RT_HW + Wiznet и авторегистрация SPI backend на первом `pool()`, функции `ethBindRtHw`, `ethSetSpiSpeed`, `ethSetStartupDelay`, `ethSetReset`.
- Зависимость от RT_HW в `flprogEthernet.h` дополнительно закрыта проверкой наличия заголовка. Без RT_HW сохраняется путь Arduino SPI / Wi-Fi; прямой `#include "flprogUtilites.h"` восстановлен для совместимости.
- `src/hardware/flprogSpiBackend.h`: перенесён SPI backend EIS через готовые RT_HW-сессии. Ранее подтверждённые Arduino STM32 remap-улучшения в `flprogSpiBackend.cpp` сохранены.
- `src/hardware/flprogWiznetHardware.h/.cpp`: перенесены корректировки пассивного reset/startup, динамической SPI-частоты и ожидания шины.
- `src/flprogNetwork.h/.cpp`: перенесены `setPinRST`, `setSpeedSPI`, фабрика SPI backend, статус подготовки, защита ручного выбора SPI и подготовка перед первым `pool()`; сохранён новый API `dev.20` и его определения.
- Включены **11** новых файлов присланной ветки (журналы, совместимый redirect header, ранние пользовательские блоки); все **69** файлов, отсутствовавших в присланном архиве, сохранены из dev.20.
- Новые MQTT/NTP/HTTP/OTA/Service файлы из dev.20 **не заменялись** более ранними исходниками из ветки EIS.

## Дополнительный API FLProg — безопасный типизированный поиск

Используется реестр `flprogNetworkDevices`. Новый API включается при наличии `FLPROG_NETWORK_HAS_TYPED_DEVICE_LOOKUP` (отдельная метка функции). Старый `FLPROG_NETWORK_API_LEVEL 10006UL` оставлен без изменения.

```cpp
flprogNetworkDevices.registerDevice(1, WiznetInterface_18584770);
FLProgWiznetInterface* wiznet = flprogNetworkDevices.getWiznet(1);
if (wiznet != nullptr) {
    wiznet->setSpeedSPI(20000000UL);
}
```

```cpp
FLProgOnBoardWifiInterface* wifi = flprogNetworkDevices.getWifi(2);
if (wifi != nullptr) {
    wifi->setClientSsid("network");
}
```

`getDevice(id)` по-прежнему возвращает `FLProgNetworkInterface*`. Новые методы `getWiznet(id)` / `getWifi(id)` возвращают конкретный тип **только после проверки класса, в конструкторе помеченного неизменяемым идентификатором типа**. `networkMode()` и `activeInterface()` не используются для проверки класса и могут меняться во время работы. `dynamic_cast` и RTTI не требуются. Есть `const`-перегрузки.

При отсутствии устройства — **`nullptr`** (нулевой указатель; не числовой ID `255`).

- `idFor(&object)` при отсутствии регистрации — `FLPROG_NETWORK_DEVICE_INVALID` (`255`).
- `getDevice(незарегистрированный id)` — `nullptr` и `lastResult() == FLPROG_NETWORK_DEVICE_NOT_FOUND` (`15`).
- `getDevice(255)` — `nullptr` и `lastResult() == FLPROG_NETWORK_DEVICE_INVALID_ID` (`10`).
- `getWifi(id)` для зарегистрированного Wiznet или `getWiznet(id)` для Wi-Fi — `nullptr` и новый `FLPROG_NETWORK_DEVICE_TYPE_MISMATCH` (`17`).
- При успешном типизированном поиске `lastResult() == FLPROG_NETWORK_DEVICE_OK` (`0`).

Существующие числовые коды не менялись. Реестр не владеет сетевыми объектами, и их адреса должны оставаться действительными в течение регистрации.

## Проверки

- Контракт реестра и новые **реальные определения методов** из `flprogNetwork.h`: GCC/Clang C++11, `-fno-rtti -fno-exceptions`, ASan/UBSan: PASS.
- RT_HW SPI backend из итогового заголовка на имитаторе RT_HW-сессий: GCC/Clang C++11, без RTTI/exceptions: PASS.
- Исходный снимок RT_HW_00_BASE содержит необходимые `getETH_bus`, `getETH_cs`, `spiBeginSession`, `spiEndSession`, `spiLL_Transfer`, `spiGetBusy`.
- Полная Arduino/STM32/ESP32 компиляция, реальный W5500/Modbus TCP и работа нескольких устройств пока **НЕ ПРОВЕРЕНЫ**. Настоятельно рекомендуется проверить на STM32 + RT_HW с общим SPI и параллельным периферийным оборудованием.

## Важные ограничения

1. Изменения EIS добавляют стартовую выдержку Wiznet по умолчанию 500 мс. Отдельно проверить влияние на существующие скетчи, начальную готовность Ethernet и Modbus TCP.
2. RT_HW auto backend добавлен в `flprogEthernet.h` и регистрируется до `setup`, но создаётся только на первом `pool`; отдельно проверить сборку профилей без RT_HW, с Wi-Fi и с ручным Arduino SPI.
3. Из-за разветвления исходников изменения MQTT/HTTP/NTP/OTA из присланного более раннего dev.17 не переносились поверх новых реализаций dev.20. Перед официальным релизом обязательно просмотреть отдельный список конфликтных файлов и выполнить реальную регрессию.
4. Присланная ветка EIS не содержит полного набора документации dev.20; все отсутствовавшие файлы сохранены. Удаления файлов не делались.
5. Внутри `library.properties` оставлена upstream-версия dev.20. Имя ZIP содержит `candidate`; это НЕ утверждение об официальном выпуске или аппаратном PASS.

### Требования к пробному тесту в FLProg

- Собрать исходный STM32 + W5500 скетч с `#include "flprogEthernet.h"`, `setPinRST` и `setSpeedSPI`.
- Проверить `registerDevice(1, wiznet)` и `getWiznet(1)`; в чужом Wi-Fi NUM проверить `nullptr` + код 17.
- Проверить отсутствие NUM, смену сетевого режима, разные CS/SPI, активность общей шины, startup reset, DHCP и Modbus TCP.
- На ESP32 проверить `FLProgOnBoardWifiInterface` и `getWifi`, и что RT_HW-фасад не навязывает SPI.
- Никакой записи в оригинальные файлы OneDrive; кандидат сохраняется отдельно.


## Дополнение от 2026-11-13: типизированные предикаты

Добавлены `flprogNetworkDevices.existsWiznet(netNum)` и `existsWifi(netNum)`; контракт и различие RMII описаны в `docs/FLPROG_TYPED_DEVICE_EXISTS_RU_2026-11-13.md`. Методы `setPinRST` и `setSpeedSPI` EIS сохранены.
