# Каналы для FLProg: FLE4D-30MT

ID проекта: `FLE4D-30MT`. Транспорт: `w5500-http-1`.

Это схема подключения из макета. Она не подтверждает, что блоки уже добавлены в .flp.

## Запуск

Один профессиональный блок **Web UI Start**, параметр **ID проекта**: `FLE4D-30MT`.
В скетче: `#include <FLE4D-30MT_webui.h>` и `FLPROG_WEBUI_BEGIN_SELECTED();` после настройки сети.
SPI и Ethernet задаются в проекте FLProg. Для сетевого обновления отдельно нужен OTA-блок.

## Системные каналы №0–100

Заполняются библиотеками автоматически. Publish/Command для них не нужны.

| CHANNEL | ID / название | Тип | Направление | Блоки FLProg | Виджеты и роли |
|---|---|---|---|---|---|
| 0 | network_ip / IP-адрес | text | ПЛК → веб | Автоматически | Диагностика / IP-адрес (network_diag_ip, значение) |
| 1 | network_ready / Сеть подключена | bool | ПЛК → веб | Автоматически | Диагностика / Сеть подключена (network_diag_ready, значение) |
| 2 | network_mac / MAC-адрес | text | ПЛК → веб | Автоматически | Диагностика / MAC-адрес (network_diag_mac, значение) |
| 3 | network_gateway / Шлюз | text | ПЛК → веб | Автоматически | Диагностика / Шлюз (network_diag_gateway, значение) |
| 4 | network_subnet / Маска подсети | text | ПЛК → веб | Автоматически | Диагностика / Маска подсети (network_diag_subnet, значение) |
| 5 | device_model / Модель контроллера | text | ПЛК → веб | Автоматически | Диагностика / Модель контроллера (network_diag_model, значение) |
| 6 | firmware_version / Версия прошивки | text | ПЛК → веб | Автоматически | Диагностика / Версия прошивки (network_diag_version, значение) |
| 7 | reset_flags / Маска сброса (накопленная) | text | ПЛК → веб | Автоматически | Диагностика / Маска сброса (накопленная) (network_diag_flags, значение) |
| 8 | reset_cause / Расшифровка флагов сброса | text | ПЛК → веб | Автоматически | Диагностика / Расшифровка флагов сброса (network_diag_reset, значение) |
| 9 | heap_used / ОЗУ: динамически занято, байт | text | ПЛК → веб | Автоматически | Диагностика / ОЗУ: динамически занято, байт (network_diag_heap_used, значение) |
| 10 | heap_arena_free / ОЗУ: свободные блоки в выделенном пуле, байт | text | ПЛК → веб | Автоматически | Диагностика / ОЗУ: свободные блоки в выделенном пуле, байт (network_diag_heap_free, значение) |
| 11 | flash_total / Flash контроллера: всего, байт | text | ПЛК → веб | Автоматически | Диагностика / Flash контроллера: всего, байт (system_flash_total, значение) |
| 12 | flash_app_capacity / Flash: доступно приложению, байт | text | ПЛК → веб | Автоматически | Диагностика / Flash: доступно приложению, байт (system_flash_app_capacity, значение) |
| 13 | flash_app_used / Flash: размер приложения, байт | text | ПЛК → веб | Автоматически | Диагностика / Flash: размер приложения, байт (system_flash_app_used, значение) |
| 14 | flash_app_free / Flash: свободно для приложения, байт | text | ПЛК → веб | Автоматически | Диагностика / Flash: свободно для приложения, байт (system_flash_app_free, значение) |
| 15 | ram_total / ОЗУ контроллера: всего, байт | text | ПЛК → веб | Автоматически | Диагностика / ОЗУ контроллера: всего, байт (system_ram_total, значение) |
| 16 | ram_app_capacity / ОЗУ: доступно приложению, байт | text | ПЛК → веб | Автоматически | Диагностика / ОЗУ: доступно приложению, байт (system_ram_app_capacity, значение) |
| 17 | ram_static_used / ОЗУ: переменные программы, байт | text | ПЛК → веб | Автоматически | Диагностика / ОЗУ: переменные программы, байт (system_ram_static_used, значение) |
| 18 | ram_available_estimate / ОЗУ: доступно для выделений (оценка), байт | text | ПЛК → веб | Автоматически | Диагностика / ОЗУ: доступно для выделений (оценка), байт (system_ram_available_estimate, значение) |
| 19 | ram_used_estimate / ОЗУ: занято и зарезервировано (оценка), байт | text | ПЛК → веб | Автоматически | Диагностика / ОЗУ: занято и зарезервировано (оценка), байт (system_ram_used_estimate, значение) |
| 20 | ccm_total / Дополнительная ОЗУ CCM: всего, байт | text | ПЛК → веб | Автоматически | Диагностика / Дополнительная ОЗУ CCM: всего, байт (system_ccm_total, значение) |
| 21 | ccm_used / Дополнительная ОЗУ CCM: занято, байт | text | ПЛК → веб | Автоматически | Диагностика / Дополнительная ОЗУ CCM: занято, байт (system_ccm_used, значение) |
| 22 | system_uptime / Время работы после запуска, с | int32 | ПЛК → веб | Автоматически | Диагностика / Время работы после запуска (system_uptime_value, значение) |
| 29 | console_ready / Консоль готова · UART6 | bool | ПЛК → веб | Автоматически | Главная / Консоль готова · UART6 (view_console_ready, значение) |
| 31 | console_core / Ядро · RT_HW | text | ПЛК → веб | Автоматически | Главная / Ядро · RT_HW (view_console_core, значение) |
| 32 | console_arch / Архитектура · RT_HW | text | ПЛК → веб | Автоматически | Главная / Архитектура · RT_HW (view_console_arch, значение) |
| 33 | console_core_version / Версия ядра · RT_HW | text | ПЛК → веб | Автоматически | Главная / Версия ядра · RT_HW (view_console_core_version, значение) |
| 34 | console_cpu_mhz / Частота CPU, МГц | int32 | ПЛК → веб | Автоматически | Главная / Частота CPU, МГц (view_console_cpu_mhz, значение) |
| 35 | console_vcc_mv / Питание Vcc, мВ | int32 | ПЛК → веб | Автоматически | Главная / Питание Vcc, мВ (view_console_vcc_mv, значение) |
| 37 | console_board_id / ID платы · RT_HW | text | ПЛК → веб | Автоматически | Главная / ID платы · RT_HW (view_console_board_id, значение) |
| 38 | console_base_version / Версия RT_HW_BASE | text | ПЛК → веб | Автоматически | Главная / Версия RT_HW_BASE (view_console_base_version, значение) |
| 39 | console_library_version / Версия RT_HW_CONSOLE | text | ПЛК → веб | Автоматически | Главная / Версия RT_HW_CONSOLE (view_console_library_version, значение) |
| 40 | console_loop_speed / Скорость цикла, циклов/с | int32 | ПЛК → веб | Автоматически | Главная / Скорость цикла, циклов/с (view_console_loop_speed, значение) |
| 41 | console_scheduler / Размеры групп диспетчера | text | ПЛК → веб | Автоматически | Главная / Размеры групп диспетчера (view_console_scheduler, значение) |
| 42 | web_control_ready / Веб-управление разрешено | bool | ПЛК → веб | Автоматически | Выходы / DO1 · PA0 (view_do_01, разрешение); Выходы / DO2 · PA1 (view_do_02, разрешение); Выходы / DO3 · PA2 (view_do_03, разрешение); Выходы / DO4 · PA3 (view_do_04, разрешение); Выходы / DO5 · PA6 (view_do_05, разрешение); Выходы / DO6 · PA7 (view_do_06, разрешение); Выходы / DO7 · PA8 (view_do_07, разрешение); Выходы / DO8 · PA11 (view_do_08, разрешение); Выходы / DO9 · PB0 (view_do_09, разрешение); Выходы / DO10 · PB1 (view_do_10, разрешение); Выходы / DO11 · PE5 (view_do_11, разрешение); Выходы / DO12 · PE6 (view_do_12, разрешение); Выходы / DO13 · PE7 (view_do_13, разрешение); Выходы / DO14 · PE8 (view_do_14, разрешение); Выходы / AO0 · PA4 (view_ao_0, разрешение); Выходы / AO1 · PA5 (view_ao_1, разрешение) |
| 43 | output_source / Источник управления выходами | text | ПЛК → веб | Автоматически | Выходы / Текущий источник (output_source_view, значение) |

## Пользовательские каналы №101–255

Номер из столбца CHANNEL задаётся на одноимённом входе универсального блока.

| CHANNEL | ID / название | Тип | Направление | Блоки FLProg | Виджеты и роли |
|---|---|---|---|---|---|
| 101 | di_01 / DI1 · PD3 | bool | ПЛК → веб | Publish Bool | Входы / DI1 · PD3 (view_di_01, значение) |
| 102 | di_02 / DI2 · PD4 | bool | ПЛК → веб | Publish Bool | Входы / DI2 · PD4 (view_di_02, значение) |
| 103 | di_03 / DI3 · PD7 | bool | ПЛК → веб | Publish Bool | Входы / DI3 · PD7 (view_di_03, значение) |
| 104 | di_04 / DI4 · PD10 | bool | ПЛК → веб | Publish Bool | Входы / DI4 · PD10 (view_di_04, значение) |
| 105 | di_05 / DI5 · PD11 | bool | ПЛК → веб | Publish Bool | Входы / DI5 · PD11 (view_di_05, значение) |
| 106 | di_06 / DI6 · PD12 | bool | ПЛК → веб | Publish Bool | Входы / DI6 · PD12 (view_di_06, значение) |
| 107 | di_07 / DI7 · PD13 | bool | ПЛК → веб | Publish Bool | Входы / DI7 · PD13 (view_di_07, значение) |
| 108 | di_08 / DI8 · PD14 | bool | ПЛК → веб | Publish Bool | Входы / DI8 · PD14 (view_di_08, значение) |
| 109 | di_09 / DI9 · PC8 | bool | ПЛК → веб | Publish Bool | Входы / DI9 · PC8 (view_di_09, значение) |
| 110 | di_10 / DI10 · PC9 | bool | ПЛК → веб | Publish Bool | Входы / DI10 · PC9 (view_di_10, значение) |
| 111 | di_11 / DI11 · PC13 | bool | ПЛК → веб | Publish Bool | Входы / DI11 · PC13 (view_di_11, значение) |
| 112 | di_12 / DI12 · PE0 | bool | ПЛК → веб | Publish Bool | Входы / DI12 · PE0 (view_di_12, значение) |
| 113 | di_13 / DI13 · PE1 | bool | ПЛК → веб | Publish Bool | Входы / DI13 · PE1 (view_di_13, значение) |
| 114 | di_14 / DI14 · PE2 | bool | ПЛК → веб | Publish Bool | Входы / DI14 · PE2 (view_di_14, значение) |
| 115 | di_15 / DI15 · PE3 | bool | ПЛК → веб | Publish Bool | Входы / DI15 · PE3 (view_di_15, значение) |
| 116 | di_16 / DI16 · PE4 | bool | ПЛК → веб | Publish Bool | Входы / DI16 · PE4 (view_di_16, значение) |
| 117 | ai_0 / AI0 · ADS1115 | int32 | ПЛК → веб | Publish Int | Входы / AI0 · ADS1115 (view_ai_0, значение) |
| 118 | ai_1 / AI1 · ADS1115 | int32 | ПЛК → веб | Publish Int | Входы / AI1 · ADS1115 (view_ai_1, значение) |
| 119 | ai_2 / AI2 · ADS1115 | int32 | ПЛК → веб | Publish Int | Входы / AI2 · ADS1115 (view_ai_2, значение) |
| 120 | ai_3 / AI3 · ADS1115 | int32 | ПЛК → веб | Publish Int | Входы / AI3 · ADS1115 (view_ai_3, значение) |
| 121 | do_01 / DO1 · PA0 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO1 · PA0 (view_do_01, значение) |
| 122 | do_02 / DO2 · PA1 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO2 · PA1 (view_do_02, значение) |
| 123 | do_03 / DO3 · PA2 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO3 · PA2 (view_do_03, значение) |
| 124 | do_04 / DO4 · PA3 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO4 · PA3 (view_do_04, значение) |
| 125 | do_05 / DO5 · PA6 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO5 · PA6 (view_do_05, значение) |
| 126 | do_06 / DO6 · PA7 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO6 · PA7 (view_do_06, значение) |
| 127 | do_07 / DO7 · PA8 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO7 · PA8 (view_do_07, значение) |
| 128 | do_08 / DO8 · PA11 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO8 · PA11 (view_do_08, значение) |
| 129 | do_09 / DO9 · PB0 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO9 · PB0 (view_do_09, значение) |
| 130 | do_10 / DO10 · PB1 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO10 · PB1 (view_do_10, значение) |
| 131 | do_11 / DO11 · PE5 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO11 · PE5 (view_do_11, значение) |
| 132 | do_12 / DO12 · PE6 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO12 · PE6 (view_do_12, значение) |
| 133 | do_13 / DO13 · PE7 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO13 · PE7 (view_do_13, значение) |
| 134 | do_14 / DO14 · PE8 | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / DO14 · PE8 (view_do_14, значение) |
| 135 | ao_0 / AO0 · PA4 | int32 | ПЛК ↔ веб | Publish Int + Command Int | Выходы / AO0 · PA4 (view_ao_0, значение) |
| 136 | ao_1 / AO1 · PA5 | int32 | ПЛК ↔ веб | Publish Int + Command Int | Выходы / AO1 · PA5 (view_ao_1, значение) |
| 137 | web_control / Управление выходами из веба | bool | ПЛК ↔ веб | Publish Bool + Command Bool | Выходы / Управление DO/AO из веба (web_control_mode, значение) |

## Подключение блоков

- Publish: `EN`, `CHANNEL`, `VALUE` — фактические данные программы передаются в веб.
- Command: `EN`, `CHANNEL` → `NEW`, `VALUE`. `NEW` означает новую команду, а не её выполнение.
- Duplex: используются оба блока с одним CHANNEL. Publish возвращает фактическое значение.
- busy/result/enabled — самостоятельные связи с каналами. Назначение каждой связи указано в таблице.
- Канал без виджета разрешён: его наличие само по себе не является ошибкой.
- Пароли и текущие значения каналов в отчёт не включаются.
