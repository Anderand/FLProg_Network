# README RU

Исходники и воспроизведение сборки

Библиотека: ../Библиотека/FLProg_Network.
Web UI: WebUI/editor, WebUI/tools, WebUI/runtime, WebUI/integration.
Менеджер: hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER.
Сборщик и общий загрузчик: hardware_gates/STM32_OTA_PORTABILITY.
OTA-блок: hardware_gates/FLProg_OTA_Block_v0_4.

Проверки Web UI: Python 3.8, tools/verify_release.py и tools/test_audit_fixes.py.
Проверка блоков OTA: build_ota_block.py (генерация и контроль XML-ссылок).
FLE4D: Примеры/FLE4D_1.0.1/build.py, ядро STM32 3.0.0, профиль из
BOARD_PROFILE_APPEND.txt. Сборка работает со смещением 0x08010000.
Путь IDE в build.py по умолчанию C:\F-981\FLProg\ideV8.

Сборка менеджера:
1. Работайте с копией Исходники вне опубликованного выпуска.
2. Python 3.8 x64; PyInstaller 5.13.2. Создайте venv в
   hardware_gates/STM32_W5500_GATE/OTA_APP_FLE4D/build_env_win7.
3. Скопируйте OTA_Менеджер из готового архива в
   hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER/portable_v6.
4. Скопируйте OTA_Менеджер/build_tools/output в
   hardware_gates/STM32_OTA_PORTABILITY/output.
5. Запустите build_unified.bat. Существующие 20 BIN включаются в комплект;
   новый запуск компилятора выполняется отдельной кнопкой менеджера.

Сборка переносимого редактора PyInstaller:
--onedir --windowed --name FLProg_WebUI_Editor --hidden-import build_project_package
--paths <WebUI/tools>; точка входа <WebUI/editor/server.py>.
Добавить ресурсы public->public, tools->tools, integration->integration,
runtime->runtime и projects->projects через --add-data SOURCE;DEST.
Выход должен лежать в WebUI/editor/portable/FLProg_WebUI_Editor.
Для проверки без открытия браузера: FLProg_WebUI_Editor.exe 18766 --no-browser.

Изменения только в релизной копии:
- очищены Wi-Fi параметры двух примеров (YOUR_WIFI_SSID/YOUR_WIFI_PASSWORD);
- сервер редактора по умолчанию использует C:\F-981\FLProg\ideV8;
- добавлен fallback demo.flpui и обработка отсутствующего stderr в EXE;
- добавлен --no-browser для проверки запуска.

Архивы старых выпусков и пользовательские проекты не удалялись из
E:\FLP\Flprog_network. Прототип web_ui_designer 0.1 исключён как устаревший.
Сторонние RT_HW, Flprog_Utilites, Arduino IDE и toolchain не включены:
нужна установленная FLProg IDE с ними. См. CHECKS_RU.md для границ проверки.

## Расширенные инструкции

[Руководство разработчика](../Документация/РАЗРАБОТЧИКУ.md) · [Общий справочник](../Документация/README.md).
