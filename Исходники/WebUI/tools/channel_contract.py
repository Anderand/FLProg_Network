"""A design-time FBD wiring report. Never exports channel values or credentials."""
import copy
import json

BLOCK_TYPES = {'bool': 'Bool', 'int32': 'Int', 'float': 'Float', 'text': 'Text'}
DIRECTIONS = {'publish': 'ПЛК → веб', 'command': 'Веб → ПЛК', 'duplex': 'ПЛК ↔ веб'}
ROLES = {'value': 'значение', 'setpoint': 'уставка', 'busy': 'выполняется', 'result': 'результат',
         'enabled': 'разрешение', 'alarm': 'авария', 'series1': 'ряд 1', 'series2': 'ряд 2'}


def channel_contract(document):
    # The legacy normalizer assigns missing FBD numbers and sorts channel groups.
    # Work on a copy, so viewing/exporting the report cannot change the editor.
    from build_project_package import validate
    design = copy.deepcopy(document)
    project_id, channels = validate(design)
    references = {c['id']: [] for c in channels}
    for page in design['pages']:
        for widget in page.get('widgets', []):
            links = [(widget.get('channel'), 'value')]
            links += [(b.get('channel'), b.get('role', 'value')) for b in widget.get('bindings', [])]
            for channel, role in links:
                if channel not in references:
                    continue
                reference = dict(page_id=page['id'], page_title=page.get('title') or page['id'],
                                 widget_id=widget['id'], widget_label=widget.get('label') or widget['id'],
                                 role=role, role_title=ROLES.get(role, role))
                if reference not in references[channel]:
                    references[channel].append(reference)
    rows = []
    for channel in sorted(channels, key=lambda item: item['index']):
        system = bool(channel.get('source') and channel['source'] != 'user')
        blocks = []
        if not system:
            if channel['direction'] in ('publish', 'duplex'):
                blocks.append('Publish ' + BLOCK_TYPES[channel['type']])
            if channel['direction'] in ('command', 'duplex'):
                blocks.append('Command ' + BLOCK_TYPES[channel['type']])
        rows.append(dict(index=channel['index'], id=channel['id'], label=channel.get('label') or channel['id'],
                         type=channel['type'], direction=channel['direction'],
                         direction_title=DIRECTIONS[channel['direction']], system=system,
                         source=channel.get('source') or 'user', blocks=blocks,
                         secret=channel.get('secret') is True, references=references[channel['id']]))
    return dict(schema='flprog.webui.channel-contract/1.0', project_id=project_id,
                project_title=design['project'].get('title') or project_id,
                transport=design.get('transport', {}).get('id', 'wifi-http'), channels=rows,
                summary=dict(system=sum(row['system'] for row in rows),
                             user=sum(not row['system'] for row in rows),
                             without_widgets=sum(not row['references'] for row in rows)))


def _cell(value):
    text = str(value).replace('\\', '\\\\').replace('\r', ' ').replace('\n', ' ')
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    for char in '|`[]*!':
        text = text.replace(char, '\\' + char)
    return text


def contract_markdown(report):
    lines = ['# Каналы для FLProg: ' + _cell(report['project_title']), '',
             'ID проекта: `' + report['project_id'] + '`. Транспорт: `' + report['transport'] + '`.', '',
             'Это схема подключения из макета. Она не подтверждает, что блоки уже добавлены в .flp.', '',
             '## Запуск', '', 'Один профессиональный блок **Web UI Start**, параметр **ID проекта**: `' + report['project_id'] + '`.',
             'В скетче: `#include <' + report['project_id'] + '_webui.h>` и `FLPROG_WEBUI_BEGIN_SELECTED();` после настройки сети.',
             'SPI и Ethernet задаются в проекте FLProg. Для сетевого обновления отдельно нужен OTA-блок.', '']
    for title, system in [('Системные каналы №0–100', True), ('Пользовательские каналы №101–255', False)]:
        lines += ['## ' + title, '',
                  'Заполняются библиотеками автоматически. Publish/Command для них не нужны.' if system else
                  'Номер из столбца CHANNEL задаётся на одноимённом входе универсального блока.', '',
                  '| CHANNEL | ID / название | Тип | Направление | Блоки FLProg | Виджеты и роли |',
                  '|---|---|---|---|---|---|']
        for channel in report['channels']:
            if channel['system'] != system:
                continue
            bindings = '; '.join('{page_title} / {widget_label} ({widget_id}, {role_title})'.format(**ref)
                                 for ref in channel['references']) or 'Виджет не использует канал'
            blocks = 'Автоматически' if system else ' + '.join(channel['blocks'])
            lines.append('| ' + ' | '.join(_cell(value) for value in [channel['index'],
                         channel['id'] + ' / ' + channel['label'], channel['type'],
                         channel['direction_title'], blocks, bindings]) + ' |')
        if not any(row['system'] == system for row in report['channels']):
            lines.append('| — | Каналов нет | — | — | — | — |')
        lines.append('')
    lines += ['## Подключение блоков', '',
              '- Publish: `EN`, `CHANNEL`, `VALUE` — фактические данные программы передаются в веб.',
              '- Command: `EN`, `CHANNEL` → `NEW`, `VALUE`. `NEW` означает новую команду, а не её выполнение.',
              '- Duplex: используются оба блока с одним CHANNEL. Publish возвращает фактическое значение.',
              '- busy/result/enabled — самостоятельные связи с каналами. Назначение каждой связи указано в таблице.',
              '- Канал без виджета разрешён: его наличие само по себе не является ошибкой.',
              '- Пароли и текущие значения каналов в отчёт не включаются.', '']
    return '\n'.join(lines)


def write_contract(document, target):
    report = channel_contract(document)
    (target / 'CHANNELS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (target / 'CHANNELS_RU.md').write_text(contract_markdown(report), encoding='utf-8')
    return report
