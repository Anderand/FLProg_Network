# Ethernet OTA: RMII и W5500

В `FLProg_Network` доступны два Ethernet-пути обновления для ESP32. Они имеют
разную сетевую архитектуру и должны проверяться раздельно.

| Транспорт | API | Сетевой стек | Загрузка |
| --- | --- | --- | --- |
| Встроенный LAN8720/RMII | `FLProgNetworkOta` | ArduinoOTA + общий lwIP ESP32 core 3.x | Arduino IDE network port или `espota.py` |
| SPI W5500 | `FLProgNetworkOtaWiznet` | Управляемые UDP/TCP-сокеты `FLProg_Network` | `espota.py` по IP, порт UDP 3232 |

## W5500: подключение в скетче

```cpp
#include <flprogNetwork.h>

FLProgNetworkInterface network;
FLProgNetworkOtaWiznet ota;

void setup()
{
  network.networkMode(FLPROG_NETWORK_MODE_ETHERNET);
  network.wiznetMode(true);
  network.rmiiMode(false);
  network.setPinCs(5);             // заменить на реальные GPIO платы
  network.setSpiPins(18, 19, 23);  // SCK, MISO, MOSI; заменить при необходимости
  network.dhcpMode(true);
  network.workMode(true);
  network.connect();

  ota.begin(network, "отдельный-сложный-OTA-пароль", 3232);
}

void loop()
{
  network.pool(); // обслуживает сеть, сокеты и OTA
}
```

Перед OTA-прошивкой по воздуху сначала загрузите приложение USB. Таблица
разделов ESP32 должна содержать две OTA app-партиции. Адрес устройства берите
из `network.wiznetIP()`. Скомпилируйте целевой проект и выполните:

```powershell
python "<путь-к-esp32-core>\tools\espota.py" -i <IP_W5500> -p 3232 `
  -a "<OTA-пароль>" -f "<путь-к-скетчу.bin>"
```

W5500 service требует непустой пароль. Аутентификация совместима с ESP32 core
3.3.11 `espota.py` (SHA-256 + PBKDF2-HMAC-SHA256, 10 000 итераций); UDP
3232 принимает приглашение, после чего устройство устанавливает обратное TCP-
соединение с компьютером. Поэтому компьютер и контроллер должны быть доступны
друг другу по LAN, включая нужный TCP-порт Windows Firewall. W5500-путь не
публикует mDNS network port автоматически; используйте прямой IP и `espota.py`.

Пароль не шифрует сам firmware: передача не защищена TLS. Ограничивайте OTA
доверенной локальной сетью и не используйте пароль Wi-Fi. На ESP8266 эта
реализация W5500 OTA не поддерживается; встроенный Wi-Fi OTA остаётся отдельным
`FLProgNetworkOta` сервисом.

## Hardware gates

- RMII: `hardware_gates/KC868_A16_RMII_OTA_GATE` (KC868-A16, LAN8720).
- W5500: `hardware_gates/ESP32_W5500_OTA_GATE` (ESP32, SPI; настройки пинов
  в скетче должны соответствовать конкретной плате).
