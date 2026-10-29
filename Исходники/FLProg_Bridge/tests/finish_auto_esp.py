# coding: utf-8
from pathlib import Path
import json,shutil,hashlib,re
r=Path(r'E:\FLP\Flprog_network');a=Path(r'E:\SAI\FLProg_Network\_work\bridge_auto_20261029');e=Path(r'E:\SAI\FLProg_Network\_work\esp32_bridge_20261029');out=a/'Проверка_автопривязки_и_TCP'
assert not out.exists();out.mkdir()
shutil.copytree(a/'editor_final_dist/FLProg_WebUI_Editor',out/'Редактор')
shutil.copytree(e/'bridge_dist/FLProg_Bridge',out/'Мост_связи')
shutil.copytree(a/'manager_final_dist/FLProg_Firmware_Manager',out/'Менеджер_прошивок')
old=Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028\Менеджер_прошивок')
for name in ('profiles','build_tools'):shutil.copytree(old/name,out/'Менеджер_прошивок'/name,ignore=shutil.ignore_patterns('settings.json','__pycache__','*.pyc'))
shutil.copy2(r/'flprog_webui_next/tools/build_compatibility.py',out/'Менеджер_прошивок/build_tools/build_compatibility.py')
shutil.copytree(a/'Блоки_FLProg',out/'Блоки_FLProg')
for name in ('FLProg_Network','FLProg_WebUI','FLProg_WebUI_Project_FLE4D-30MT'):shutil.copytree(a/'libraries'/name,out/'libraries'/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(a/'FLE4D_Auto',out/'Контрольный_проект_FLE4D')
shutil.copytree(r/'flprog_bridge/esp32/FLProgBridgeEsp32',out/'ESP32_прототип')
docs=out/'Документация';docs.mkdir()
for name in ('AUTO_BINDING_RU.md','ESP32_TCP_UART_RU.md','ETHERNET_LINK_RU.md','FLASH_WEB_RU.md'):shutil.copy2(r/'flprog_bridge/docs'/name,docs/name)
shutil.copy2(r/'flprog_bridge/LICENSE_PYSERIAL.md',out/'Мост_связи/LICENSE_PYSERIAL.md')
binDir=out/'Контрольные_BIN';binDir.mkdir();build=json.loads((a/'BUILD.json').read_text(encoding='utf-8'));shutil.copy2(build['bin'],binDir/'FLE4D_1.0.12_compile_only.bin')
assert hashlib.sha256(Path(build['base_source']).read_bytes()).hexdigest()==build['base_source_sha256']
report=dict(auto_binding=dict(version=build['version'],flash=367404,static_ram=51948,delta_to_1_0_10=dict(flash=848,static_ram=304),bin_sha256=build['sha256'],flashed=False),esp32=dict(core='3.3.11',flash=894832,static_ram=46936,flashed=False),tests=dict(editor=100,protocol=20,auto_binding=3,tcp=3,bounded_relay=True,frozen_editor_export_and_bridge_tcp=True),installed_plc_unchanged='1.0.10-BRIDGE-LINK',git_published=False)
(out/'ПРОВЕРКИ.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
text='''# Рабочая проверка автопривязки и TCP моста

Это предварительный комплект разработки, не замена опубликованного релиза.

## Что сделано

- UART-блоки v0.2 автоматически связываются с проектом из экспорта. Для Basic и обычного Professional ID берётся из Web UI Start. UART Project Professional задаёт ID в своём параметре и может работать без HTTP. Новые UBI находятся в Блоки_FLProg/Bridge_UART и вкладываются в экспортированный пакет проекта.
- Новый EXE редактора создаёт entry, ресурсы и паспорт с проверкой всех заголовков. Менеджер0.8.0-preview.8 понимает новый состав паспорта; в его профиле сохранена проверенная прошивка1.0.10.
- FLProg Bridge0.4.0-preview.1 поддерживает явное tcp://IP:порт в дополнение к COM. ESP32-прототип переводит TCP в UART, не повторяя команды. Браузер и HTTP пока работают на PC, автономного HTTP на ESP ещё нет.

## Проверки

100 тестов редактора,20 протокола,3 привязки,3 TCP и нативный bounded relay прошли. Проверены frozen EXE: экспорт реального редактора создаёт entry/паспорт/UBI без копирования в IDE; мост по localhost TCP получает веб с C++-стенда, команды закрыты по умолчанию. Это программные проверки, не радиоиспытание ESP.

FLE4D1.0.12 собран: Flash367404 и static RAM51948 байт (+848/+304 к1.0.10). Контрольный BIN находится в Контрольные_BIN и пока не устанавливался. На ПЛК остаётся проверенная1.0.10-BRIDGE-LINK. ESP32 classic/core3.3.11 собрана: Flash894832/RAM46936; не прошивалась, учётные данные сети не заданы. Рабочие .116/.117 не использовались.

## Как смотреть

1. Редактор/FLProg_WebUI_Editor.exe — открыть свой .flpui и экспортировать для моста. Открытые старые программы этим комплектом не заменены.
2. libraries содержит две изменённые библиотеки и пакет FLE4D. Это не полный общий релиз и не установщик: штатные библиотеки не заменять. В менеджере выбрать именно эту внешнюю папку libraries для контрольной сборки. На компьютере для FLE4D также используются его обычные зависимости из IDE.
3. Для ESP читать Документация/ESP32_TCP_UART_RU.md. Воспользоваться исходником можно только после выбора отдельной платы, UART и локальной сети. Пока задача пользователя — прототип без прошивки ESP.

Первый следующий аппаратный шаг — проверка нового UART-блока/автопривязки на ПЛК и отдельной ESP32. Modbus/MQTT-службы через мост не реализованы. Прежние релизы, архивы, установленная IDE и GitHub не изменены.
'''
(out/'ПРОЧИТАТЬ.md').write_text(text,encoding='utf-8')
manifest={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()};(out/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(a/'CURRENT.md').write_text('# Текущая рабочая проверка\n\n'+str(out)+'\n\nПрочитайте ПРОЧИТАТЬ.md. Это рабочий комплект, не готовый опубликованный релиз. ПЛК1.0.10 и ESP не прошивались.\n',encoding='utf-8')
print(json.dumps(dict(folder=str(out),files=len(manifest),report=report),ensure_ascii=False))
