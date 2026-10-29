from pathlib import Path
import json,shutil,re,hashlib
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028');old=Path(r'E:\SAI\FLProg_Network\_work\bridge_flash_20261028\Комплект\Менеджер_прошивок')
d=json.loads((w/'BUILD.json').read_text(encoding='utf-8'));out=w/'Менеджер_прошивок';out.mkdir(exist_ok=True)
shutil.copytree(old/'build_tools',out/'build_tools',dirs_exist_ok=True,ignore=shutil.ignore_patterns('settings.json','__pycache__','*.pyc'))
profiles=out/'profiles';profiles.mkdir(exist_ok=True)
for f in (old/'profiles').iterdir():
 if f.is_dir() and json.loads((f/'profile.json').read_text(encoding='utf-8-sig')).get('loader_only'):shutil.copytree(f,profiles/f.name,dirs_exist_ok=True)
base=old/'profiles/fle4d_30mt_profile_1_0_9_flash';row=json.loads((base/'profile.json').read_text(encoding='utf-8-sig'))
row.update(id='fle4d_30mt_profile_1_0_10_link',firmware_version=d['version'],label='FLE4D-30MT / STM32F407VG / W5500 — исправление Ethernet, 1.0.10',description='Проект4, DHCP. Веб из Flash по UART6 PC6/PC7. Исправлена готовность Ethernet при отключённом кабеле. Аппаратная проверка кандидата выполняется отдельно.')
row['artifacts']['application']['sha256']=d['sha256'];row['validation']['application_hardware_verified']=False;row['validation']['source_sketch']=str(d['sketch']);row['validation']['source_sha256']=hashlib.sha256(Path(d['sketch']).read_bytes()).hexdigest()
f=profiles/row['id'];f.mkdir(exist_ok=True);shutil.copy2(base/'bootloader.bin',f/'bootloader.bin');shutil.copy2(d['bin'],f/'application.bin');(f/'profile.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
m=r/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER';p=m/'profile_policy.py';s=p.read_text(encoding='utf-8');pins={row['id']:dict(firmware_version=d['version'],artifacts={k:v['sha256'] for k,v in row['artifacts'].items()})};s=re.sub(r'^BUNDLED_PROFILES = .*$',lambda _: 'BUNDLED_PROFILES = '+repr(pins),s,flags=re.M);p.write_text(s,encoding='utf-8')
p=m/'flprog_stm32_ota_manager.py';p.write_text(p.read_text(encoding='utf-8').replace('0.8.0-preview.6','0.8.0-preview.7'),encoding='utf-8')
(w/'PROFILE_READY.json').write_text(json.dumps(dict(folder=str(w),profile=str(f),version=d['version'],application_sha256=d['sha256'],ready_before_ota=True),ensure_ascii=False,indent=2),encoding='utf-8')
print(d['bytes'],d['sha256'])
