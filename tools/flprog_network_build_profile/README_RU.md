# FLProg_Network profile hook для F985

`flprog_network_build_profile.py` запускается перед сборкой для ESP32 и ESP8266 и
сканирует исходники проекта, которые собрал генератор FLProg. Выбор основан на
используемых сетевых блоках, а не на имени проекта:

| Используемый код FLProg_Network | `FLPROG_NETWORK_BUILD_PROFILE` | `FLPROG_NETWORK_COMPILE_OTA` |
| --- | ---: | ---: |
| только Wi-Fi | 1 | 0, если нет блока OTA |
| только проводная сеть | 2 | 0, если нет блока OTA |
| Wi-Fi и проводная сеть | 0 | 0, если нет блока OTA |
| явный `FLProgNetworkOta` и вызов `begin(...)` | профиль по сетевым блокам | 1 |
| нет ссылок на FLProg_Network | 0 | 0 |

Профиль 0 остаётся безопасным значением для неоднозначных проектов. Анализ
просматривает `.ino`, `.cpp`, `.c`, `.h`, `.hpp`, `.hh`, `.cc`, `.cxx`, `.ipp`
во всём дереве скетча, поэтому объявление и вызов могут находиться в разных TU.
Распознаются также старые блоки `FLProgOTA` с вызовом `pool()` и блок
`FLProgOtaUniversalBlock` с вызовом `control(...)`. Явно типизированные
`FLProgOnBoardWifiInterface`/`FLProgWiznetInterface` или парное
`wiznetMode(true)` + `rmiiMode(false)` добавляют `FLPROG_NETWORK_COMPILE_RMII=0`;
неоднозначная динамическая конфигурация и явный RMII оставляют макрос
неопределённым, сохраняя библиотечную поддержку RMII.

Дополнительно `FLPROG_NETWORK_COMPILE_WIZNET_DHCP=0` создаётся только при
узком статическом доказательстве: все объявленные W5500/generic интерфейсы
полностью покрыты, в `setup()` без ветвлений явно вызывается
`dhcpMode(false)` либо legacy-алиас `resetDhcp()`, а конфигурация W5500 задана
до активации интерфейса. Любой `setDhcp()`, повторный/условный вызов,
неизвестный доступ к объекту, прямой `wiznetDhcpClient()` или неполное покрытие
оставляют DHCP-бэкенд включённым. Анализ намеренно консервативен и не пытается
выводить статичность из вспомогательных функций или alias-ов. Флаг влияет
только на Wiznet DHCP; DHCP Wi-Fi и RMII не отключается.

Анализ не учитывает комментарии, строки, а также вложенные `libraries`,
`examples`, `backup` и `backups`. Сканируются исходные файлы активного проекта,
включая его подпапки, чтобы объявления и вызовы в разных TU оставались одним
профилем. Переход от OTA-скетча к скетчу без блока OTA перезаписывает
конфигурацию сборки.

Хук создаёт в `build.path` `flprog_network_build_profile.h` и response-файл
`flprog_network_build_profile.rsp`. Preprocessor и рецепты компиляции C, C++ и
ассемблерных единиц подключают response-файл; он форсированно включает header.
Так выбор OTA виден при проверке зависимостей до линковки, и библиотека
`ArduinoOTA` не остаётся в списке из предыдущей сборки. Путь и заголовок
уникальны для каждой сборки, header виден компилятору как зависимость; при его
изменении hook очищает stale include/libraries cache и объектные файлы скетча и
библиотек, но сохраняет кэш ядра.

## Установка

Распакуйте ZIP. При обновлении перенесите прежнюю папку `FLProg_Network` за пределы `sketchbook/libraries`, затем скопируйте новую папку `FLProg_Network` целиком в `ideV8/portable/sketchbook/libraries`. Внутри неё должен находиться файл `library.properties`.

Откройте PowerShell в папке `FLProg_Network/tools/flprog_network_build_profile` установленной библиотеки (в репозитории это `tools/flprog_network_build_profile`). Запустите команды ниже, подставив свой путь к FLProg и версии пакетов. Для F985 проверены
ESP8266 3.1.2 и ESP32 3.3.11.

```powershell
python .\install_hook.py --platform-dir C:\f985\FLProg\ideV8\portable\packages\esp8266\hardware\esp8266\3.1.2
python .\install_hook.py --platform-dir C:\f985\FLProg\ideV8\portable\packages\esp32\hardware\esp32\3.3.11
```

После установки перезапустите Arduino IDE, если она открыта, и соберите проект из FLProg. Профиль определяется при каждой сборке. После обновления пакета платы повторите команду для нового каталога ядра.

Установщик сохраняет первый исходный `platform.txt` рядом как
`platform.txt.before-flprog-network-profile.bak`, копирует helper в `tools/` и
добавляет hook и response file к текущим recipe. Повторный запуск безопасен.
Для отката используйте `--uninstall`; он восстанавливает сохранённый исходный
`platform.txt` и удаляет установленный helper.

Настройки FQBN, flash layout, `platform.local.txt` и пользовательские build flags
не меняются. Для legacy Arduino IDE и Arduino CLI используется один и тот же
`platform.txt` и prebuild hook в соответствующем пакете ESP8266 или ESP32.

## Проверки

Локальные правила (включая меж-TU OTA, консервативное отключение RMII/Wiznet
DHCP и поведение response-файла) проверяются командой:

```powershell
python -m unittest discover -s .\tests -v
```
