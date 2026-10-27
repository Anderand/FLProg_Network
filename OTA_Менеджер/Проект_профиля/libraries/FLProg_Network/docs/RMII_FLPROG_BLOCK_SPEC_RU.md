# Задание для FLProg: блок «RMII / LAN8720 Ethernet»

## Назначение

Добавить штатный блок настройки встроенного Ethernet MAC по RMII для плат с поддерживаемым MAC (в первую очередь ESP32 и KinCony с LAN8720). Блок не заменяет W5500: RMII должен подключаться как ещё один интерфейс объекта сети и использовать общий HTTP-сервер библиотеки.

Блок не должен предполагать конкретную KinCony-плату. Все пины являются параметрами. Позже допустимо добавить отдельные пресеты плат.

## Размещение и имя

- Раздел палитры: `Сеть → Ethernet`.
- Отображаемое имя: `RMII / LAN8720 Ethernet`.
- Системное имя: `FLProgNetworkRmii`.
- Доступность: только для платформ, где библиотека сообщает поддержку RMII. На остальных платформах блок должен отображаться отключённым с пояснением «требуется встроенный Ethernet MAC/RMII».

## Входы и параметры

| Поле | Тип | Значение по умолчанию | Генерируемый вызов |
|---|---:|---:|---|
| В работе | BOOL-вход | `true` | `network.rmiiMode(value)` |
| DHCP | BOOL-параметр | `true` | `network.rmiiDhcpMode(value)` |
| IP-адрес | IP-параметр | `0.0.0.0` | `network.rmiiLocalIP(value)` |
| Маска подсети | IP-параметр | `255.255.255.0` | `network.rmiiSubnet(value)` |
| Шлюз | IP-параметр | `0.0.0.0` | `network.rmiiGateway(value)` |
| DNS 1 | IP-параметр | `0.0.0.0` | `network.rmiiDns(value)` |
| DNS 2 | IP-параметр | `0.0.0.0` | `network.rmiiDns2(value)` |
| Адрес PHY | INT | `0` | `network.setRmiiPhyAddress(value)` |
| MDC | pin | `23` | `network.setRmiiMdcPin(value)` |
| MDIO | pin | `18` | `network.setRmiiMdioPin(value)` |
| Питание PHY | pin / «не используется» | `-1` | `network.setRmiiPowerPin(value)` |
| Reset PHY | pin / «не используется» | `-1` | `network.setRmiiResetPin(value)` |
| Такт RMII | выпадающий список | `GPIO0 — внешний вход` | `network.setRmiiClockMode(value)` |
| Имя узла | STRING-параметр | пусто | `network.setRmiiHostname(value)` |

Список «Такт RMII»:

| Наименование | Значение |
|---|---:|
| GPIO0 — внешний вход 50 МГц | `FLPROG_RMII_CLOCK_GPIO0_IN` |
| GPIO0 — выход 50 МГц | `FLPROG_RMII_CLOCK_GPIO0_OUT` |
| GPIO16 — выход 50 МГц | `FLPROG_RMII_CLOCK_GPIO16_OUT` |
| GPIO17 — выход 50 МГц | `FLPROG_RMII_CLOCK_GPIO17_OUT` |

Правило UI: поля IP, маски, шлюза и DNS видны и сохраняются всегда, но при включённом DHCP должны быть помечены как резервные для статического режима.

## Выходы блока

| Выход | Тип | Генерируемое выражение |
|---|---|---|
| Готов | BOOL | `network.rmiiIsReady()` |
| Линк | BOOL | `network.rmiiLinkStatus() == 1` |
| IP-адрес | IP | `network.rmiiIP()` |
| Скорость, Мбит/с | UINT | `network.rmiiLinkSpeed()` |
| Полный дуплекс | BOOL | `network.rmiiFullDuplex()` |
| Ошибка | UINT | `network.error()` |

`rmiiLinkStatus()` возвращает: `0` — интерфейс не запущен, `1` — link up, `2` — link down. При необходимости можно вывести его отдельным числовым диагностическим выходом.

## Генерация кода

Для одного экземпляра сетевого устройства объект уже создаётся FLProg. Блок добавляет конфигурацию в Setup section **до первого вызова** `network.pool()`.

```cpp
network.setRmiiPhyAddress(RMII_PHY_ADDRESS);
network.setRmiiMdcPin(RMII_MDC_PIN);
network.setRmiiMdioPin(RMII_MDIO_PIN);
network.setRmiiPowerPin(RMII_POWER_PIN);
network.setRmiiResetPin(RMII_RESET_PIN);
network.setRmiiClockMode(RMII_CLOCK_MODE);
network.setRmiiHostname(RMII_HOSTNAME);
network.rmiiDhcpMode(RMII_DHCP);
network.rmiiLocalIP(RMII_IP);
network.rmiiSubnet(RMII_SUBNET);
network.rmiiGateway(RMII_GATEWAY);
network.rmiiDns(RMII_DNS1);
network.rmiiDns2(RMII_DNS2);
network.rmiiMode(RMII_ENABLED);
```

В Loop section никаких отдельных `begin()`, `ETH.begin()` или `delay()` генерировать не нужно. Достаточно уже штатного:

```cpp
network.pool();
```

Библиотека сама выполняет неблокирующий старт PHY, следит за линией и повторяет попытки подключения. Ручной вызов `ETH.begin()` из блока запрещён: он обойдёт общую транспортную архитектуру и может нарушить shared HTTP.

## Совместимость с WebServer

Блок WebServer должен использовать тот же объект `FLProgNetworkInterface`. Для выбора именно RMII-маршрута сервер вызывается через существующий API библиотеки с `FLPROG_NETWORK_ROUTE_RMII`. При стандартном автоматическом маршруте общий HTTP-сервер подключит RMII как доступный listener самостоятельно.

## Проверка после реализации блока

1. ESP32: сгенерировать проект только с блоком RMII, убедиться в успешной компиляции.
2. KinCony с LAN8720: DHCP, затем статический IP.
3. Проверить `Готов`, `Линк`, IP, скорость и duplex.
4. Открыть общую веб-страницу через RMII.
5. Вытащить и вернуть Ethernet-кабель: `Линк` должен смениться, веб на остальных интерфейсах не должен пострадать, RMII должен восстановиться.

## Граница текущего результата

RMII API и его связка с shared HTTP прошли ESP32 compile-gate. Аппаратный тест на KinCony/LAN8720 требуется отдельно; до него нельзя заявлять поддержку конкретного расположения пинов или PHY-профиля платы.
