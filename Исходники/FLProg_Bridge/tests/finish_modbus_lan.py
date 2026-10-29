from pathlib import Path
import json,shutil,hashlib,zipfile,re
r=Path.cwd();w=Path(r'E:\SAI\FLProg_Network\_work\modbus_lan_bridge_20261029')
log=(w/'BUILD.log').read_text(encoding='utf-8',errors='replace');assert 'Global variables use ' in log,'SDK link not complete'
flash=int(re.search(r'Sketch uses (\d+)',log)[1]);ram=int(re.search(r'Global variables use (\d+)',log)[1])
binfile=w/'build/BridgeModbusLanPrototype.ino.bin';assert binfile.stat().st_mtime>=(w/'build/sketch/BridgeModbusLanPrototype.ino.cpp.o').stat().st_mtime
for source in (w/'BridgeModbusLanPrototype').glob('*.h'):
 text=(w/'build/sketch'/source.name).read_text(encoding='utf-8-sig').splitlines();text=text[1:] if text[0].startswith('#line ') else text
 assert '\n'.join(text)=='\n'.join(source.read_text(encoding='utf-8-sig').splitlines()),source.name
 assert source.read_bytes()==(r/'flprog_bridge/esp32/FLProgBridgeEsp32'/source.name).read_bytes(),source.name
actual=(w/'build/libraries/FLProg_Network/flprogNetwork.cpp.d').read_text(encoding='utf-8',errors='replace');assert str(w/'libraries/FLProg_Network/src/flprogNetwork.cpp') in actual
library=w/'libraries/FLProg_Network';reference=Path(r'E:\SAI\FLProg_Network\releases\FLProg_Network_2026-10-29_r17\Библиотека\FLProg_Network')
for p in reference.rglob('*'):
 if p.is_file():assert p.read_bytes()==(library/p.relative_to(reference)).read_bytes(),p
assert (r/'flprog_bridge/firmware/FLProgBridgeProtocol.h').read_bytes()==(r/'flprog_bridge/esp32/FLProgBridgeEsp32/BridgeWire.h').read_bytes()
checks=json.loads((w/'CHECKS.json').read_text(encoding='utf-8'));checks['esp32_compile']={'flash':flash,'static_ram':ram,'core':'3.3.11','board':'classic ESP32 WROOM','compiled_headers_match':True,'isolated_r17_library_verified':True,'wifi_wired_rmii_static_assert':True,'flashed':False};(w/'CHECKS.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
build=json.loads((w/'BUILD.json').read_text(encoding='utf-8'));build.update(runtime_setup=False,runtime_configuration=True,config_namespace='flpbridge-lan',service_modes=['raw3234','modbus502'],library='FLProg_Network r17 private copy',web_settings_integrated=False);(w/'BUILD.json').write_text(json.dumps(build,indent=2),encoding='utf-8')
dst=w/'FLProg_Bridge_Modbus_LAN_Prototype';dst.mkdir(exist_ok=True)
shutil.copytree(w/'BridgeModbusLanPrototype',dst/'ESP32/BridgeModbusLanPrototype',dirs_exist_ok=True)
shutil.copytree(library,dst/'Библиотека/FLProg_Network',dirs_exist_ok=True)
(dst/'ПЛК').mkdir(exist_ok=True)
for name in ['FLProgBridgeProtocol.h','FLProgModbusBridge.h']:shutil.copy2(r/'flprog_bridge/firmware'/name,dst/'ПЛК'/name)
(dst/'Проверки').mkdir(exist_ok=True)
shutil.copytree(w/'network_stub',dst/'Проверки/network_stub',dirs_exist_ok=True)
shutil.copy2(r/'flprog_bridge/PROTOCOL_RU.md',dst/'ПЛК/ПРОТОКОЛ.md')
for name in ['CHECKS.json','TCP_CHECKS.json','NETWORK_BACKENDS.json','BUILD.json','BUILD.log','plc_f407_compile.cpp','modbus_tcp_native_server.exe']:shutil.copy2(w/name,dst/'Проверки'/name)
for name in ['modbus_lan_test.cpp','network_endpoint_test.cpp','modbus_tcp_native_server.cpp','test_modbus_tcp_native.py','relay_test.cpp']:shutil.copy2(r/'flprog_bridge/tests'/name,dst/'Проверки'/name)
(dst/'BIN').mkdir(exist_ok=True);shutil.copy2(binfile,dst/'BIN/BridgeModbusLanPrototype_application_0x10000.bin')
shutil.copy2(r/'flprog_bridge/docs/MODBUS_LAN_RU.md',dst/'ИНСТРУКЦИЯ.md')
(dst/'README.md').write_text(f'''# FLProg Bridge — Modbus и LAN, программный прототип

Отдельный пример для классической ESP32 WROOM. Выбор Wi-Fi / WiznetSPI / RMII LAN8720 через API/NVS. Режимы: service1=ModbusTCP502,service0=прозрачныйBridge3234. Он не заменяет основной0.7: GUIвыбораLAN и самостоятельныйвеб8081черезLAN ещё не перенесены. Устройства не прошивались, Гит не менялся.

Начните с ИНСТРУКЦИЯ.md. ESP32/BridgeModbusLanPrototype — скетч и заголовки. ПЛК — адаптер службы2 и транспорт; подключение к банкам приложения с явной политикойзаписи. Без неё только чтение. Библиотека — неизменённая FLProg_Networkr17; штатные RT_HW_BASE/Flprog_Utilites не включены и не заменяются. Длясборки нужны их обычные версии изFLProgIDE.

BIN — только проверочный образ другого приложения ESP, не готовое обновление0.7. КомпиляцияESP32core3.3.11/FULL/EMAC прошла: Flash{flash},staticRAM{ram}байт. Памятьнастоящегоheap/радио/SPI/UARTещёнеизмерена.

Проверки/CHECKS.json и TCP_CHECKS.json — результаты native/настоящегоlocalhostTCP/ARMobject. Программный стенд Windows (PowerShell):

    .\\Проверки\\modbus_tcp_native_server.exe

Он слушает только127.0.0.1 наслучайномпорту, печатаетJSONадрес, поумолчанию записьзакрыта. Длявиртуальныхзаписей аргумент --allow-writes; это не доступ к физическомуПЛК. Ctrl+Cостанавливаетсервер. TCPтест:

    python .\\Проверки\\test_modbus_tcp_native.py --work .\\Проверки

АппаратнаяпроверкаESP/FLE4Dиединаяинтеграциявосновнойвеб/менеджер—следующиеэтапы. SHA256.json покрывает файлы комплекта кроме самого списка.
''',encoding='utf-8')
hashes={p.relative_to(dst).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dst.rglob('*')) if p.is_file() and p.name!='SHA256.json'};(dst/'SHA256.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf-8')
z=Path(shutil.make_archive(str(dst),'zip',root_dir=dst.parent,base_dir=dst.name))
with zipfile.ZipFile(z) as archive:
 assert archive.testzip() is None
 for name,sha in hashes.items():assert hashlib.sha256(archive.read(dst.name+'/'+name)).hexdigest()==sha,name
assert b'<configured Wi-Fi>' not in binfile.read_bytes()
result={'archive':str(z),'files':len(hashes),'zip_sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'crc':'PASS','sha':'PASS','flashed':False,'published':False,'flash':flash,'static_ram':ram};(w/'PACKAGE_VERIFIED.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
