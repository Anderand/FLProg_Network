# coding: utf-8
"""Create the two-program portable handoff; never alters running programs."""
import hashlib,json,re,shutil,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent.parent;B=Path(r'E:\SAI\FLProg_Network');U=B/'_work/bridge_web_20261028/user4'
base=B/'releases/FLProg_Network_FLE4D_1.0.8_COM_2026-10-28_r2'
name='FLProg_Network_Manager_Bridge_2026-10-28_v1';out=B/'releases'/name;archive=out.parent/(name+'.zip')
assert not out.exists() and not archive.exists()
out.mkdir()
shutil.copytree(base/'Менеджер_прошивок',out/'Менеджер_прошивок',ignore=shutil.ignore_patterns('settings.json','__pycache__'))
shutil.copytree(U/'guard_manager_dist/FLProg_Firmware_Manager',out/'Менеджер_прошивок',dirs_exist_ok=True)
shutil.copytree(base/'Мост_связи',out/'Мост_связи')
shutil.copytree(base/'Проект_профиля/bridge_web',out/'Проект_профиля/bridge_web')
shutil.copy2(R/'flprog_bridge/MANAGER_RU.md',out/'Менеджер_прошивок/README_RU.md')
shutil.copy2(R/'flprog_bridge/MANAGER_RU.md',out/'Мост_связи/MANAGER_RU.md')
shutil.copy2(base/'LICENSE_PYTHON.md',out/'LICENSE_PYTHON.md')
guide='''# FLProg Network — менеджер и мост

Переносимый комплект Windows: **Менеджер прошивок0.8.0-preview.5** и
**Мост связи0.2.0**, профиль **FLE4D-30MT1.0.8-BRIDGE-WEB**.

## Запуск

Полностью распакуйте ZIP. Запускайте `Менеджер_прошивок\\FLProg_Firmware_Manager.exe`
или `Мост_связи\\FLProg_Bridge.exe`. Папки `_internal` оставьте рядом с EXE.
Python устанавливать не требуется. Личные настройки автора не включены.

## Веб через COM

1. В менеджере откройте вкладку **COM / UART**, обновите список и выберите
   свой COM и скорость115200. Номер COM зависит от вашего компьютера.
2. Для прошитого профиля подключение: UART6 PC6 TX / PC7 RX, 115200,8N1.
3. Папка веб-проекта — `Проект_профиля\\bridge_web`, она определяется рядом
   с менеджером. Если комплект перемещён и сохранён старый путь, выберите её заново.
4. Нажмите «Подключить веб через выбранный COM». Откроется самостоятельный мост.
   В его окне нажмите «Открыть веб-интерфейс». Используйте показанный localhost-адрес;
   порт выбирается при запуске. Одновременно COM может занимать только одна программа.
5. Для управления DO/AO отдельно разрешите команды в мосте и включите режим
   управления на странице «Выходы». Сохраняются подтверждения и ограничения ПЛК.

**В этой версии HTML/JavaScript и макет веба хранятся на компьютере в bridge_web.**
Через COM передаются значения каналов и команды. Сам веб из Flash ПЛК через UART
ещё не скачивается. Папку bridge_web нужно передавать вместе с программами;
ID/API/хеш должны совпадать с установленной прошивкой. На Ethernet веб выдаёт сам ПЛК.

Мост работает самостоятельно, менеджер можно закрыть после его запуска.
[Подробности моста](Мост_связи/docs/FULL_WEB_RU.md).

## Прошивка

В менеджере выбран готовый профиль FLE4D-30MT1.0.8. При пустом поле BIN используется
программа этого профиля. Приложение —0x08010000, загрузчик —0x08000000.
Ethernet настроен по DHCP; найдите адрес сканером и выберите своё устройство.
OTA передаёт приложение по Ethernet и сохраняет загрузчик. Для OTA требуется
уже установленный совместимый загрузчик.

Для первичной записи по SWD или UART отдельно установите STM32CubeProgrammer
и укажите `STM32_Programmer_CLI.exe` из его папки bin. В комплект он не включён.
Графический `STM32CubeProgrammer.exe` не запускается: менеджер выбирает соседний CLI
или выдаёт понятную ошибку, если CLI не найден. Если ST установлен стандартно,
менеджер находит CLI автоматически. IP для SWD/UART не требуется.

**Для первичной UART-записи F407 не подходит UART6.** Нужен USART1 PA9 TX / PA10 RX
либо USART3 PB10 TX / PB11 RX (также PC10/PC11) и системный ROM-загрузчик:
BOOT0=1, BOOT1=0, RESET. ROM использует8E1. Выводы и доступ к BOOT проверьте по
схеме платы; RS-485 не является TTL UART. На вкладке COM / UART сначала проверьте
ROM, затем запишите загрузчик и приложение. После записи BOOT0=0 и RESET.
[Руководство менеджера](Менеджер_прошивок/README_RU.md).

Для нескольких ПЛК в одной Ethernet-сети назначайте уникальные MAC при сборке:
готовый BIN содержит MAC проверенного стенда. Для собственных сборок менеджеру
нужны ваша IDE, STM32 core3.0.0, скетч и библиотеки проекта.

## Проверено

FLE4D: полный веб COM, четыре страницы, команды, DO1/AO0 по регистрам, DHCP/OTA,
восстановление после reset и работа при физически отключённом Ethernet.
Первичная ROM UART-прошивка проверена программными тестами; на реальном UART ROM
ещё не испытывалась. При этой упаковке ПЛК не прошивался, работающие программы
не останавливались. [Результаты](Проверки/ПРОВЕРКИ.md).
'''
(out/'ПРОЧИТАТЬ.md').write_text(guide,encoding='utf-8')
(out/'Мост_связи/README_RU.md').write_text('# Мост связи0.2.0\n\nЗапустите FLProg_Bridge.exe. COM выбирается здесь или на вкладке COM / UART менеджера.\nДля полного веба выберите соседнюю папку Проект_профиля\\bridge_web; прошивка должна совпадать с ней по ID и хешу.\n[Инструкция комплекта](../ПРОЧИТАТЬ.md), [API](API_RU.md).\n',encoding='utf-8')
checks=out/'Проверки';checks.mkdir()
for source,target in ((U/'MANAGER_CLI_GUARD_TESTS.log','MANAGER_CLI_GUARD_TESTS.log'),(U/'WEB_NO_ETHERNET.png','WEB_NO_ETHERNET.png'),(U/'NO_ETHERNET.json','NO_ETHERNET.json')):shutil.copy2(source,checks/target)
(checks/'ПРОВЕРКИ.md').write_text('# Проверки\n\nМенеджер0.8.0-preview.5 собран с защитой CLI:12 тестов UART/CLI прошли, включая остановку до запуска неверного EXE и выбор CLI вместо GUI.\n\nПрофиль1.0.8 и мост0.2.0 не менялись. На FLE4D ранее проверены полный COM-веб, подтверждения, GPIO/DAC, OTA/reset без повтора команд; без Ethernet —4страницы, RAM-команда и0ошибок кадров. Напряжение на клеммах не измерялось, reset без Ethernet не выполнялся.\n\nПервичная запись по ROM UART аппаратно пока не проверена. Новая сборка менеджера не запускалась на контроллер для записи; действующие приложения не трогали.\n',encoding='utf-8')
profile=out/'Менеджер_прошивок/profiles/fle4d_30mt_profile_1_0_8/profile.json';meta=json.loads(profile.read_text(encoding='utf-8'))
app=profile.with_name('application.bin').read_bytes();assert hashlib.sha256(app).hexdigest()==meta['artifacts']['application']['sha256']=='4c4763e1c9b2179037567b12d241750a7453b069f2f8afb899cb877ac5080176'
site=out/'Проект_профиля/bridge_web';web=json.loads((site/'bridge.json').read_text(encoding='utf-8'))
assert web['projectHash'].encode() in app and web['projectHash']==meta['bridge']['web_hash']
for relative,digest in web['files'].items():assert hashlib.sha256((site/relative).read_bytes()).hexdigest()==digest
for exe in ('Менеджер_прошивок/FLProg_Firmware_Manager.exe','Мост_связи/FLProg_Bridge.exe'):assert (out/exe).read_bytes()[:2]==b'MZ'
assert not list(out.rglob('settings.json'))
manifest={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
(out/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for relative in list(manifest)+['MANIFEST_SHA256.json']:z.write(out/relative,name+'/'+relative)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for relative,digest in manifest.items():assert hashlib.sha256(z.read(name+'/'+relative)).hexdigest()==digest,relative
    assert len(z.namelist())==len(manifest)+1
digest=hashlib.sha256(archive.read_bytes()).hexdigest();archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n',encoding='utf-8')
result=dict(folder=str(out),archive=str(archive),sha256=digest,bytes=archive.stat().st_size,files=len(manifest)+1,manager='0.8.0-preview.5',bridge='0.2.0',firmware='1.0.8-BRIDGE-WEB',crc_verified=True,all_hashes_verified=True,web_hash_verified=True,personal_settings_included=False,applications_restarted=False,git_updated=False)
(U/'MANAGER_BRIDGE_PACKAGE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(B/'CURRENT_MANAGER_BRIDGE.md').write_text('# Менеджер + мост для передачи\n\n[Архив](releases/'+archive.name+').\n\nМенеджер0.8.0-preview.5, мост0.2.0, профильFLE4D1.0.8 и папка веба включены.\nВеб черезCOM использует ресурсы наPC; черезUART передаются данные/команды.\nSHA-256: `'+digest+'`. CRC и SHA всех файлов проверены.\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
