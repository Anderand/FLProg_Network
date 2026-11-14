# Проверка релиза r18 — 14.11.2026

Финальный dev20/EIS объединён с main e68f94f. Реальная компиляция и линковка ESP8266 generic (core 3.1.2) и ESP32 ESP32S_DEV_EIS (core 3.3.11) завершились с кодом 0. Использован скетч [NetworkCompile](../../Библиотека/FLProg_Network/tests/compile/NetworkCompile/NetworkCompile.ino), Arduino Builder portable IDE, RT_HW 7.1.1 и Flprog_Utilites 1.0.0.

В [network_build.json](network_build.json) приведены параметры, память, хеши исходников и BIN/ELF. [network_setters.txt](network_setters.txt) содержит PASS для всех трёх профилей; стенд находится в [NETWORK_SETTERS](../NETWORK_SETTERS/README.md).

Редактор проверен командами `python tools/verify_release.py` и `python tools/test_runtime.py` из `Исходники/WebUI`: PASS. Готовый EXE ранее в этот же день собран из передаваемых исходников, запущен без браузера; проверены HTML, каталог сети, демопроект, предпросмотр и валидация. [Результаты EXE](editor/editor_smoke.json), [сборка](editor/editor_build.log), [переносимость проектов](editor/project_portability.json).

[assets.json](assets.json) содержит размеры и SHA-256 двух ZIP и двух sidecar-файлов. Каждый ZIP проверен по CRC и всем записям внутреннего MANIFEST_SHA256.json. Исходники редактора и WebUI в Git соответствуют Source/Libraries архива с учётом стандартной нормализации переводов строк Git.

Все проверки этого релиза выполнены без устройства. Контроллер не подключался и не прошивался; аппаратная работа W5500/RMII, DHCP/Modbus и электрические параметры RESET требуют отдельного испытания. Старые релизы и готовые BIN не заменялись.
