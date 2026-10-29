# coding: utf-8
"""Install the hardware-tested DHCP/UART6 profile into a new local candidate."""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[2];W=Path(r'E:\SAI\FLProg_Network\_work\bridge_20261028\hardware');P=Path(r'E:\FLProg_Projects\FLE4D-30MT')
base=Path(r'E:\SAI\FLProg_Network\_work\bridge_20261028\Комплект')
smoke=json.loads((W/'COM_HARDWARE.json').read_text(encoding='utf-8'))
reset=json.loads((W/'RESTART_HARDWARE.json').read_text(encoding='utf-8'))
assert smoke['hardware_tested'] and reset['old_session_rejected'] and reset['staged_bytes']>0
build=json.loads((W/'bridge_BUILD.json').read_text(encoding='utf-8'))
source=Path(build['sketch']);blob=Path(build['bin']).read_bytes();assert hashlib.sha256(blob).hexdigest()==build['sha256']
old=base/'Менеджер_прошивок/profiles/fle4d_30mt_profile_1_0_4'
pid='fle4d_30mt_profile_1_0_6';profile=json.loads((old/'profile.json').read_text(encoding='utf-8'))
profile.update(id=pid,firmware_version='1.0.6-BRIDGE',
 label='FLE4D-30MT / STM32F407VG / W5500 — DHCP + мост UART6, 1.0.6',
 description='DHCP: IP, маска, шлюз и DNS от роутера. UART6 PC6/PC7 115200 выделен мосту; консоль и Modbus RTU на UART6 отключены. Другие UART, WebUI и OTA сохранены. COM: реальные каналы читаются; запись только в программный echo 241, физические DO/AO запрещены.',
 network=dict(mode='dhcp',static_ip=None,gateway=None,dns=None),
 bridge=dict(protocol=1,uart=6,tx='PC6',rx='PC7',baud=115200,services=['webui'],physical_output_commands=False),
 validation=dict(build_verified=True,application_hardware_verified=True,
 hardware_scope='FLE4D-30MT: COM/UART6, чтение I/O, программная команда, DHCP, HTTP и повторная OTA с автосбросом; физические DO/AO не переключались.',
 source_sketch='FLE4D_30MT_Profile/FLE4D_30MT_Profile.ino',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
profile['artifacts']['application']['sha256']=build['sha256']
target=W/'profiles'/pid;target.mkdir(parents=True,exist_ok=True)
(target/'application.bin').write_bytes(blob);shutil.copy2(old/'bootloader.bin',target/'bootloader.bin')
(target/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
policy=R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER/profile_policy.py'
pin={pid:dict(firmware_version=profile['firmware_version'],artifacts={key:row['sha256'] for key,row in profile['artifacts'].items()},hardware_scope=profile['validation']['hardware_scope'])}
text=policy.read_text(encoding='utf-8');text,n=re.subn(r'^BUNDLED_PROFILES = .*$',lambda m:'BUNDLED_PROFILES = '+repr(pin),text,flags=re.M);assert n==1
policy.write_text(text,encoding='utf-8')
# Preserve current project inputs before replacing only this project's sources.
history=W/'project_before_bridge';history.mkdir(exist_ok=True)
for name in ['FLE4D_30MT_Profile','FLE4D-30MT.flpui','ПРОЕКТ.md']:
    src=P/name;dst=history/name
    if not dst.exists():
        if src.is_dir():shutil.copytree(src,dst)
        else:shutil.copy2(src,dst)
for name in ['FLProg_WebUI','FLProg_WebUI_Project_FLE4D-30MT']:
    dst=history/'libraries'/name
    if not dst.exists():shutil.copytree(P/'libraries'/name,dst)
    shutil.copytree(W/'libraries'/name,P/'libraries'/name,dirs_exist_ok=True)
shutil.copy2(source,P/'FLE4D_30MT_Profile/FLE4D_30MT_Profile.ino')
for f in source.parent.glob('*.h'):shutil.copy2(f,P/'FLE4D_30MT_Profile'/f.name)
project=json.loads((W/'FLE4D-30MT_bridge.flpui').read_text(encoding='utf-8'));project['projectFolder']=str(P)
(P/'FLE4D-30MT.flpui').write_text(json.dumps(project,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
version_dir=P/'firmware/1.0.6-BRIDGE';version_dir.mkdir(exist_ok=True)
shutil.copy2(target/'application.bin',version_dir/'FLE4D_30MT_PROFILE_1.0.6_BRIDGE.bin')
metadata=dict(build,bin=str(version_dir/'FLE4D_30MT_PROFILE_1.0.6_BRIDGE.bin'),hardware_tested=True,flashed=True,
 ip=smoke['ip'],network='DHCP',uart6='bridge only',physical_output_commands=False)
(version_dir/'BUILD_RESULT.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['COM_HARDWARE.json','RESTART_HARDWARE.json','BACKUP.json']:
    shutil.copy2(W/name,version_dir/name)
(P/'ПРОЕКТ.md').write_text('''# FLE4D-30MT — программа профиля 1.0.6-BRIDGE

Основа: скетч пользователя 3 с прежними WebUI/диагностикой/I/O и OTA.
Ethernet **DHCP**, без привязки к подсети. Адрес при проверке: 192.168.100.19,
он может измениться в другой сети. MAC пока сохранён из проекта; для нескольких
ПЛК одновременно требуются уникальные MAC.

UART6 PC6/PC7, 115200 выделен FLProg Bridge. По указанию пользователя исключены
консоль и Modbus RTU на UART6. Остальные UART и алгоритмы I/O сохранены.
COM позволяет читать системные каналы и реальные входы/выходы; команды DO/AO
запрещены политикой моста. Программные каналы 241→242 и счётчик243 нужны для
проверки доставки без переключения физических выходов.

Скетч: FLE4D_30MT_Profile/FLE4D_30MT_Profile.ino и два локальных заголовка моста.
Макет: FLE4D-30MT.flpui; библиотеки проекта: libraries. Заголовок descriptor
пересобран штатным генератором с паспортом совместимости. Установка в IDE не нужна.
BIN: firmware/1.0.6-BRIDGE/FLE4D_30MT_PROFILE_1.0.6_BRIDGE.bin, адрес0x08010000.

На FLE4D проверены COM5/UART6, чтение I/O, RAM-команда, DHCP, HTTP, OTA и автосброс.
Область загрузчика сохранена. Физические DO/AO при испытании не переключались.
Полный макет через COM и UART-блоки Basic/Professional ещё не реализованы;
пока используется отдельная сервисная страница моста и HTTP API каналов.

Исходные 1/2/3 и старые firmware сохранены. Перед правками создана копия проекта
в E:/SAI/FLProg_Network/_work/bridge_20261028/hardware/project_before_bridge.
Генерация .ino заново из исходного .flp вернёт его старые настройки: перенесите
DHCP и исключение UART6 либо используйте этот подготовленный скетч.
''',encoding='utf-8')
print('New tested profile:',target)
