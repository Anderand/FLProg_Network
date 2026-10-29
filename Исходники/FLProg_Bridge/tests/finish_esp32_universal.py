# coding: utf-8
from pathlib import Path
import json,hashlib,shutil,subprocess
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\esp32_universal_20261029');out=w/'ESP32_Bridge_Universal_0.2';assert not out.exists();out.mkdir()
build=json.loads((w/'BUILD.json').read_text(encoding='utf-8'));assert build['universal_plc_bridge'] and not build['flashed']
images=out/'Прошивка';images.mkdir()
for source,target in [('FLProgBridgeEsp32.ino.bin','ESP32_Bridge_Universal_0.2_application.bin'),('FLProgBridgeEsp32.ino.merged.bin','ESP32_Bridge_Universal_0.2_first_install_4MB.bin')]:
 p=w/'build'/source;assert hashlib.sha256(p.read_bytes()).hexdigest()==build['files'][source];shutil.copy2(p,images/target)
shutil.copytree(r/'flprog_bridge/esp32/FLProgBridgeEsp32',out/'Исходники/FLProgBridgeEsp32')
shutil.copy2(r/'flprog_bridge/docs/ESP32_UNIVERSAL_RU.md',out/'ПРОЧИТАТЬ.md')
config=subprocess.run([str(w/'config_test.exe')],capture_output=True,check=True);(w/'CONFIG_TESTS.log').write_bytes(config.stdout+config.stderr)
relay=subprocess.run([r'E:\SAI\FLProg_Network\_work\esp32_bridge_20261029\relay_test.exe'],capture_output=True,check=True);(w/'RELAY_TESTS.log').write_bytes(relay.stdout+relay.stderr)
for p in (r/'flprog_bridge/esp32/FLProgBridgeEsp32').glob('*'):
 if p.suffix in ('.ino','.h'):
  text=p.read_text(encoding='utf-8');assert all(x not in text for x in ('FLE4D','projectId','FLPROG_BRIDGE_WEB_PACKAGE','WIFI_SSID='))
report=dict(version='ESP32 Universal0.2',board='classic ESP32 Dev Module / 4MB',core='3.3.11',flash=931864,static_ram=47504,application_bytes=932016,credentials_included=False,plc_project_included=False,runtime_settings=True,nvs_schema=1,flashed=False,hardware_verified=False,config_test=config.stdout.decode().strip(),relay_test=relay.stdout.decode().strip(),source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/'Исходники/FLProgBridgeEsp32').iterdir() if p.is_file()})
(out/'ПРОВЕРКИ.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'ОБРАЗЫ.md').write_text('''# Образы ESP32 Universal0.2

Сборка для классической ESP32 Dev Module,4MB flash. Она универсальна по отношению к проекту ПЛК; другой тип чипа ESP требует своей аппаратной сборки.

- ESP32_Bridge_Universal_0.2_application.bin — приложение, адрес0x10000 только при соответствующем загрузчике и таблице разделов этой сборки. Не является загрузчиком STM32.
- ESP32_Bridge_Universal_0.2_first_install_4MB.bin — объединённый4MB образ для первичной установки, базовый адрес0x0. Содержит загрузчик, разделы и приложение. Полная запись может сбросить NVS и прежние настройки; это не способ обновлять проект ПЛК.

Адреса исходной сборки: bootloader0x1000, partitions0x8000, boot_app0 0xe000, application0x10000; DIO80MHz/4MB. Образы собраны и проверены по SHA, но на физической ESP не испытывались. Ничего автоматически не прошивается. Для будущей аппаратной проверки сначала уточнить модель отдельной платы и COM-порт. РабочиеESP.116/.117 не использовать.

После первой установки настройки сети и UART вводятся через AP-страницу, а затем хранятся в NVS. Для смены веб-проекта на ПЛК не нужно записывать ни один из этих файлов заново.
''',encoding='utf-8')
manifest={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()};(out/'SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for name,digest in manifest.items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==digest
summary='\n29.10.2026: ESP32 Universal0.2 собрана, Flash931864/RAM47504. config120байт/валидацияPASS, boundedrelayPASS. Проверена независимость исходников отID/проектаПЛК. Комплект '+str(out)+' содержит application932016байт (SHA'+build['files']['FLProgBridgeEsp32.ino.bin']+'), полный4MBобразпервичнойустановки, исходники ирусскуюинструкцию. ПолнаязаписьможетсброситьNVS; приложениеобновляетсяпотекущейразметке, неSTM32загрузчик. Этоcompile-only, физическаяESP/AP/NVSнеиспытывались; ничего непрошивали. Старые прототипы/архивы/EXE/Git неизменны.\n'
for p in [Path(r'E:\SAI\Правила для Codex\Проекты\FLProg_Network.md'),Path(r'E:\SAI\FLProg_Network\AGENTS.md'),r/'flprog_bridge/ROADMAP_RU.md']:
 with p.open('a',encoding='utf-8') as f:f.write(summary)
(w/'CURRENT.md').write_text('# Универсальный ESP32-мост\n\n'+str(out)+'\n\nБез проекта ПЛК в BIN. Параметры через AP/NVS. Не прошивался.\n',encoding='utf-8')
print(json.dumps(dict(folder=str(out),files=len(manifest),application_sha256=build['files']['FLProgBridgeEsp32.ino.bin'],flashed=False),ensure_ascii=False))
