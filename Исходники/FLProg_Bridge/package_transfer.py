# coding: utf-8
"""Package the verified FLE4D preview for transfer without touching running apps."""
import hashlib,json,re,shutil,struct,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent.parent
B=Path(r'E:\SAI\FLProg_Network');U=B/'_work/bridge_web_20261028/user4'
ready=json.loads((U/'FINAL.json').read_text(encoding='utf-8'));source=Path(ready['folder'])
assert ready['hardware_tested'] and ready['ethernet_unplug_test']
base=B/'releases/FLProg_Network_2026-10-28_r16'
name='FLProg_Network_FLE4D_1.0.8_COM_2026-10-28'
out=B/'releases'/name;archive=out.parent/(name+'.zip')
assert not out.exists() and not archive.exists(),'Never overwrite a release'
out.mkdir()
ignore=shutil.ignore_patterns('__pycache__','*.pyc','.git','settings.json')
for folder in ('Мост_связи','Редактор','Менеджер_прошивок','Проект_профиля'):
    # PyInstaller internals are copied intact, including its licenses/resources.
    shutil.copytree(source/folder,out/folder)
for library,path in (
 ('FLProg_WebUI',source/'Библиотека/FLProg_WebUI'),
 ('FLProg_Network',base/'Библиотека/FLProg_Network'),
 ('Flprog_Modbus',base/'Библиотека/Flprog_Modbus')):
    shutil.copytree(path,out/'Библиотека'/library,ignore=ignore)
shutil.copytree(base/'Блоки_FLProg',out/'Блоки_FLProg',ignore=ignore)
shutil.copytree(R/'flprog_webui_next/runtime/FLProg_WebUI/user_blocks',out/'Блоки_FLProg/WebUI',dirs_exist_ok=True,ignore=ignore)
shutil.copytree(base/'Документация',out/'Документация',ignore=ignore)
shutil.copytree(base/'API_для_интеграции',out/'API_для_интеграции',ignore=ignore)
bridge_api=out/'API_для_интеграции/Мост_связи';bridge_api.mkdir()
for f in ('API_RU.md','PROTOCOL_RU.md'):shutil.copy2(R/'flprog_bridge'/f,bridge_api/f)
shutil.copytree(R/'flprog_bridge/firmware',bridge_api/'firmware')
for f in ('FULL_WEB_RU.md','FULL_WEB_CHECKS_RU.md'):shutil.copy2(R/'flprog_bridge/docs'/f,out/'Документация'/f)
checks=out/'Проверки';checks.mkdir()
for f in ('WEB_COM_FIXED.png','WEB_NO_ETHERNET.png','COM_HARDWARE.json','NO_ETHERNET.json'):
    shutil.copy2(U/f,checks/f)
shutil.copy2(U/'ПРОВЕРКИ.md',checks/'FLE4D_1.0.8.md')
shutil.copy2(base/'LICENSE_PYTHON.md',out/'LICENSE_PYTHON.md')

# Portable editor document: local output settings are not part of the UI hash.
project=out/'Проект_профиля/FLE4D-30MT.flpui'
doc=json.loads(project.read_text(encoding='utf-8'));doc.update(projectFolder='',packageOutput='',installToIde=False)
project.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Developer sources retain the original relative layout; no local hardware scripts.
sources=out/'Исходники';bridge=sources/'flprog_bridge';bridge.mkdir(parents=True)
for f in (R/'flprog_bridge').iterdir():
    if f.is_file() and f.suffix in ('.py','.md') and f.name!='package_transfer.py':shutil.copy2(f,bridge/f.name)
for folder in ('public','firmware','docs'):shutil.copytree(R/'flprog_bridge'/folder,bridge/folder,ignore=ignore)
(bridge/'tests').mkdir()
for f in ('test_bridge.py','test_web_project.py','peer.cpp'):shutil.copy2(R/'flprog_bridge/tests'/f,bridge/'tests'/f)
editor=sources/'flprog_webui_next'
for folder in ('editor','tools','runtime','projects','integration','specification'):
    shutil.copytree(R/'flprog_webui_next'/folder,editor/folder,ignore=ignore)
for f in ('ROADMAP_RU.md','README_RU.md'):
    if (R/'flprog_webui_next'/f).is_file():shutil.copy2(R/'flprog_webui_next'/f,editor/f)
for folder in ('hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER','hardware_gates/STM32_W5500_GATE/OTA_APP_FLE4D','hardware_gates/STM32_OTA_PORTABILITY'):
    target=sources/folder;target.mkdir(parents=True)
    for f in (R/folder).iterdir():
        if f.is_file() and f.suffix in ('.py','.md','.json'):shutil.copy2(f,target/f.name)
shutil.copytree(source/'Менеджер_прошивок/build_tools/STM32_OTA_BOOTLOADER',sources/'hardware_gates/STM32_OTA_PORTABILITY/STM32_OTA_BOOTLOADER',ignore=ignore)

guide='''# FLProg Network — комплект для передачи

Windows, FLE4D-30MT / STM32F407VG / W5500. Программа профиля **1.0.8-BRIDGE-WEB**,
Мост связи **0.2.0**, Менеджер прошивок **0.8.0-preview.3**.
Это проверенный локальный комплект нового направления COM, отдельный от опубликованного r16.

## Начало работы

1. Полностью распакуйте ZIP в любую доступную папку. Не запускайте EXE из архива.
2. Мост: `Мост_связи\\FLProg_Bridge.exe`. Python и редактор для его работы не нужны.
3. Прошивка: `Менеджер_прошивок\\FLProg_Firmware_Manager.exe`.
4. Конструктор: `Редактор\\FLProg_WebUI_Editor.exe`.
5. Папки `_internal` и файлы рядом с EXE оставьте на месте.

## Веб через COM без Ethernet

В профиле UART6 выделен только мосту: PC6 TX, PC7 RX, 115200 бод.
Выберите соответствующий COM-порт своего компьютера, скорость115200 и папку
`Проект_профиля\\bridge_web`. Подключитесь, затем нажмите «Открыть веб-интерфейс».
Используйте адрес, который покажет программа: номер локального порта выбирается
при запуске. COM5 и localhost64016 были адресами нашего стенда, задавать их всем не требуется.

На контроллере должна быть совместимая прошивка из профиля. Текстовая консоль и
Modbus RTU на UART6 отключены; другие UART сохранены. Для изменения выходов
разрешите команды в мосте и включите режим управления DO/AO на странице «Выходы».
Подтверждение, диапазоны и разрешения ПЛК сохраняются; после разрыва команды
автоматически не повторяются. Подробнее: [полный веб COM](Документация/FULL_WEB_RU.md).

## Прошивка FLE4D

В менеджере по умолчанию выбран профиль «проект4, DHCP + полный веб COM,1.0.8».
«Программа профиля» — готовый BIN приложения, не загрузчик.
Для OTA найдите контроллер сканером, выберите найденный IP и нажмите «Прошить по OTA».
Ethernet получает настройки от роутера по DHCP; фиксированный IP не зашит.
OTA использует Ethernet, а не COM-мост. Для OTA в ПЛК уже должен быть совместимый загрузчик.
Первичная установка по SWD требует ST-Link и STM32CubeProgrammer CLI, установленного отдельно.
Обычный BIN Arduino без смещения нельзя подставлять вместо OTA-программы этого профиля.
Приложение начинается с0x08010000, загрузчик — с0x08000000; OTA не пишет загрузочную область.

## Три библиотеки и блоки

Для STM32 нужен **STMicroelectronics STM32 core3.0.0** в IDE FLProg.
Закройте FLProg и Arduino IDE. Вручную скопируйте только `FLProg_Network`,
`FLProg_WebUI` и `Flprog_Modbus` из `Библиотека` в
`<папка IDE>\\portable\\sketchbook\\libraries`, с заменой файлов этих трёх папок.
Штатные RT_HW_00_BASE, Flprog_Utilites, Wire не входят в установку.
BAT-установщика нет. Снова откройте FLProg.

В `Блоки_FLProg` находятся WebUI, OTA, MQTT и диагностические блоки.
Импортируйте нужный `.ubi`/`.ubl` через пользовательскую библиотеку FLProg.
MQTT включает Basic и Professional. Универсальные UART-блоки ещё не выпущены:
в данном профиле мост подключён непосредственно в скетче.

## Проект и повторная сборка BIN

В `Проект_профиля` лежат:

- `FLE4D-30MT.flpui` — проект веб-редактора;
- `FLE4D_Profile_Bridge\\FLE4D_Profile_Bridge.ino` — адаптированный скетч для сборки;
- `4_ORIGINAL.ino` — неизменённый пользовательский исходник4;
- `libraries` — точный снимок библиотек для повторной сборки проверенного BIN;
- `bridge_web` — согласованный экспорт интерфейса для моста.

После открытия `.flpui` выберите полную папку `Проект_профиля` на своём компьютере:
локальный путь автора в файле очищен. Для сборки менеджером выберите адаптированный
`.ino`, свою IDE и `Проект_профиля\\libraries`. В IDE библиотеки проекта копировать не требуется.
Снимок в `Проект_профиля\\libraries` нужен для воспроизведения этого BIN;
для обычной установки актуальных библиотек, включая MQTT, используйте корневую `Библиотека`.
Нативный проект FLProg `.flp` не создавался: в комплекте `.ino` и `.flpui`.

Макет, каналы и хеш интерфейса должны совпадать с прошивкой. После изменения
веб-проекта заново экспортируйте его для моста и пересоберите ПЛК с новым `_bridge.h`.
Для нескольких устройств в одной Ethernet-сети назначьте каждому уникальный MAC
в проекте перед сборкой: готовый образ содержит MAC проверенного стенда.

## Что проверено

На FLE4D-30MT проверены четыре страницы, состояния полей, подтверждения, DO1/AO0
по регистрам GPIO/DAC, OTA и восстановление сеанса после reset. Физически отключён
Ethernet: веб продолжил работать через COM, программная команда вернулась с ПЛК,
ошибок кадров0. Без Ethernet повторный reset не выполнялся; напряжение на клеммах не измерялось.
Только этот профиль испытан на плате; остальные загрузчики скрыты общей галочкой непроверенных плат.
[Полный отчёт](Проверки/FLE4D_1.0.8.md), [API для интеграции](API_для_интеграции/Мост_связи/API_RU.md).

Исходники программ — в `Исходники`. Проект и программы не обращаются к исходным
папкам автора для запуска готовых EXE. GitHub этой операцией не обновлялся.
'''
(out/'ПРОЧИТАТЬ.md').write_text(guide,encoding='utf-8')
(out/'Инструкция.md').write_text(guide,encoding='utf-8')
(out/'Библиотека/УСТАНОВКА.md').write_text('# Установка\n\nВручную устанавливаются только три соседние папки библиотек.\nДля STM32 требуется core3.0.0. [Полная инструкция](../Инструкция.md).\n',encoding='utf-8')
(out/'README_RU.md').write_text('# FLProg Network: FLE4D и COM-веб\n\nНачните с [инструкции](Инструкция.md). Три готовых EXE, проверенная прошивка1.0.8, проект4, библиотеки, блоки и API включены.\n',encoding='utf-8')
(out/'README.md').write_text((out/'README_RU.md').read_text(encoding='utf-8'),encoding='utf-8')
for f in (out/'Документация').rglob('*.md'):
    text=f.read_text(encoding='utf-8-sig').replace('OTA_Менеджер','Менеджер_прошивок').replace('../Проверки/RELEASE_R15.md','../Проверки/FLE4D_1.0.8.md').replace('../Исходники/WebUI','../Исходники/flprog_webui_next');f.write_text(text,encoding='utf-8')

# Validate the actual build snapshot and immutable precompiled image.
profile=out/'Менеджер_прошивок/profiles/fle4d_30mt_profile_1_0_8/profile.json'
data=json.loads(profile.read_text(encoding='utf-8'));blob=profile.with_name('application.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()==ready['bin_sha256']==data['artifacts']['application']['sha256']
sp,pc=struct.unpack('<II',blob[:8]);assert sp==0x20020000 and 0x08010000<=pc&~1<0x08010000+len(blob)<0x08080000
assert ready['web_hash'].encode() in blob
assert hashlib.sha256((out/'Проект_профиля/4_ORIGINAL.ino').read_bytes()).hexdigest()==ready['source4_sha256']
assert set(p.name for p in (out/'Библиотека').iterdir() if p.is_dir())=={'FLProg_Network','FLProg_WebUI','Flprog_Modbus'}
for exe in ('Мост_связи/FLProg_Bridge.exe','Редактор/FLProg_WebUI_Editor.exe','Менеджер_прошивок/FLProg_Firmware_Manager.exe'):
    assert (out/exe).read_bytes()[:2]==b'MZ'
for f in out.rglob('*'):
    if not f.is_file():continue
    assert f.name not in ('flash_before_bridge.bin','BOOT_BEFORE.bin','BOOT_AFTER.bin','settings.json')
    assert not (f.suffix.lower()=='.bat' and 'install' in f.name.lower())
    assert not any(part in ('RT_HW_00_BASE','Flprog_Utilites','Wire') for part in f.relative_to(out).parts)
hashes={f.relative_to(out).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}
(out/'MANIFEST_SHA256.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in out.rglob('*'):
        if f.is_file():z.write(f,name+'/'+f.relative_to(out).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    archived=json.loads(z.read(name+'/MANIFEST_SHA256.json'))
    assert archived==hashes
    for relative,digest in archived.items():
        assert hashlib.sha256(z.read(name+'/'+relative)).hexdigest()==digest,relative
    assert len(z.namelist())==len(hashes)+1
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n',encoding='utf-8')
result=dict(folder=str(out),archive=str(archive),bytes=archive.stat().st_size,files=len(hashes)+1,sha256=digest,zip_crc_verified=True,all_hashes_verified=True,application_sha256=ready['bin_sha256'],source4_sha256=ready['source4_sha256'],libraries=3,executables=3,git_updated=False)
(U/'TRANSFER_PACKAGE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
