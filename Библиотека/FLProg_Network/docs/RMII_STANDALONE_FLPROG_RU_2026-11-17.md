# FLProg_Network — самостоятельный RMII-интерфейс (кандидат)

## Задача

Добавлен публичный `FLProgRmiiInterface`, производный от `FLProgNetworkInterface`, для визуального блока FLProg. RMII не является SPI-Wiznet; вместо SPI-чипа используется аппаратный Ethernet MAC микроконтроллера и внешний PHY.

**Платформа:** поддержка фактического Ethernet MAC/PHY зависит от платы, Arduino core и настроек PHY. В библиотеке имеется `FLProgRmiiEthernet`. Это НЕ реализация универсального драйвера LAN8720 для любой STM32.

## Создание и регистрация

```cpp
#include "flprogEthernet.h" // включает flprogNetwork.h
FLProgRmiiInterface RmiiInterface_1;

void setup() {
    flprogNetworkDevices.registerDevice(3, RmiiInterface_1);
    RmiiInterface_1.setPhyAddress(0);
    RmiiInterface_1.setMdcPin(23);
    RmiiInterface_1.setMdioPin(18);
    RmiiInterface_1.setPowerPin(-1);
    RmiiInterface_1.setResetPin(-1);
    RmiiInterface_1.setClockMode(FLPROG_RMII_CLOCK_GPIO0_IN);
    RmiiInterface_1.setHostname("flprog-rmii");
    RmiiInterface_1.setDhcp();
}
void loop() { RmiiInterface_1.pool(); }
```

Другой способ создания: `FLProgRmiiInterface rmii(0, 23, 18);` — аргументы `phyAddress`, `mdcPin`, `mdioPin`.

`setResetPin` управляет линией RESET PHY. Это НЕ `setPinRST()` Wiznet, который применяется к SPI-чипу.

### IP

Для статического IP **через конкретный RMII-объект**, до первого `pool()`:

```cpp
RmiiInterface_1.resetDhcp();
RmiiInterface_1.localIP(192, 168, 1, 25);
RmiiInterface_1.gateway(192, 168, 1, 1);
RmiiInterface_1.subnet(255, 255, 255, 0);
RmiiInterface_1.dns(1, 1, 1, 1);
RmiiInterface_1.dns2(8, 8, 8, 8);
```

Методы `localIP`, `gateway`, `subnet`, `dns`, `dhcpMode`, `setDhcp`, `resetDhcp` существуют и в базовом классе, но в текущем API они **не виртуальные**. Для настройки PHY используйте `FLProgRmiiInterface&` / `FLProgRmiiInterface*`; типизированные методы нового класса одновременно обновляют базовые настройки и конфигурацию RMII-драйвера. Если вызвать одноимённый setter через `FLProgNetworkInterface*`, сработает базовая версия и передача настроек в RMII не гарантируется. Для универсального генератора лучше статически знать тип при конфигурации, а в сервис передавать базовый указатель только после настройки.

### Универсальная привязка сервисов

```cpp
FLProgNetworkInterface* net = flprogNetworkDevices.getDevice(3);
// Такой указатель подходит существующим TCP/UDP/HTTP/MQTT/NTP/Modbus/WebUI API,
// которые принимают FLProgNetworkInterface*.
```

Типизированный поиск:

```cpp
FLProgRmiiInterface* rmii = flprogNetworkDevices.getRmii(3);
bool present = flprogNetworkDevices.existsRmii(3);
```

`getRmii` возвращает `nullptr`, если ID отсутствует, недопустим или соответствует Wi-Fi/Wiznet/базовому объекту. `existsRmii` возвращает `false` и не изменяет `lastResult()`.

| Ситуация | `getRmii()` | `lastResult()` |
|---|---|---|
| RMII под ID | указатель | `FLPROG_NETWORK_DEVICE_OK = 0` |
| Wi-Fi/Wiznet под ID | `nullptr` | `TYPE_MISMATCH = 17` |
| ID не зарегистрирован | `nullptr` | `NOT_FOUND = 15` |
| ID = 255 | `nullptr` | `INVALID_ID = 10` |

Тип RMII: `FLPROG_NETWORK_DEVICE_KIND_RMII = 3`. Макросы доступности `FLPROG_NETWORK_HAS_RMII_INTERFACE` и `FLPROG_NETWORK_HAS_TYPED_DEVICE_RMII` имеют значение **1** в профиле с проводным backend, **0** в `WIFI_ONLY`; в Wi-Fi-only профиле `getRmii` предсказуемо возвращает `nullptr`, `existsRmii` — `false` и сам класс недоступен. Это не равнозначно аппаратной поддержке; отдельно проверяйте `rmii.supported()`.

### Аппаратная диагностика

- `supported()` — собрана ли поддержка на данной платформе;
- `phyReady()`, `phyLinkUp()`, `phyError()` — состояние PHY;
- `phyMacAddress()` — реально используемый MAC (возвращает стек ETH); стандартный унаследованный `mac(...)` не гарантирует изменение MAC встроенного PHY;
- `linkSpeedMbps()` и `fullDuplex()` — данные, если предоставляет core. На STM32 некоторые поля могут возвращать `0`/`false` при отсутствии API.

**Ограничения:** один физический Ethernet MAC обычно не допускает несколько одновременно активных RMII-интерфейсов на одном MCU. Компиляция на ESP8266/RP2040 не означает наличие аппаратной поддержки RMII; `supported()` будет `false`. Поддержка LAN8720 на STM32 зависит от PHY профиля варианта.

### Статус

Автономные проверки типизированного реестра и класса через mock-среду GCC/Clang с ASan/UBSan — PASS. **Сборка Arduino ESP32/STM32 и испытания физического RMII ещё не проведены.** Поддержка сервисов на реальной Ethernet сети не заявляется до аппаратных испытаний.

### Базовая ветка и официальный релиз

Кандидат основан на предоставленном архиве `FLProg_Network_dev20_final_2026-11-14.zip`. По сравнению с официальным GitHub `v2026.11.14-r18` исходники четырёх файлов отличаются: `src/flprogNetwork.cpp`, `src/flprogNetwork.h`, `src/hardware/flprogWiznetHardware.cpp/.h`. Поэтому данный полный ZIP **НЕ является заменой официального r18**: для релиза изменения нужно перенести на актуальный GitHub source и прогнать его сборку. Никакие исходные файлы пользователя или GitHub не перезаписаны.
