# Типизированная проверка NET NUM — дополнение к ветке dev.20 + EIS 1.6.2

Дата: 2026-11-13. Статус: кандидат; реальная компиляция в FLProg и аппаратура ещё не проверены.

## Новые методы

```cpp
bool flprogNetworkDevices.existsWiznet(FLProgNetworkDeviceId netNum) const;
bool flprogNetworkDevices.existsWifi(FLProgNetworkDeviceId netNum) const;
```

- `true` возвращается только если номер зарегистрирован и класс объекта соответствует `FLProgWiznetInterface` или `FLProgOnBoardWifiInterface` соответственно.
- Для `255` (недопустимый ID), отсутствующего ID, базового/чужого объекта результат `false`.
- Это проверки **класса оболочки**, а не активного `networkMode()` или аппаратного маршрута: переключение режима не меняет результат.
- Как и существующий `exists()`, методы не меняют `lastResult()` и `lastId()`.
- Методы `getWiznet()` и `getWifi()` по-прежнему дают указатель либо `nullptr`; на ошибке типа `lastResult()=17`, на отсутствующем номере — `15`, на номере `255` — `10`.
- RTTI/dynamic_cast и дополнительная память не требуются.

Пример:

```cpp
#if defined(FLPROG_NETWORK_HAS_TYPED_DEVICE_EXISTS)
if (flprogNetworkDevices.existsWiznet(netNum)) {
    FLProgWiznetInterface* wiznet = flprogNetworkDevices.getWiznet(netNum);
    if (wiznet) wiznet->setSpeedSPI(20000000UL);
}
#endif
```

Регистрация выполняется отдельно через `registerDevice(netNum, device)` в `setup()`; устройство само номер не получает.

## Методы EIS

`setPinRST(uint8_t pin=255)` и `setSpeedSPI(uint32_t hz)` сохранены в `FLProgNetworkInterface` и наследуются Wiznet-оболочкой. RST `255` означает отсутствие назначенного пина. Конфигурацию RST выполняют до первого `pool()`; скорость зависит от стадии подготовки SPI.

## RMII

`FLProgRmiiEthernet` — **аппаратный backend**, не подкласс `FLProgNetworkInterface`; напрямую в реестре не регистрируется. У интерфейса доступен `rmiiHardware()`, режим определяется через `rmiiMode()`. Для проверки активной технологии передачи по номеру используйте `getDevice()` и проверяйте режим/транспорт, а не `existsWiznet()` (это проверка класса, и она может быть `true` у оболочки Wiznet с включённым RMII).

## Область проверки

GCC/Clang, C++11, -fno-rtti/-fno-exceptions, ASan/UBSan, существующий RT_HW SPI stub: PASS. Нужна компиляция STM32duino, ESP32 и аппаратное тестирование общих шин SPI, RST, DHCP, TCP/Modbus.
