# coding: utf-8
from pathlib import Path
import json,re,shutil
R=Path(__file__).resolve().parents[2];W=Path(r'E:\SAI\FLProg_Network\_work\bridge_web_20261028');U=W/'user4';out=U/'Комплект'
report=json.loads((U/'NO_ETHERNET.json').read_text(encoding='utf-8'))
assert report['user_confirmed_ethernet_unplugged'] and report['echo']['value']==53002
assert report['bad_frames']==0 and not report['physical_outputs_written']
addition='''
## Проверка с отключённым Ethernet

Пользователь физически отключил Ethernet, оставив USB/ST-Link и питание.
ПЛК через COM подтвердил network_ready=false, IP/шлюз/маску0.0.0.0.
Все четыре страницы прочитаны, десять последовательных чтений продолжили
обновлять данные и время работы. RAM-команда241=53002 принята, echo242=53002,
счётчик243 увеличился ровно на1. Ошибок кадров0, сеанс оставался действующим.
Режим управления и DO1 уже были включены пользователем, web_control_ready=true
сохранялся без Ethernet. Физические DO/AO не записывались и режим не менялся.
Повторный reset без Ethernet не выполнялся, чтобы не прерывать управление
пользователя. Ранее reset/reconnect был проверен отдельно с подключённой сетью.
Доказательства: NO_ETHERNET.json и WEB_NO_ETHERNET.png.
'''
for path in (R/'flprog_bridge/docs/FULL_WEB_CHECKS_RU.md',U/'ПРОВЕРКИ.md',out/'ПРОВЕРКИ_FLE4D.md'):
    text=path.read_text(encoding='utf-8').replace('Физическое отключение Ethernet пока ожидается от пользователя. Длительная','Работа при физически отключённом Ethernet подтверждена (см. ниже). Длительная')
    if '## Проверка с отключённым Ethernet' not in text:text+=addition
    path.write_text(text,encoding='utf-8')
p=R/'flprog_bridge/README_RU.md';text=p.read_text(encoding='utf-8')
text=text.replace('Измерение напряжения на клеммах и физическое отключение Ethernet пока отдельно\nне подтверждены.','Полный веб и программная команда проверены при физически отключённом Ethernet;\nнапряжение на клеммах не измерялось.')
p.write_text(text,encoding='utf-8')
p=R/'flprog_bridge/ROADMAP_RU.md';text=p.read_text(encoding='utf-8').replace('Ожидается физическое отключение кабеля пользователем; не выдавать за проверенное','Проверено: Ethernet отключён физически, 4 страницы, RAM-команда, чтения без ошибок; пользовательские DO/AO не менялись');p.write_text(text,encoding='utf-8')
p=R/'flprog_webui_next/ROADMAP_RU.md';text=p.read_text(encoding='utf-8').replace('Физическая проверка без Ethernet ожидается.','Физическая проверка без Ethernet пройдена: 4 страницы и RAM-команда через COM.');p.write_text(text,encoding='utf-8')
profile=out/'Менеджер_прошивок/profiles/fle4d_30mt_profile_1_0_8/profile.json';data=json.loads(profile.read_text(encoding='utf-8'))
scope=data['validation']['hardware_scope'].replace('Без кабеля Ethernet пока не проверено.','Веб и RAM-команда проверены без Ethernet.')
data['validation'].update(hardware_scope=scope,ethernet_unplug_verified=True)
profile.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
policy=R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER/profile_policy.py';ns={};exec(policy.read_text(encoding='utf-8'),ns)
pins=ns['BUNDLED_PROFILES'];pins[data['id']]['hardware_scope']=scope
text,n=re.subn(r'^BUNDLED_PROFILES = .*$',lambda m:'BUNDLED_PROFILES = '+repr(pins),policy.read_text(encoding='utf-8'),flags=re.M);assert n==1;policy.write_text(text,encoding='utf-8')
final=U/'FINAL.json';data=json.loads(final.read_text(encoding='utf-8'));data['ethernet_unplug_test']=True;final.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ('NO_ETHERNET.json','NO_ETHERNET.log','WEB_NO_ETHERNET.png'):shutil.copy2(U/name,out/'Проверки'/name)
for name in ('README_RU.md','ROADMAP_RU.md'):shutil.copy2(R/'flprog_bridge'/name,out/'Мост_связи'/name)
shutil.copytree(R/'flprog_bridge/docs',out/'Мост_связи/docs',dirs_exist_ok=True)
shutil.copy2(R/'flprog_webui_next/ROADMAP_RU.md',out/'Редактор/ДОРОЖНАЯ_КАРТА.md')
note='''
28.10.2026 — пользователь подтвердил физическое отключение Ethernet при
подключённых USB и питании. COM-веб64016 работает: network_ready=false,
IP0.0.0.0, 4 страницы, 10 чтений, RAM241=53002→242=53002/count+1, badFrames0.
У пользователя уже были включены web_control и DO1: их не меняли, reset
без Ethernet не выполняли. Доказательства user4/NO_ETHERNET.json и WEB_NO_ETHERNET.png.
Ожидание физического кабеля закрыто; профиль и дорожная карта обновлены.
Git/архив/BIN не менялись. Повторять аппаратные команды для этой проверки не нужно.
'''
for p in (Path(r'E:\SAI\FLProg_Network\AGENTS.md'),Path(r'E:\SAI\Правила для Codex\Проекты\FLProg_Network.md')):
    with p.open('a',encoding='utf-8') as f:f.write(note)
p=W/'ACTIVE_TASK.md';text=p.read_text(encoding='utf-8');text=text.replace('**Единственная ожидающая аппаратная проверка:** физически отключить Ethernet.','**Закрыто:** проверка без Ethernet пройдена; актуально дополнение ниже.\n\nИстория ожидания: физически отключить Ethernet.');text+=note;p.write_text(text,encoding='utf-8')
print('Recorded physical Ethernet-unplug verification. No firmware changes.')
