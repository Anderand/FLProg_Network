# coding: utf-8
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[2];B=Path(r'E:\SAI\FLProg_Network');W=B/'_work/bridge_flash_20261028'
base=B/'releases/FLProg_Network_Manager_Bridge_2026-10-28_v1'
data=json.loads((W/'BUILD.json').read_text(encoding='utf-8'));out=W/'Комплект';assert not out.exists();out.mkdir()
manager=out/'Менеджер_прошивок';manager.mkdir()
shutil.copytree(base/'Менеджер_прошивок/build_tools',manager/'build_tools',ignore=shutil.ignore_patterns('__pycache__','*.pyc','settings.json'))
shutil.copy2(R/'flprog_webui_next/tools/build_compatibility.py',manager/'build_tools/build_compatibility.py')
profiles=manager/'profiles';profiles.mkdir()
for folder in (base/'Менеджер_прошивок/profiles').iterdir():
    if folder.is_dir() and json.loads((folder/'profile.json').read_text(encoding='utf-8')).get('loader_only'):shutil.copytree(folder,profiles/folder.name)
old=base/'Менеджер_прошивок/profiles/fle4d_30mt_profile_1_0_8';profile=json.loads((old/'profile.json').read_text(encoding='utf-8'))
profile.update(id='fle4d_30mt_profile_1_0_9_flash',firmware_version=data['version'],label='FLE4D-30MT / STM32F407VG / W5500 — веб из Flash по COM, 1.0.9',description='Основа: проект4, DHCP. UART6 PC6/PC7 115200. Полный веб получает мост0.3.0 с ПЛК; папка сайта на PC не требуется. Проверка SHA-256, кеш; OTA сохраняет загрузчик.')
profile['artifacts']['application']['sha256']=data['sha256']
profile['validation']=dict(build_verified=True,application_hardware_verified=False,source_sketch='Проект_профиля/FLE4D_Bridge_Flash/FLE4D_Bridge_Flash.ino',source_sha256=hashlib.sha256(Path(data['sketch']).read_bytes()).hexdigest(),original_source='4/4.ino',original_source_sha256=data['base_source_sha256'])
profile['bridge'].update(web_hash=data['projectHash'],resource_service=4,resource_api=1,resources_from_flash=True)
folder=profiles/profile['id'];folder.mkdir();shutil.copy2(old/'bootloader.bin',folder/'bootloader.bin');shutil.copy2(data['bin'],folder/'application.bin')
assert hashlib.sha256((folder/'application.bin').read_bytes()).hexdigest()==data['sha256']
(folder/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pins={profile['id']:dict(firmware_version=data['version'],artifacts={key:value['sha256'] for key,value in profile['artifacts'].items()})}
policy=R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER/profile_policy.py';text,n=re.subn(r'^BUNDLED_PROFILES = .*$',lambda m:'BUNDLED_PROFILES = '+repr(pins),policy.read_text(encoding='utf-8'),flags=re.M);assert n==1;policy.write_text(text,encoding='utf-8')
shutil.copytree(W/'bridge_final_dist/FLProg_Bridge',out/'Мост_связи')
shutil.copytree(W/'editor_dist/FLProg_WebUI_Editor',out/'Редактор')
project=out/'Проект_профиля';project.mkdir();shutil.copytree(Path(data['sketch']).parent,project/'FLE4D_Bridge_Flash')
shutil.copytree(W/'libraries',project/'libraries');shutil.copy2(Path(r'E:\FLProg_Projects\FLE4D-30MT\FLE4D-30MT.flpui'),project/'FLE4D-30MT.flpui')
# Developer-only generated source; not the conventional local fallback directory.
shutil.copytree(W/'generated_site',out/'Исходники/Веб_в_Flash')
shutil.copy2(Path(data['base_source']),project/'4_ORIGINAL.ino')
(W/'PROFILE_READY.json').write_text(json.dumps(dict(folder=str(out),profile=str(folder),version=data['version'],application_sha256=data['sha256'],ready_before_ota=True),ensure_ascii=False,indent=2),encoding='utf-8')
print(str(out))
