# coding: utf-8
"""Stage the new profile before OTA. Never modifies an existing release."""
import hashlib,json,re,shutil,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_web_20261028')
U=W/'user4';H=Path(r'E:\SAI\FLProg_Network\_work\bridge_20261028\hardware')
M=R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER'
data=json.loads((W/'BUILD.json').read_text());prepared=json.loads((W/'PREPARED.json').read_text())
assert data['projectHash']==prepared['projectHash']
assert hashlib.sha256(Path(data['bin']).read_bytes()).hexdigest()==data['sha256']
assert hashlib.sha256(Path(data['source']).read_bytes()).hexdigest()==data['sourceSha256']
out=U/'Комплект';assert not out.exists(),'Candidate already exists'
out.mkdir()
manager=out/'Менеджер_прошивок';manager.mkdir()
shutil.copytree(H/'Комплект/Менеджер_прошивок/build_tools',manager/'build_tools',ignore=shutil.ignore_patterns('__pycache__','*.pyc','settings.json'))
shutil.copy2(R/'flprog_webui_next/tools/build_compatibility.py',manager/'build_tools/build_compatibility.py')
profiles=manager/'profiles';profiles.mkdir()
for folder in (H/'Комплект/Менеджер_прошивок/profiles').iterdir():
    if folder.is_dir() and json.loads((folder/'profile.json').read_text(encoding='utf-8')).get('loader_only'):
        shutil.copytree(folder,profiles/folder.name)
previous=H/'profiles/fle4d_30mt_profile_1_0_6'
profile=json.loads((previous/'profile.json').read_text(encoding='utf-8'))
profile.update(id='fle4d_30mt_profile_1_0_8',firmware_version=data['version'],label='FLE4D-30MT / STM32F407VG / W5500 — проект 4, DHCP + полный веб COM, 1.0.8',
 description='На основе 4/4.ino. DHCP от роутера. Полный веб через UART6 PC6/PC7 115200, отдельная программа моста. DO/AO доступны после включения режима управления; AO 0–10000 мВ. Консоль UART6 отключена. Ethernet WebUI и OTA сохранены.')
profile['artifacts']['application']['sha256']=data['sha256']
profile['validation']=dict(build_verified=True,application_hardware_verified=False,source_sketch='Проект_профиля/FLE4D_Profile_Bridge/FLE4D_Profile_Bridge.ino',
 source_sha256=hashlib.sha256(Path(data['sketch']).read_bytes()).hexdigest(),original_source='4/4.ino',original_source_sha256=data['sourceSha256'])
profile['bridge'].update(physical_output_commands=True,web_api=1,web_hash=data['projectHash'])
folder=profiles/profile['id'];folder.mkdir()
shutil.copy2(previous/'bootloader.bin',folder/'bootloader.bin');shutil.copy2(data['bin'],folder/'application.bin')
(folder/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pin={profile['id']:dict(firmware_version=data['version'],artifacts={k:v['sha256'] for k,v in profile['artifacts'].items()})}
policy=M/'profile_policy.py';text=policy.read_text(encoding='utf-8')
text,n=re.subn(r'^BUNDLED_PROFILES = .*$',lambda m:'BUNDLED_PROFILES = '+repr(pin),text,flags=re.M);assert n==1
policy.write_text(text,encoding='utf-8')
shutil.copytree(U/'exe/dist/FLProg_Bridge',out/'Мост_связи')
shutil.copytree(U/'editor_dist/FLProg_WebUI_Editor',out/'Редактор')
project=out/'Проект_профиля';project.mkdir()
shutil.copytree(Path(data['sketch']).parent,project/'FLE4D_Profile_Bridge')
shutil.copytree(U/'libraries',project/'libraries')
shutil.copytree(U/'site',project/'bridge_web')
shutil.copy2(Path(data['source']),project/'4_ORIGINAL.ino')
shutil.copy2(Path(r'E:\FLProg_Projects\FLE4D-30MT\FLE4D-30MT.flpui'),project/'FLE4D-30MT.flpui')
shutil.copytree(R/'flprog_webui_next/runtime/FLProg_WebUI',out/'Библиотека/FLProg_WebUI',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(R/'flprog_bridge',out/'Исходники/Мост_связи',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ('README_RU.md','PROTOCOL_RU.md','API_RU.md','CHECKS_RU.md','HARDWARE_RU.md','ROADMAP_RU.md','LICENSE_PYSERIAL.md'):
    shutil.copy2(R/'flprog_bridge'/name,out/'Мост_связи'/name)
shutil.copytree(R/'flprog_bridge/docs',out/'Мост_связи/docs')
shutil.copytree(R/'flprog_bridge/firmware',out/'Мост_связи/firmware')
(out/'ПРОЧИТАТЬ.md').write_text('# FLProg Network — локальный комплект полного веба COM\n\nМост_связи/FLProg_Bridge.exe; Редактор/FLProg_WebUI_Editor.exe; Менеджер_прошивок/FLProg_Firmware_Manager.exe.\n\nПрограмма профиля 1.0.8-BRIDGE-WEB получена из пользовательского 4/4.ino, Ethernet DHCP. Исходник 4 сохранён.\n\nПолный веб: Мост_связи/docs/FULL_WEB_RU.md. Результаты аппаратной проверки фиксируются отдельно. Это не опубликованный релиз; архив и GitHub не менялись.\n',encoding='utf-8')
(U/'PROFILE_READY.json').write_text(json.dumps(dict(folder=str(out),profile=str(folder),build=data,manager='0.8.0-preview.3',ready_before_ota=True),ensure_ascii=False,indent=2),encoding='utf-8')
print(str(out))
