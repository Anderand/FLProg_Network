# Optical Architecture Gate — заглушка до оборудования

## Что добавлено

- Зарезервирован transport kind `FLPROG_TRANSPORT_KIND_OPTICAL` (`7`).
- Добавлен публичный inert-класс `FLProgNetworkOpticalStub`.
- Включение по умолчанию выключено: `FLPROG_NETWORK_ENABLE_OPTICAL_STUB=0`.
- Класс хранит только будущие настройки режима и MTU; не создаёт route, socket, task, SPI-обмена и не вызывает драйверы.

## Границы текущего этапа

`available()`, `ready()` и `supported()` всегда возвращают `false`. Это намеренно: заглушка не выдаёт себя за рабочую оптику и не меняет поведение Wi-Fi, W5500 либо RMII.

## Решение при появлении оборудования

До подключения железа нужно выбрать один вариант:

1. Оптика как прозрачный Ethernet-канал через PHY/медиаконвертер: реализовать backend как Ethernet transport, проверить link, DHCP/static IP, TCP/UDP и recovery.
2. Собственный пакетный оптический канал: до реализации согласовать framing, MTU, адресацию, контроль ошибок, повтор передачи и совместимость с TCP/IP.

После выбора backend получает identity `OPTICAL + instanceId`; только тогда его можно зарегистрировать в transport manager и открыть для route/socket API.
