# coding: utf-8
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2]
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_web_20261028');U=W/'user4';out=U/'Комплект';B=Path(r'E:\SAI\FLProg_Network')
for name in ('README_RU.md','PROTOCOL_RU.md','API_RU.md','CHECKS_RU.md','HARDWARE_RU.md','ROADMAP_RU.md','LICENSE_PYSERIAL.md'):
    shutil.copy2(R/'flprog_bridge'/name,out/'Мост_связи'/name)
shutil.copy2(R/'flprog_bridge/MANAGER_RU.md',out/'Менеджер_прошивок/README_RU.md')
shutil.copytree(R/'flprog_bridge',out/'Исходники/Мост_связи',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copy2(R/'flprog_webui_next/ROADMAP_RU.md',out/'Редактор/ДОРОЖНАЯ_КАРТА.md')
manager_src=out/'Исходники/Менеджер_прошивок';manager_src.mkdir(exist_ok=True)
for name in ('flprog_stm32_ota_manager.py','profile_policy.py'):
    shutil.copy2(R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER'/name,manager_src/name)
b=json.loads((W/'BUILD.json').read_text());assert hashlib.sha256(Path(b['source']).read_bytes()).hexdigest()==b['sourceSha256']
profile=out/'Менеджер_прошивок/profiles/fle4d_30mt_profile_1_0_8/profile.json';p=json.loads(profile.read_text(encoding='utf-8'))
assert p['validation']['application_hardware_verified'] and p['network']['mode']=='dhcp'
assert hashlib.sha256(profile.with_name('application.bin').read_bytes()).hexdigest()==b['sha256']
site=json.loads((out/'Проект_профиля/bridge_web/bridge.json').read_text(encoding='utf-8'))
assert site['projectHash']==p['bridge']['web_hash']==b['projectHash']
for path in ('Мост_связи/FLProg_Bridge.exe','Редактор/FLProg_WebUI_Editor.exe','Менеджер_прошивок/FLProg_Firmware_Manager.exe'):
    assert (out/path).is_file()
manifest={f.relative_to(out).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file() and f.name!='MANIFEST_SHA256.json'}
(out/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(U/'FINAL.json').write_text(json.dumps(dict(folder=str(out),files=len(manifest),version=b['version'],bin_sha256=b['sha256'],web_hash=b['projectHash'],source4_sha256=b['sourceSha256'],hardware_tested=True,ethernet_unplug_test=False,git_updated=False,archive_built=False),ensure_ascii=False,indent=2),encoding='utf-8')
note='''
28.10.2026 — полный веб COM 0.2.0 проверен на FLE4D. По просьбе пользователя
сборка теперь основана на E:/FLProg_Projects/FLE4D-30MT/4/4.ino; raw4 не менялся.
DHCP сохранён; UART6 PC6/PC7 115200 выделен мосту, консоль UART6 отключена.
Менеджер 0.8.0-preview.3 с новым проектом и BIN 1.0.8-BRIDGE-WEB был готов
и проверен в GUI ДО OTA. BIN351232, SHA4c4763e1c9b2179037567b12d241750a7453b069f2f8afb899cb877ac5080176.
Flash350724/RAM51628. UI SHA ca252bd0b928fbc18f53c21e4770d5d53c29512d4b31ac40784d5ef55216aee3.
Через COM проверены 4 страницы, подтверждения, DO1/AO0 по регистрам GPIO/DAC,
возврат штатной логике, reset/reconnect 1.203с без повтора команд. Старый session
отвергнут HTTP409. Напряжение на клеммах не измеряли. Загрузочные64КиБ сохранены:
SHA4ed69ac7fbb577cc80899ebeb4b3cda80fda9c7ba29e7ef058988341cf325c57.
Исправлены слипшиеся подписи/значения: root-inline CSS включён в экспорт и
предпросмотр перед app.css, добавлены gap/padding/wrap. Есть реальный скрин
WEB_COM_FIXED.png и проверка360px. 20 C++/Python, 8 Web, 100 редакторских тестов OK.
Профиль fle4d_30mt_profile_1_0_8 и три EXE находятся в
_work/bridge_web_20261028/user4/Комплект. Текущий COM-веб:127.0.0.1:64016.
Рабочий P-скетч, libraries/site/firmware обновлены; исходный4 сохранён.
Физическое отключение Ethernet ожидается от пользователя, не заявлять проверенным.
Отчёт: flprog_bridge/docs/FULL_WEB_CHECKS_RU.md. Git/архив/IDE/r16 не менялись.
'''
for path in (B/'AGENTS.md',Path(r'E:\SAI\Правила для Codex\Проекты\FLProg_Network.md')):
    with path.open('a',encoding='utf-8') as f:f.write(note)
(B/'CURRENT_PREVIEW.md').write_text('# Локальная предварительная версия\n\nПолный веб COM0.2.0, FLE4D1.0.8, Менеджер0.8.0-preview.3.\n\nПапка: `_work\\bridge_web_20261028\\user4\\Комплект`.\nПроверки: `_work\\bridge_web_20261028\\user4\\ПРОВЕРКИ.md`.\n\nОпубликованный релиз по-прежнему указан в CURRENT_RELEASE.md. Этот комплект не опубликован и не заархивирован.\n',encoding='utf-8')
print(json.dumps(dict(folder=str(out),files=len(manifest)),ensure_ascii=False))
