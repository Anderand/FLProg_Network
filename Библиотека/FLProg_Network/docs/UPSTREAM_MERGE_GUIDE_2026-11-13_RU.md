# FLProg_Network — технический отчёт для разработчика и Codex

**Дата:** 13 ноября 2026 года  
**Цель:** перенести изменения из объединённой ветки в основную разработку без утраты новых функций и без изменения публичного API старых проектов.  
**Состояние:** кандидат, последняя пользовательская сборка **успешно скомпилировалась на Generic ESP8266 Module**, пользователь проверил вызовы добавленных методов. Полная аппаратная регрессия сетевых интерфейсов **не завершена**.

> **Задание для Codex / разработчика:** считать эталонным основанием `libraries_исходный_эталон_2026-11-10.zip → libraries/FLProg_Network` версии `1.0.0-rc.6a.dev.20-ntp-timezones`. Сравнить с поставляемым полным архивом этой версии, перенести **содержательные изменения** в актуальное upstream-дерево; не заменять дерево полностью и не откатывать новые MQTT/NTP/HTTP/OTA или пользовательские блоки.

## 1. От каких файлов считалась разница

1. **Эталон до изменений:** `libraries_исходный_эталон_2026-11-10.zip` (локальный `libraries.zip`), путь `libraries/FLProg_Network/`, **145 файлов**; `library.properties` = `1.0.0-rc.6a.dev.20-ntp-timezones`. Именно эта версия имеется в виду под «самой первой» библиотекой.
2. **Ветка партнёра EIS:** присланный `FLProg_Network.zip` (**87 файлов**, `library.properties` = `1.0.0-rc.6a.dev.17-pr28`); в `0900_Развитие` — история изменений 1.6/1.6.1/1.6.2 от 05.11.2026. Это **не полный преемник** dev.20: в ней нет части более поздних файлов.
3. **Итоговое дерево:** сохранена основа dev.20, выборочно перенесены настройки RT_HW/SPI/Wiznet из EIS, затем добавлены наши типизированные методы реестра, исправление ESP8266-OTA и актуализация `keywords.txt`.

**Принцип merge:** пофайловое сравнение и перенос по функциям; никогда не заменять все `src/service/*`, `src/protocol/*`, `src/socket/*` на соответствующие файлы из старой ветки EIS.

## 2. Сводка файлов (относительно первого эталона)

- **Удалённых файлов: 0**.
- **Изменённых существовавших файлов: 9**, из них 8 C++/заголовков и `keywords.txt`.
- **Добавлено новых файлов: 20** (включая импортированные материалы EIS, тесты и два документа текущего этапа).
- Список добавлений и контрольные суммы изменённых файлов приведены в разделе 8. Все пути относительно корня `FLProg_Network/`.
- `library.properties` не изменялся относительно первого эталона. Старое обозначение версии в `src/flprogNetwork.h` (`dev.17-pr28`) не унифицировано с `library.properties` (`dev.20`): перед официальным выпуском разработчику следует согласовать метки и журнал версий.

## 3. Изменения EIS: RT_HW / Wiznet / SPI

### 3.1 `src/flprogEthernet.h` (фасад, который включает старый генератор FLProg)

- Обнаружение наличия `<RT_HW_BASE.h>` через `__has_include` и `FLPROG_NETWORK_HAS_RT_HW_BASE`, чтобы сборки без RT_HW не зависели от его заголовков.
- Введён `FLPROG_NETWORK_RT_HW_AUTO` (по умолчанию `1`) для автопривязки RT_HW backend к Wiznet при первом `pool()`. Регистрация фабрики выполняется заранее, но создание backend и работа с шиной отложены до `pool()`.
- Перенесены фасадные функции: `ethBindRtHw(num, net, backend)`, `ethSetSpiSpeed(num, hz)`, `ethSetStartupDelay(num, ms)`, `ethSetReset(num, mode, pin, activeLevel, holdUs)` (последняя только при наличии RT_HW).
- Для времён жизни backend используется статический массив с placement-new (`FLPROG_NETWORK_MAX_DEVICES`), без `new/delete` в куче; **слоты не переиспользуются**. Не включать автоматическую регистрацию в нескольких единицах трансляции разными адресами фабрик без отдельного теста.
- `flprogRtHwEthernet.h` в итоговом архиве — совместимый redirect-header для старых точек подключения. `flprogUtilites.h` в `flprogEthernet.h` пока сохранён как зависимость совместимости.

### 3.2 `src/hardware/flprogSpiBackend.h`

- Обновлён шаблон `FLProgRtHwSpiBackend` для RT_HW; SPI должен открываться/закрываться штатными RT_HW-операциями `spiBeginSession()`, `spiEndSession()`, `spiLL_Transfer()`.
- Отдельная проверка занятости через `spiGetBusy()`, защита ошибочной шины и CS; собственные SPI lock/transaction не должны конфликтовать с RT_HW. Нельзя вручную дёргать CS поверх активной RT_HW-сессии.
- Сохранены старые виртуальные методы интерфейса `FLProgSpiBackend` и Arduino SPI backend; новое поведение реализовано внутри RT_HW backend.

### 3.3 `src/hardware/flprogWiznetHardware.h` / `.cpp`

- Добавлен контракт `FLProgEthernetResetMode`: `FLPROG_ETH_RESET_NONE=0`, `EXTERNAL=1`, `MANAGED=2` и writer `FLProgEthernetResetWriter`.
- Добавлены `setStartupDelayMs(uint32_t)`, `setSpiSpeedRuntime(uint32_t)`, `setResetMode(...)`, `startupState()`, `resetMode()`.
- Новый startup-state-machine для пассивной выдержки, необязательного аппаратного RESET, возможной ошибки GPIO. **Начальная выдержка 500 мс** — требует регрессии времени выхода сети в READY и запуска Modbus/TCP.
- Пин `255` означает отсутствие назначенного RESET, интерфейс Writer передаёт `uint8_t`; нельзя незаметно приводить произвольный `int` к байту (например 256 превратится в 0). Учитывать несовместимость между RESET и CS.
- Изменение SPI-частоты во время работы выполнено без полной переинициализации Wiznet там, где это позволяет новый API.

### 3.4 `src/flprogNetwork.h` / `.cpp`

- Новые методы верхнего интерфейса `FLProgNetworkInterface::setPinRST(uint8_t = 255)` и `setSpeedSPI(uint32_t)` — именно их генерирует FLProg 9.8.6.
- Параметры до запуска накапливаются в объекте. `prepareWiznetPool()` на первом `pool()` связывает backend и устанавливает скорость/RESET. Возвращаемые значения конфигурационных методов — `uint8_t`, `1` принято / `0` отказ.
- Доступна `setWiznetPoolFactory(...)`, состояние `poolConfigurationStatus()`, `pinRST()`.
- Новые RT_HW пути применяются только к выбранному SPI/Wiznet; Wi-Fi и RMII не должны требовать этой настройки. При явно выбранном Arduino/custom backend автозамена нежелательна.

## 4. Наши дополнения: типизированный реестр NET NUM

**Файлы:** `src/device/flprogNetworkDeviceRegistry.h`, `src/flprogNetwork.h`.

- При регистрации `FLProgOnBoardWifiInterface` получает фиксированный тип оболочки `FLPROG_NETWORK_DEVICE_KIND_WIFI=1`, `FLProgWiznetInterface` — `FLPROG_NETWORK_DEVICE_KIND_WIZNET=2` через конструктор. База `FLProgNetworkInterface` имеет `BASE=0`.
- Добавлены `getWiznet(id)`, `getWifi(id)` (включая `const`-варианты) с проверкой класса перед `static_cast` — без RTTI / `dynamic_cast`.
- Добавлены `existsWiznet(id)` и `existsWifi(id)`; проверка опирается на **тип C++-оболочки**, не на текущий `networkMode()` или `activeInterface()`. Они не меняют `lastResult()` / `lastId()`.
- Добавлены feature flags `FLPROG_NETWORK_HAS_TYPED_DEVICE_LOOKUP=1`, `FLPROG_NETWORK_HAS_TYPED_DEVICE_EXISTS=1`. `FLPROG_NETWORK_API_LEVEL=10006UL` не менялся.
- Новый код результата `FLPROG_NETWORK_DEVICE_TYPE_MISMATCH=17`, старые коды без изменений.

### Контракт отсутствия / несоответствия

| Выражение | Результат |
|---|---|
| `getDevice(id)` / `getWifi(id)` / `getWiznet(id)`, если ID отсутствует | `nullptr`, `lastResult() = NOT_FOUND (15)` |
| `getWifi(wiznetId)` или `getWiznet(wifiId)` | `nullptr`, `lastResult() = TYPE_MISMATCH (17)` |
| `getDevice(255)` и типизированные getter с ID `255` | `nullptr`, `lastResult() = INVALID_ID (10)` |
| `idFor(&object)` для незарегистрированного объекта | `FLPROG_NETWORK_DEVICE_INVALID = 255` |
| `exists(id)` / `existsWifi(id)` / `existsWiznet(id)` | `true`/`false`; диагностика `lastResult` не меняется |

`FLProgRmiiEthernet` — hardware/backend, не третий регистрируемый C++-класс. Если нужна отдельная диагностика RMII, она должна ориентироваться на режим/драйвер, не вводить фиктивный `getRmii()` в этот реестр.

### Примеры для генератора FLProg

```cpp
flprogNetworkDevices.registerDevice(1, WifiInterface_64270285);
flprogNetworkDevices.registerDevice(2, WiznetInterface_224409254);

if (flprogNetworkDevices.existsWiznet(2)) {
    FLProgWiznetInterface* net = flprogNetworkDevices.getWiznet(2);
    if (net != nullptr) {
        net->setPinRST(255);           // До первого pool()
        net->setSpeedSPI(20000000UL);
    }
}

FLProgOnBoardWifiInterface* wifi = flprogNetworkDevices.getWifi(1);
// Отсутствует или не того типа: nullptr, без неопределённого поведения
```

## 5. Исправление ESP8266: независимость заголовка OTA

**Файл:** `src/service/flprogNetworkOtaWiznet.h`.

- В класс OTA для Wiznet добавлено явное `#include <IPAddress.h>`.
- Причина: отдельно компилируемый `flprogNetworkOtaWiznet.cpp` не получает автоматически `#include` из скетча. На `Generic ESP8266 Module` наблюдалось `error: 'IPAddress' does not name a type`.
- Логику OTA, условия платформ, сетевой протокол и генерируемый скетч это исправление не меняет.
- После этого исправления **пользователь подтвердил успешную компиляцию на Generic ESP8266 Module**.

## 6. Актуализация `keywords.txt` — только подсветка редактора

- В первом эталоне было 440 строк ключевых слов, включая три дублирующих идентификатора и две строки с буквальным `\t`.
- Две строки исправлены, дубликаты убраны, добавлены **53** обозначения API и констант: итог **490 уникальных** корректных записей.
- Проверены все имена по исходникам, категории `KEYWORD1/KEYWORD2/LITERAL1`, реальные разделители TAB. Добавлен автономный тест `tests/check_keywords.py`.
- `keywords.txt` не влияет на C++-сборку и двоичный код. **По отношению к предыдущему пакету, который пользователь успешно скомпилировал, исполняемые `.h/.cpp` файлы не менялись.**
- Детали находятся в `docs/KEYWORDS_AUDIT_2026-11-13_RU.md`.

## 7. Что НЕ включено в изменения и что проверить до upstream-merge

- **Не переписаны** новые MQTT, NTP, HTTP, UDP, TCP, OTA/STM32, DNS и socket/backend dev.20 версиями старой ветки dev.17. Эти файлы оставлены побайтово, если нет целевого изменения выше.
- Не менялся оригинальный `library.properties`. При релизе устранить противоречие `version=...dev.20...` и `FLPROG_NETWORK_VERSION_STRING "...dev.17-pr28"` в `flprogNetwork.h` (не делать в рамках этого функционального merge без согласования релизной политики).
- Подтверждено пользователем: компиляция на **Generic ESP8266 Module** и проверка вызовов новых методов. Нельзя на этой основе утверждать, что собраны STM32/ESP32 или испытано оборудование W5500/RMII.
- Аппаратная регрессия: STM32 + RT_HW + W5500, общая SPI-шина с дисплеем и прочими устройствами, DHCP/Modbus TCP, RESET и startup delay 500 мс, Wi-Fi+Wiznet на ESP8266/ESP32, переключение режимов, многократная регистрация и конфликт NET NUM.
- Тесты на хосте (при наличии GCC и Clang): `python3 tests/check_typed_registry.py`, `python3 tests/check_rthw_spi.py`, `python3 tests/check_esp8266_wiznet_ota_header.py`, `python3 tests/check_keywords.py`. Они проходят, но используют тестовые Arduino-заглушки там, где нет платы.
- Файлы из ветки EIS, включающие `user_blocks/MQTT_User_Blocks_v0_1/`, носят исторический/экспериментальный характер; не подменять ими современные блоки `dev.20` без разбора API.
- Перед официальным выпуском уточнить лицензии и авторские уведомления сторонних компонентов; исходные `library.properties` и документы оставлены без правок на этом этапе.

## 8. Полная инвентаризация отличий относительно первого эталона

### Изменённые существовавшие файлы

Сокращённые SHA-256 (12 первых шестнадцатеричных символов) для удобства машинного сопоставления; считать их **идентификаторами сверки, а не криптографическим доказательством целого файла**. Статистика +/− приведена по строкам текстового diff, включая комментарии и пробелы.

| Относительный путь | Строки +/− | SHA-256 эталона (префикс) | SHA-256 результата (префикс) |
|---|---:|---|---|
| `keywords.txt` | +60/−4 | `5ddd15dcb430` | `b010f19ee741` |
| `src/device/flprogNetworkDeviceRegistry.h` | +27/−1 | `00c90d93e29a` | `06d28aa3eccc` |
| `src/flprogEthernet.h` | +138/−1 | `f6397f382300` | `858d16f20b67` |
| `src/flprogNetwork.cpp` | +78/−0 | `c3866a337ba4` | `d55822c8d6b5` |
| `src/flprogNetwork.h` | +117/−0 | `24d2be54b53d` | `5ca90e5d89ac` |
| `src/hardware/flprogSpiBackend.h` | +100/−127 | `d4ec1c9d9adb` | `7a75110840b4` |
| `src/hardware/flprogWiznetHardware.cpp` | +90/−0 | `9dd91f980e67` | `ec846c322b24` |
| `src/hardware/flprogWiznetHardware.h` | +44/−0 | `93e5ea11cb18` | `58f3b89431b8` |
| `src/service/flprogNetworkOtaWiznet.h` | +3/−0 | `1b2d2132e1f6` | `f2f519a30f78` |

### Новые файлы в конечном комплекте

- `0900_Развитие/0100_Развитие_Network.md`
- `0900_Развитие/0200_Изменения_20261105_1.6.md`
- `0900_Развитие/0300_Изменения_20261105_1.6.1.md`
- `0900_Развитие/0400_Изменения_20261105_1.6.2.md`
- `ESP8266_OTA_HEADER_FIX_20261113_RU.md`
- `MERGE_FLPROG_NETWORK_RU.md`
- `docs/FLPROG_TYPED_DEVICE_EXISTS_RU_2026-11-13.md`
- `src/flprogRtHwEthernet.h`
- `tests/check_esp8266_wiznet_ota_header.py`
- `tests/check_keywords.py`
- `tests/check_rthw_spi.py`
- `tests/check_typed_registry.py`
- `user_blocks/MQTT_User_Blocks_v0_1/FLProg_Network_MQTT_Core.ubi`
- `user_blocks/MQTT_User_Blocks_v0_1/FLProg_Network_MQTT_Publish.ubi`
- `user_blocks/MQTT_User_Blocks_v0_1/FLProg_Network_MQTT_Subscribe.ubi`
- `user_blocks/MQTT_User_Blocks_v0_1/README_EN.md`
- `user_blocks/MQTT_User_Blocks_v0_1/README_RU.md`
- `user_blocks/MQTT_User_Blocks_v0_1/flprogMqttUserBlocks.h`

### Удалённые файлы

Нет. Каталоги и документы первого эталона сохранены.

## 9. Рекомендуемая последовательность merge для Codex

1. Зафиксировать актуальное upstream-дерево и сравнить его с исходным `dev.20`, затем с этим полным архивом; **не делать checkout или overwrite всего каталога**.
2. Перенести блоки EIS RT_HW/SPI/RESET/стартовой выдержки с учётом текущих механизмов RT_HW и профилей `FLPROG_NETWORK_COMPILE_WIRED`/`FLPROG_NETWORK_PROFILE_WIFI_ONLY`.
3. Перенести device-kind и typed-getter/exists, не задействуя RTTI; проверить значения enum и неизменность старых кодов ошибок.
4. Перенести прямой include `IPAddress.h` для заголовка Wiznet OTA и тест сборки `ESP8266`.
5. Обновить `keywords.txt` по файлу из текущего архива; изменения подсветки можно принимать независимо от прошивочного кода.
6. Выполнить существующие автономные тесты, затем компиляцию ESP8266/ESP32/STM32 и аппаратные проверки. Только после этого повышать статус кандидата до релиза.
7. Документировать собственную релизную версию и происхождение изменений EIS/FLProg, не уничтожая исходный changelog.

**Конец отчёта.**
