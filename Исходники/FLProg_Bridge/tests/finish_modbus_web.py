"""Archive the local software-only Universal 0.9 candidate after SDK link."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
r=Path(__file__).resolve().parents[2]
w=Path(r'E:\SAI\FLProg_Network\_work\esp32_modbus_web_20261029')
log=(w/'BUILD.log').read_text(encoding='utf-8',errors='replace')
flash=int(re.search(r'Sketch uses (\d+)',log)[1])
ram=int(re.search(r'Global variables use (\d+)',log)[1])
doc=r/'flprog_bridge/docs/ESP32_MODBUS_WEB_RU.md'
text=doc.read_text(encoding='utf-8-sig').split('\n## Компиляция ESP32')[0]
text+=f'\n## Компиляция ESP32\n\nCore 3.3.11, классическая ESP32: Flash {flash} байт, статическая RAM {ram} байт. Относительно Universal 0.8: Flash {flash-1186204:+} байт, RAM {ram-63008:+} байт. Это результат компоновщика, не измерение heap. BIN не прошивался.\n'
doc.write_text(text,encoding='utf-8')
esp=r/'flprog_bridge/esp32/FLProgBridgeEsp32'
for p in esp.glob('*.h'):
    built=w/'build/sketch'/p.name
    assert built.exists(),p.name
    s=re.sub(r'^#line[^\n]*\n','',built.read_text(encoding='utf-8-sig'))
    assert s.splitlines()==p.read_text(encoding='utf-8-sig').splitlines(),p.name
dep=(w/'build/libraries/FLProg_Network/flprogNetwork.cpp.d').read_text(errors='replace')
assert 'modbus_lan_bridge_20261029' in dep
build=json.loads((w/'BUILD.json').read_text(encoding='utf-8'))
build.update(version='0.9',service_modes=['raw','modbus_tcp'],default_ports=[3234,502],flashed=False,flash=flash,static_ram=ram)
(w/'BUILD.json').write_text(json.dumps(build,indent=2),encoding='utf-8')
checks=dict(software_only=True,flashed=False,git_changed=False,sdk_headers_match=True,private_r17_dependency=True,
    settings_three_networks_and_services=True,combined_runtime=True,tcp=json.loads((w/'TCP_CHECKS.json').read_text()),
    full_web=json.loads((w/'LAN_TRANSFER_CHECKS.json').read_text()),
    regressions=['http_read_client','http_read_routes','full_web_routes','command_typed_client','universal_config','modbus_lan'],
    gui_service_port_save_reboot=True,hardware_uart_lan_heap_tested=False)
(w/'CHECKS.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
dst=w/'ESP32_Universal_0.9_Modbus_Web_Prototype';dst.mkdir(exist_ok=True)
for source,target in [(esp,dst/'esp32/FLProgBridgeEsp32'),(r/'flprog_bridge/esp32/web',dst/'esp32/web'),(r/'flprog_bridge/firmware',dst/'firmware')]:
    shutil.copytree(source,target,dirs_exist_ok=True)
shutil.copytree(Path(r'E:\SAI\FLProg_Network\_work\modbus_lan_bridge_20261029\libraries\FLProg_Network'),dst/'libraries/FLProg_Network',dirs_exist_ok=True)
(dst/'bin').mkdir(exist_ok=True)
shutil.copy2(w/'build/FLProgBridgeEsp32.ino.bin',dst/'bin/ESP32_Universal_0.9_application_0x10000.bin')
for name in ['CHECKS.json','BUILD.json','BUILD.log','TCP_CHECKS.json','LAN_TRANSFER_CHECKS.json','MODBUS_SETTINGS.png']:
    shutil.copy2(w/name,dst/name)
shutil.copy2(r/'flprog_bridge/docs/ESP32_MODBUS_WEB_RU.md',dst/'README_RU.md')
(dst/'tests').mkdir(exist_ok=True)
for name in ['modbus_runtime_test','modbus_lan_test','lan_web_settings_test','universal_config_test','http_read_client_test','http_read_routes_test','full_web_routes_test','command_typed_client_test','modbus_tcp_native_server','lan_web_preview_peer']:
    shutil.copy2(w/(name+'.exe'),dst/'tests'/(name+'.exe'))
    shutil.copy2(r/'flprog_bridge/tests'/(name+'.cpp'),dst/'tests'/(name+'.cpp'))
for name in ['test_modbus_tcp_native.py','preview_lan_web.py','build_settings_page.py','build_project_viewer.py','lan_web_native_adapter.h','http_read_native_adapter.h']:
    shutil.copy2(r/'flprog_bridge/tests'/name,dst/'tests'/name)
files={p.relative_to(dst).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in dst.rglob('*') if p.is_file() and p.name!='SHA256.json'}
(dst/'SHA256.json').write_text(json.dumps(files,indent=2,ensure_ascii=False),encoding='utf-8')
z=w/(dst.name+'.zip')
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
    for p in dst.rglob('*'):
        if p.is_file():out.write(p,(Path(dst.name)/p.relative_to(dst)).as_posix())
with zipfile.ZipFile(z) as out:
    assert out.testzip() is None
    for name,sha in files.items():assert hashlib.sha256(out.read(dst.name+'/'+name)).hexdigest()==sha
report=dict(files=len(files),crc=True,sha256_all_files=True,zip_sha256=hashlib.sha256(z.read_bytes()).hexdigest(),flash=flash,static_ram=ram)
(w/'PACKAGE_VERIFIED.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
