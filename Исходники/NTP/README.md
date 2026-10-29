# NTP TimeZones0.1 — исходники и воспроизведение

Реализация находится в `Библиотека/FLProg_Network/src/service/flprogNtpTimeZone.h`,
расширение сервиса — `flprogNetworkNtp.h`, обвязка блока — `src/flprogNtpUserBlocks.h`.
[Пользовательская инструкция](../../Документация/NTP_TIMEZONES_RU.md).

Из корня репозитория можно пересоздать UBI:

```powershell
python Исходники/NTP/build_ntp_blocks.py --output C:/Temp/NTP_Blocks
```

Нужен Python3 и соседние собственные сериализаторы из Исходники/MQTT и
Исходники/WebUI/tools. Рабочие блоки находятся в Блоки_FLProg/NTP.

## Проверка календаря

Нужен компиляторC++11 (Clang или Zig), Python3.9+ и база zoneinfo.
На Windows при отсутствии базы установите пакет tzdata.
Выберите отдельную папку для результатов вне репозитория:

```powershell
$env:NTP_TEST_OUTPUT='C:/Temp/NTP_Tests'
New-Item -ItemType Directory -Force $env:NTP_TEST_OUTPUT
clang++ -std=c++11 -O2 -UNDEBUG -I Библиотека/FLProg_Network/src/service Исходники/NTP/tests/timezone_peer.cpp -o "$env:NTP_TEST_OUTPUT/timezone_peer.exe"
python Исходники/NTP/tests/check_timezones.py
$env:NTP_CXX='clang++'
python Исходники/NTP/tests/check_blocks.py
```

Для Zig замените первую компиляцию на `zig c++ ...`, а NTP_CXX задайте полным
путём к zig.exe; check_blocks.py сам добавит подкоманду c++.

check_timezones.py сравнивает реальный C++ с независимым IANA zoneinfo для
современных повторяющихся правил, включая границы переходов. check_blocks.py
извлекает код из обоих UBI, проверяет эквивалентность и запускает его на нативных
заглушках сервиса/сети. tests/block_test.cpp отдельно проверяет кэш секунды,
фронты SYNC и отсутствие повторного сброса периода за2000сканов; собирается
с include-путями tests/stub, Библиотека/FLProg_Network/src и src/service.

Контрольный Arduino-скетч: Примеры/NTP_TimeZone_Gate. Сборка проверена для
FLE4D-30MT/F407, STM32 core3.0.0; логи в Проверки/NTP_TimeZones_v0.1.
Скетч не является готовой программой профиля и не прошивался на ПЛК.
Живой импорт UBI/аппаратный NTP-обмен пока не испытывались.
