"""Read-only checks shared by the editor and the STM32 builder."""
import hashlib
import json
import re
from pathlib import Path

DESCRIPTOR_API = 1
MANIFEST = 'WEBUI_COMPATIBILITY.json'
SCHEMA = 'flprog.webui.build/1.0'
ID = re.compile(r'[A-Za-z][A-Za-z0-9_-]{1,63}')


def add(report, status, message, path=None):
    report['checks'].append(dict(status=status, message=message, path=str(path) if path else ''))


def finish(report):
    report['summary'] = {key: sum(c['status'] == status for c in report['checks'])
                         for key, status in [('errors', 'error'), ('warnings', 'warning')]}
    report['ok'] = not report['summary']['errors']
    return report


def runtime_check(report, library):
    library = Path(library)
    header = library / 'src/FLProgWebUi.h'
    adapter = library / 'src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h'
    if not header.is_file() or not adapter.is_file():
        add(report, 'error', 'Не найден полный runtime FLProg_WebUI. Укажите libraries с библиотекой из нового редактора.', library)
        return
    text = header.read_text(encoding='utf-8-sig')
    match = re.search(r'^\s*#define\s+FLPROG_WEBUI_DESCRIPTOR_API\s+(\d+)\b', text, re.M)
    if not match or int(match[1]) != DESCRIPTOR_API:
        add(report, 'error', 'Несовместимая FLProg_WebUI: нужен контракт заголовков API 1. Пересоберите пакет новым редактором; для IDE замените только FLProg_WebUI вручную.', header)
    else:
        add(report, 'ok', 'FLProg_WebUI: контракт заголовков API 1 совпадает.', header)


def check_directory(report, target):
    target = Path(target)
    nearest = target
    while not nearest.exists() and nearest != nearest.parent:
        nearest = nearest.parent
    if not nearest.is_dir():
        add(report, 'error', 'В пути папки находится файл. Выберите другую папку.', nearest)
    else:
        add(report, 'info', 'Папка назначения (проверка не создаёт файлы).', target)


def export_report(document, resource_root, projects, packages, ide_libraries):
    from project_storage import project_locations
    report = dict(kind='export', checks=[])
    try:
        if not isinstance(document, dict):
            raise ValueError('Ожидается объект проекта .flpui.')
        if document.get('schema') != 'flprog.webui/1.0' or not isinstance(document.get('project'), dict):
            raise ValueError('Неверная структура проекта .flpui: проверьте schema и project.')
        project_id = document.get('project', {}).get('id', '')
        if not isinstance(project_id, str) or not ID.fullmatch(project_id):
            raise ValueError('ID проекта: 2–64 латинских буквы, цифры, _ или -, начиная с буквы.')
        source, output = project_locations(document, projects, packages)
        if '\\libraries\\flprog_network' in str(output).replace('/', '\\').lower():
            raise ValueError('Пакет проекта нельзя размещать в FLProg_Network.')
        check_directory(report, source.parent)
        check_directory(report, output)
        check_directory(report, output / ('FLProg_WebUI_Project_' + project_id))
        runtime = Path(resource_root) / 'runtime/FLProg_WebUI'
        runtime_check(report, runtime)
        # Export always carries a matching runtime; old output is replaced only
        # by the explicit Build operation, never by this read-only check.
        check_directory(report, output / 'FLProg_WebUI')
        add(report, 'info', 'При сборке будут созданы заголовок ' + project_id + '_webui.h, descriptor и паспорт совместимости.', output)
        add(report, 'info', 'В папку libraries будет скопирован подходящий runtime FLProg_WebUI.', output / 'FLProg_WebUI')
        if document.get('installToIde') is True:
            if not Path(ide_libraries).is_dir():
                add(report, 'error', 'Папка libraries Arduino IDE не найдена. Снимите копирование в IDE или задайте правильный путь.', ide_libraries)
            else:
                runtime_check(report, Path(ide_libraries) / 'FLProg_WebUI')
                add(report, 'info', 'Копирование в IDE включено: будет обновлена только библиотека этого проекта; runtime устанавливается вручную.', ide_libraries)
        else:
            add(report, 'ok', 'Копирование в IDE выключено. Для компиляции передайте менеджеру эту папку libraries.', output)
        add(report, 'info', 'STM32 требует core 3.0.0. Здесь проверен экспорт; скетч и установленное ядро проверяет менеджер перед компиляцией.')
    except (OSError, ValueError, TypeError) as error:
        add(report, 'error', str(error))
    return finish(report)


def candidates(roots, header):
    found = []
    for root in roots:
        root = Path(root)
        if not root.is_dir():
            continue
        for path in sorted(root.glob('*/src/' + header)) + sorted(root.glob('*/' + header)):
            resolved = path.resolve()
            if path.is_file() and resolved not in found:
                found.append(resolved)
    return found


def choose(report, roots, header):
    found = candidates(roots, header)
    if not found:
        add(report, 'error', 'Не найден ' + header + '. Соберите пакет проекта в редакторе и укажите его папку libraries в менеджере.')
        return None
    add(report, 'ok', 'Найден ' + header, found[0])
    if len(found) > 1:
        add(report, 'warning', 'Есть дубли ' + header + '. Arduino выбирает библиотеку по своим правилам; сверяйте пути в логе. Новый descriptor дополнительно проверяет выбранный runtime при компиляции.', '; '.join(map(str, found)))
    return found[0]


def verify_manifest(report, wrapper, project_id):
    library = wrapper.parent.parent if wrapper.parent.name == 'src' else wrapper.parent
    path = library / MANIFEST
    if not path.is_file():
        add(report, 'error', 'У пакета нет паспорта совместимости. Пересоберите этот .flpui новым редактором; менять ID проекта или FBD-связи не нужно.', path)
        return
    try:
        manifest = json.loads(path.read_text(encoding='utf-8-sig'))
        if manifest.get('schema') != SCHEMA or manifest.get('projectId') != project_id or manifest.get('descriptorApi') != DESCRIPTOR_API:
            raise ValueError('ID проекта или контракт в паспорте не совпадает со скетчем.')
        safe = re.sub(r'[^A-Za-z0-9_]', '_', project_id)
        expected = {'src/' + project_id + '_webui.h', 'src/' + safe + '_descriptor.h'}
        files = manifest.get('files', {})
        if not isinstance(files, dict) or set(files) != expected:
            raise ValueError('Неполный паспорт: нужны оба сгенерированных заголовка.')
        for name, digest in files.items():
            target = library / name
            if library.resolve() not in target.resolve().parents:
                raise ValueError('Заголовок находится вне библиотеки проекта.')
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError('Отсутствует или изменён заголовок ' + name + '. Пересоберите пакет из .flpui.')
        add(report, 'ok', 'ID проекта и оба заголовка соответствуют паспорту сборки.', path)
    except (OSError, ValueError, TypeError, AttributeError) as error:
        add(report, 'error', 'Паспорт проекта: ' + str(error), path)


def sketch_report(sketch, ide, libraries=None):
    report = dict(kind='compile', checks=[])
    try:
        sketch, ide = Path(sketch), Path(ide)
        if not sketch.is_file() or sketch.suffix.lower() != '.ino':
            raise ValueError('Выберите существующий скетч .ino.')
        add(report, 'ok', 'Скетч найден.', sketch)
        if not (ide / 'arduino-builder.exe').is_file():
            add(report, 'error', 'Не найден arduino-builder.exe: проверьте путь Arduino IDE.', ide)
        core = ide / 'portable/packages/STMicroelectronics/hardware/stm32/3.0.0/cores/arduino/Arduino.h'
        add(report, 'ok' if core.is_file() else 'error', 'STM32 core 3.0.0 найден.' if core.is_file() else 'Не найден STM32 core 3.0.0. Версия 2.7.1 не поддерживается.', core)
        roots = []
        if libraries:
            folder = Path(libraries).expanduser().resolve()
            if not folder.is_dir():
                add(report, 'error', 'Папка библиотек проекта не найдена.', folder)
            else:
                roots.append(folder)
                if (folder / 'libraries').is_dir():
                    add(report, 'warning', 'Внутри выбранной папки есть libraries. Проверьте, что выбрана именно папка библиотек, а не корень проекта.', folder / 'libraries')
        roots.append(ide / 'portable/sketchbook/libraries')
        text = sketch.read_text(encoding='utf-8-sig')
        text = re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)
        wrappers = list(dict.fromkeys(re.findall(r'^\s*#\s*include\s*[<"]([^>"\n]*_webui\.h)[>"]', text, re.M)))
        if not wrappers:
            add(report, 'info', 'В скетче нет прямого include <ID_webui.h>: проверка пакета WebUI не применяется. Вложенные и условные подключения не раскрываются.')
        elif len(wrappers) > 1:
            add(report, 'error', 'Подключено несколько проектов WebUI. Оставьте один Web UI Start с нужным ID: ' + ', '.join(wrappers))
        else:
            name = wrappers[0]
            project_id = name[:-len('_webui.h')]
            if not ID.fullmatch(project_id):
                add(report, 'error', 'Неверный ID в include: ' + name)
            else:
                local = sketch.parent / name
                wrapper = local if local.is_file() else choose(report, roots, name)
                if wrapper:
                    verify_manifest(report, wrapper, project_id)
                runtime_header = choose(report, roots, 'FLProgWebUi.h')
                if runtime_header:
                    runtime_check(report, runtime_header.parent.parent)
                    if wrapper:
                        safe = re.sub(r'[^A-Za-z0-9_]', '_', project_id)
                        descriptor = wrapper.parent / (safe + '_descriptor.h')
                        helper = runtime_header.parent / 'adapters/FLProgWebUiWidgetCatalog.h'
                        if descriptor.is_file() and 'FLProgWebUiWidgetCatalog.h' in descriptor.read_text(encoding='utf-8-sig') and not helper.is_file():
                            add(report, 'error', 'Для каталога виджетов нужна FLProg_WebUI из того же нового пакета проекта. Обновите только эту библиотеку.', helper)
                choose(report, roots, 'flprogNetwork.h')
                if not re.search(r'\bFLPROG_WEBUI_BEGIN_SELECTED\s*\(', text):
                    add(report, 'warning', 'Не найден FLPROG_WEBUI_BEGIN_SELECTED(). Проверьте стартовый блок и вызов после настройки Ethernet.')
    except (OSError, ValueError, TypeError) as error:
        add(report, 'error', str(error))
    return finish(report)


def format_report(report):
    labels = {'ok': 'OK', 'info': 'INFO', 'warning': 'ВНИМАНИЕ', 'error': 'ОШИБКА'}
    lines = ['Совместимость: ошибок {errors}, предупреждений {warnings}.'.format(**report['summary'])]
    for check in report['checks']:
        lines.append(labels[check['status']] + ': ' + check['message'] + ('\n  ' + check['path'] if check['path'] else ''))
    return '\n'.join(lines)


def require_sketch(sketch, ide, libraries=None):
    report = sketch_report(sketch, ide, libraries)
    if not report['ok']:
        raise ValueError(format_report(report))
    return report
