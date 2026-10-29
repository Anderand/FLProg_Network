from pathlib import Path
import shutil,json,hashlib,zipfile
r=Path.cwd();w=Path(r'E:\SAI\FLProg_Network\_work\esp32_commands_20261029');dst=w/'ESP32_Universal_0.7_Commands_Prototype';dst.mkdir(exist_ok=True)
checks=json.loads((w/'CHECKS.json').read_text(encoding='utf-8'));checks['browser']['lost_ack_unknown_no_replay']=True;checks['browser']['lost_ack_disables_write']=True;(w/'CHECKS.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
for src,target in [(r/'flprog_bridge/esp32',dst/'source/esp32'),(r/'flprog_bridge/firmware',dst/'source/firmware'),(r/'flprog_webui_next/runtime/FLProg_WebUI/src',dst/'source/webui_src'),(r/'flprog_bridge/tests',dst/'source/tests'),(w/'native_stubs',dst/'native_fixture/native_stubs')]:shutil.copytree(src,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
for name in ['MockProject.h','MockIdentity.h','fixture.gz','fixture_package.json','FIXTURE.json','command_web_preview_peer_release.exe']:shutil.copy2(w/name,dst/'native_fixture'/('command_web_preview_peer_final.exe' if name=='command_web_preview_peer_release.exe' else name))
shutil.copy2(w/'fixture_site/firmware/FLProgBridgeProject.h',dst/'native_fixture/FLProgBridgeProject.h')
(dst/'firmware').mkdir(exist_ok=True);shutil.copy2(w/'build/FLProgBridgeEsp32.ino.bin',dst/'firmware/ESP32_Universal_0.7_application_0x10000.bin')
for name in ['CHECKS.json','COMMAND_CHECKS.json','BUILD.json','BUILD.log','COMMANDS_PREVIEW.png','COMMAND_TIMEOUT.png']:shutil.copy2(w/name,dst/name)
shutil.copy2(r/'flprog_bridge/docs/ESP32_COMMANDS_RU.md',dst/'ИНСТРУКЦИЯ.md')
(dst/'README.md').write_text('''# ESP32 Universal0.7 — команды WebUI, программный прототип

Без PC Bridge: полный веб из Flash ПЛК, чтение и явное включение команд. Инструкция: ИНСТРУКЦИЯ.md. Результаты: CHECKS.json. Устройства не прошивались. BIN приложения ESP32 WROOM находится в firmware, адрес0x10000, не устанавливать автоматически.

Программный стенд с реальными C++ обработчиками (Python3, COM не использует):

    python source/tests/preview_command_web.py --worker native_fixture/command_web_preview_peer_final.exe --status-file preview-status.json

Откройте адрес localhost из консоли. «Включить управление», вкладка «Выходы», измените виртуальный DO/AO и подтвердите. Для потери ACK добавьте --fault drop-ack. Значения DEMO, физических устройств нет.

Тесты HTTP/протокола и потери ACK:

    python source/tests/test_esp_commands.py --work native_fixture --worker command_web_preview_peer_final.exe

Тесты SHA/gzip:

    node source/tests/test_project_codec.js native_fixture

Пересборка native worker: C++17, исходник source/tests/command_web_preview_peer.cpp, include source/esp32/FLProgBridgeEsp32, source/firmware, source/webui_src, native_fixture и native_fixture/native_stubs. Компиляция ESP32 проверена с Arduino core3.3.11/esp32:esp32:esp32; компиляторы не включены.

На ESP не хранится весь веб-пакет и нет проекта/SSID/паролей в универсальном BIN. Динамический heap/радио/физический UART не измерены. Статическая память: Flash976192, RAM48440; к0.6 +8520/+72байта. Общий релизr17 и Гит не менялись.
''',encoding='utf-8')
hashes={p.relative_to(dst).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dst.rglob('*')) if p.is_file() and p.name!='SHA256.json'};(dst/'SHA256.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf-8')
z=Path(shutil.make_archive(str(dst),'zip',root_dir=dst.parent,base_dir=dst.name))
with zipfile.ZipFile(z) as archive:
 assert archive.testzip() is None
 for name,sha in hashes.items():assert hashlib.sha256(archive.read(dst.name+'/'+name)).hexdigest()==sha,name
assert b'<configured Wi-Fi>' not in (dst/'firmware/ESP32_Universal_0.7_application_0x10000.bin').read_bytes()
report={'package':str(dst),'archive':str(z),'files':len(hashes),'crc':'PASS','sha256':'PASS','zip_sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'flashed':False,'published':False};(w/'PACKAGE_VERIFIED.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
