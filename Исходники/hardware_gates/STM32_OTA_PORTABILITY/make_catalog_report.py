import json
from pathlib import Path

root = Path(__file__).resolve().parent
rows = json.loads((root / 'boards_catalog.json').read_text(encoding='utf-8'))
lines = [
    '# STM32 в установленном FLProg', '',
    'Источник: ideV8/portable/packages/STMicroelectronics/hardware/stm32/3.0.0/boards.txt.', '',
    '53 варианта плат, 9 семейств. Это каталог портирования, не список готовой поддержки OTA.', '',
    '| Плата | MCU | Flash, KiB | RAM, KiB | Требуется |',
    '|---|---|---:|---:|---|',
]
for row in rows:
    reason = 'Драйвер Flash, загрузчик, разметка и проверка платы'
    if row['mcu'] == 'STM32F407xx':
        reason = 'Адаптация разметки F407 и проверка сети/платы'
    if row['flash'] <= 32768 or row['ram'] < 10664:
        reason = 'Текущий тестовый стек не помещается по Flash или RAM; нужна другая реализация'
    row['porting_requirement'] = reason
    lines.append('| {} | {} | {} | {} | {} |'.format(
        row['label'], row['mcu'], row['flash'] // 1024, row['ram'] // 1024, reason))
lines += [
    '', '## Общий контракт', '',
    'Один блок: EN, NET_NUM, PASSWORD; настройки сети берутся из проекта FLProg.',
    'Профиль платы описывает MCU, геометрию Flash, области загрузчика, приложения,',
    'staging, RAM, адрес векторов и способ запуска приложения.',
    'Каждому семейству нужна своя реализация работы с Flash и передачи управления.',
    'Для Cortex-M0 без VTOR требуется отдельное решение векторов прерываний.', '',
    'Первичная установка записывает загрузчик. OTA обновляет только приложение.',
    'Если два образа не помещаются, нужна внешняя память или другая схема восстановления.',
    'Наличие Generic-платы в FLProg не означает наличие Ethernet-модуля.', '',
    'Подтверждён полный цикл только на FLE4D-30MT / STM32F407VG 1 МиБ / W5500.',
    'Следующие реализации: F407 512 КиБ/1 МиБ, затем F103 256 КиБ.',
    'Остальные семейства требуют выбора staging, реализации и испытаний.',
    'Заменить проверку STM32F407xx на ARDUINO_ARCH_STM32 недостаточно и опасно.',
]
(root / 'README_RU.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
(root / 'boards_catalog.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
