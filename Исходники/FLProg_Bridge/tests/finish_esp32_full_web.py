from pathlib import Path
import shutil,json,hashlib,re
r=Path.cwd();w=Path(r'E:\SAI\FLProg_Network\_work\esp32_full_web_20261029');dst=w/'ESP32_Universal_0.6_Full_Web_Prototype';dst.mkdir(exist_ok=True)
checks=json.loads((w/'CHECKS.json').read_text(encoding='utf-8'));checks['build']={'flash':967672,'static_ram':48368,'vs_0_5_flash':19696,'vs_0_5_static_ram':456,'bin_bytes':(w/'build/FLProgBridgeEsp32.ino.bin').stat().st_size,'compiled_source_matches':True,'heap_hardware_measurement':False};(w/'CHECKS.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copytree(r/'flprog_bridge/esp32',dst/'source/esp32',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(r/'flprog_bridge/firmware',dst/'source/firmware',dirs_exist_ok=True)
shutil.copytree(r/'flprog_webui_next/runtime/FLProg_WebUI/src',dst/'source/webui_src',dirs_exist_ok=True)
shutil.copytree(r/'flprog_bridge/tests',dst/'source/tests',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(w/'native_stubs',dst/'native_fixture/native_stubs',dirs_exist_ok=True)
for name in ['MockProject.h','MockIdentity.h','fixture.gz','fixture_package.json','FIXTURE.json','full_web_preview_peer_final.exe']:
 shutil.copy2(w/name,dst/'native_fixture'/name)
shutil.copy2(w/'fixture_site/firmware/FLProgBridgeProject.h',dst/'native_fixture/FLProgBridgeProject.h')
(dst/'firmware').mkdir(exist_ok=True);shutil.copy2(w/'build/FLProgBridgeEsp32.ino.bin',dst/'firmware/ESP32_Universal_0.6_application_0x10000.bin')
for name in ['CHECKS.json','BUILD.json','BUILD.log','NATIVE_TRANSFER.json','FULL_WEB_PREVIEW.png']:
 shutil.copy2(w/name,dst/name)
shutil.copy2(r/'flprog_bridge/docs/ESP32_FULL_WEB_RU.md',dst/'ИНСТРУКЦИЯ.md')
readme='''# ESP32 Universal 0.6 — программный прототип полного веба

Полный веб из Flash ПЛК через ESP без PC Bridge. Это compile-only: на устройства не устанавливался. См. ИНСТРУКЦИЯ.md и CHECKS.json. Управление пока закрыто, чтение и 4 страницы проверены.

- firmware — только BIN приложения ESP32 WROOM, адрес0x10000. Не прошивать автоматически.
- source/esp32 — универсальная прошивка и браузерный загрузчик; проекта ПЛК и паролей в BIN нет.
- native_fixture — стендовый пакет FLE4D и модель DEMO, не измерения устройства.
- source/tests — тесты и локальный HTTP-адаптер C++ обработчиков. Программа PC Bridge не используется.

Запуск готового стенда из корня пакета (Python3):

    python source/tests/preview_full_web.py --worker native_fixture/full_web_preview_peer_final.exe --status-file preview-status.json

Адрес localhost будет выведен в консоль. Для отрицательного сценария добавьте --fault corrupt либо --fault wrong-id. Не открывает COM и не обращается к ESP/ПЛК.

Проверка передачи:

    python source/tests/test_full_web_transfer.py --work native_fixture --worker full_web_preview_peer_final.exe

Проверка SHA/gzip/манифеста (Node с DecompressionStream):

    node source/tests/test_project_codec.js native_fixture

Нативная пересборка (C++17): include source/esp32/FLProgBridgeEsp32, source/firmware, source/webui_src, native_fixture, native_fixture/native_stubs; исходник source/tests/full_web_preview_peer.cpp. Для ESP — Arduino ESP32 core3.3.11, плата esp32:esp32:esp32. Исходники ZIP не содержат компиляторы.

SHA256.json покрывает все файлы комплекта кроме самого списка. Гит и опубликованный общий релиз r17 не обновлялись.
'''
(dst/'README.md').write_text(readme,encoding='utf-8')
hashes={p.relative_to(dst).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dst.rglob('*')) if p.is_file() and p.name!='SHA256.json'};(dst/'SHA256.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf-8')
for name,sha in hashes.items():assert hashlib.sha256((dst/name).read_bytes()).hexdigest()==sha
archive=shutil.make_archive(str(dst),'zip',root_dir=dst.parent,base_dir=dst.name)
print(json.dumps({'package':str(dst),'archive':archive,'files':len(hashes),'zip_sha256':hashlib.sha256(Path(archive).read_bytes()).hexdigest()}))
