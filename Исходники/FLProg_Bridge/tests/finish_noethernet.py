# coding: utf-8
"""Create a new local verified copy without stopping or replacing running apps."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];B=Path(r'E:\SAI\FLProg_Network');U=B/'_work/bridge_web_20261028/user4'
old=U/'Комплект';out=U/'Комплект_проверен_без_Ethernet'
assert not out.exists(),'Never overwrite an existing verified folder'
shutil.copytree(old,out)
shutil.copytree(U/'manager_dist/FLProg_Firmware_Manager',out/'Менеджер_прошивок',dirs_exist_ok=True)
shutil.copytree(R/'flprog_bridge',out/'Исходники/Мост_связи',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copy2(R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER/profile_policy.py',out/'Исходники/Менеджер_прошивок/profile_policy.py')
profile=out/'Менеджер_прошивок/profiles/fle4d_30mt_profile_1_0_8/profile.json'
data=json.loads(profile.read_text(encoding='utf-8'));assert data['validation']['ethernet_unplug_verified']
assert hashlib.sha256(profile.with_name('application.bin').read_bytes()).hexdigest()==data['artifacts']['application']['sha256']
shutil.copy2(U/'WEB_NO_ETHERNET.png',out/'Проверки/WEB_NO_ETHERNET.png')
manifest={f.relative_to(out).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file() and f.name!='MANIFEST_SHA256.json'}
(out/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
final=U/'FINAL.json';d=json.loads(final.read_text(encoding='utf-8'));d.update(folder=str(out),files=len(manifest),ethernet_unplug_test=True,running_apps_replaced=False);final.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
ready=U/'PROFILE_READY.json';d=json.loads(ready.read_text(encoding='utf-8'));d.update(folder=str(out),profile=str(profile.parent));ready.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
(B/'CURRENT_PREVIEW.md').write_text('# Проверенный локальный комплект\n\nПолный веб COM0.2.0, FLE4D1.0.8, Менеджер0.8.0-preview.3.\n\nПапка: `_work\\bridge_web_20261028\\user4\\Комплект_проверен_без_Ethernet`.\nПроверки: `_work\\bridge_web_20261028\\user4\\ПРОВЕРКИ.md`.\n\nEthernet физически отключён: четыре страницы, чтения и RAM-команда через COM проверены. Пользовательские DO/AO сохранены; reset без Ethernet не выполнялся.\n\nЗапущенные приложения не заменялись. Опубликованный релиз по-прежнему указан в CURRENT_RELEASE.md; архив и GitHub не менялись.\n',encoding='utf-8')
note='\nПосле проверки без Ethernet обновлённый EXE менеджера сохранён в новом\nкомплекте _work/bridge_web_20261028/user4/Комплект_проверен_без_Ethernet.\nАвтоматическая проверка отклонила остановку запущенного менеджера, поэтому\nработающие приложения оставлены без замены. CURRENT_PREVIEW.md указывает новый комплект.\n'
for path in (B/'AGENTS.md',Path(r'E:\SAI\Правила для Codex\Проекты\FLProg_Network.md'),U.parent/'ACTIVE_TASK.md'):
    with path.open('a',encoding='utf-8') as f:f.write(note)
print(json.dumps(dict(folder=str(out),files=len(manifest),ethernet_unplug_verified=True,running_apps_unchanged=True),ensure_ascii=False))
