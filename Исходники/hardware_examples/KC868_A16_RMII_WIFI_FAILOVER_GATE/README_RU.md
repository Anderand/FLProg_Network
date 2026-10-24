# KC868-A16: RMII + Wi-Fi STA hardware gate

Минимальный испытательный скетч для KinCony KC868-A16. Он проверяет одновременную работу встроенного LAN8720/RMII и Wi-Fi STA средствами публичного API `FLProg_Network`.

## Что делает

- LAN8720/RMII: PHY `0`, MDC `GPIO23`, MDIO `GPIO18`, clock `GPIO17 OUT`, DHCP;
- Wi-Fi STA: подключается к заданной сети, DHCP;
- запускает один HTTP-сервер на порту `80` с первичным маршрутом RMII и общим слушателем Wi-Fi;
- одинаковая страница доступна по IP RMII и по IP Wi-Fi;
- HTTP: `/` — компактная диагностика, `/api/status` — JSON;
- SoftAP, OTA, TCP/UDP echo и Bluetooth не включаются.

Пароль Wi-Fi находится только в исходнике `.ino`; он не печатается через Serial и не возвращается HTTP API.

## Прошивка и проверка

1. Откройте `KC868_A16_RMII_WIFI_FAILOVER_GATE.ino` в Arduino IDE/FLProg.
2. Выберите плату **FLPrpog: ESP32S-Dev-Module** (как в пройденном RMII gate) и прошейте.
3. Откройте монитор порта `115200`.
4. Дождитесь строки вида:

   ```text
   RMII ready=1 link=1 ip=<RMII_IP> | WiFi ready=1 ip=<WIFI_IP> | both=1 http=1 shared=1 error=0
   ```

5. Откройте в браузере `http://<RMII_IP>/`, затем `http://<WIFI_IP>/`.
6. Для проверки независимости маршрутов временно отключите кабель Ethernet: Wi-Fi страница должна оставаться доступна; подключите кабель обратно и убедитесь, что RMII снова доступен.

## Память

Здесь намеренно выбран универсальный профиль `FLPROG_NETWORK_BUILD_PROFILE=0`: Wi-Fi и RMII компилируются одновременно. В `build_opt.h` отключён неиспользуемый Bluetooth, чтобы не тратить память на него. Сравнивать размер следует с RMII TCP/UDP gate только с учётом того, что данный скетч содержит полный Wi-Fi стек.
