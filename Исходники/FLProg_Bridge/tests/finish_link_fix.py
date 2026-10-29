from pathlib import Path
import json,hashlib,subprocess,shutil,difflib
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028');old=Path(r'E:\SAI\FLProg_Network\_work\bridge_flash_20261028')
a=subprocess.run([str(w/'link_test_before.exe')],capture_output=True);b=subprocess.run([str(w/'link_test.exe')],capture_output=True);assert a.returncode!=0 and b.returncode==0
(w/'HOST_TESTS.json').write_text(json.dumps(dict(old_return_code=a.returncode,old_error=a.stderr.decode(errors='replace'),new_return_code=b.returncode,new_result=b.stdout.decode(),test_scope='Exact production function with fake hardware and controlled millis'),indent=2),encoding='utf-8')
p=w/'Менеджер_прошивок/profiles/fle4d_30mt_profile_1_0_10_link/profile.json';d=json.loads(p.read_text(encoding='utf-8'));d['validation']['application_hardware_verified']=True;d['description']='Проект4, DHCP. Веб из Flash по UART6 PC6/PC7. Проверены потеря кабеля (40 чтений false), возврат без reset (true), UART веб без Ethernet, четыре HTTP страницы и OTA после возврата. Загрузчик сохранён.';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
data=json.loads((w/'BUILD.json').read_text(encoding='utf-8'));data['hardware_tested']=True;(w/'BUILD.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
assert hashlib.sha256(Path(data['base_source']).read_bytes()).hexdigest()==data['base_source_sha256']
first=(old/'libraries/FLProg_Network/src/flprogNetwork.cpp').read_text(encoding='utf-8').splitlines(True);last=(w/'libraries/FLProg_Network/src/flprogNetwork.cpp').read_text(encoding='utf-8').splitlines(True)
(w/'ethernet_link.patch').write_text(''.join(difflib.unified_diff(first,last,fromfile='a/src/flprogNetwork.cpp',tofile='b/src/flprogNetwork.cpp')),encoding='utf-8')
summary='''

## Итог испытаний

Установка1.0.10-BRIDGE-LINK поOTA, MAC78:AC:C0:5C:44:8D. При отключённом Ethernet40 чтений ready=false; веб изFlash поUART передан без ошибок за2,234с. После возврата кабеля без reset ready=true, IP192.168.100.19; подтверждены версияOTA и страницы main/diagnostics/inputs/outputs. Загрузчик64КиБ совпадает до/после. Физические выходы не переключались. Flash366556 (-16), staticRAM51644 (без роста), BIN367064. Менеджер0.8.0-preview.7 подготовлен с точным профилем доOTA; открытый пользователем preview.6 не заменён. Профиль отмечен аппаратно проверенным в указанном объёме. Копии в IDE и пользовательский raw4 не менялись; исправленный снимок — libraries этой рабочей папки. Готовые архивы и GitHub не изменены.
'''
p=w/'README_RU.md';p.write_text(p.read_text(encoding='utf-8-sig')+summary,encoding='utf-8');shutil.copy2(p,r/'flprog_bridge/docs/ETHERNET_LINK_RU.md')
for target in [Path(r'E:\SAI\Правила для Codex\Проекты\FLProg_Network.md'),Path(r'E:\SAI\FLProg_Network\AGENTS.md')]:
 with target.open('a',encoding='utf-8') as f:f.write(summary)
with (r/'flprog_bridge/ROADMAP_RU.md').open('a',encoding='utf-8') as f:f.write('\n28.10.2026: исправление DHCP/link завершено аппаратно на1.0.10: off40/40false, возвратtrueбезreset, четыреHTTPстраницы/OTA/UARTresourcesPASS. См. docs/ETHERNET_LINK_RU.md.\n')
(w/'CURRENT.md').write_text('# Проверенная рабочая сборка\n\n1.0.10-BRIDGE-LINK, менеджер0.8.0-preview.7.\n[Отчёт](README_RU.md)\n\nНе опубликованный релиз. Ранее открытый менеджер0.8.0-preview.6 остаётся со своим прежним профилем1.0.9. Для новой версии используйте Менеджер_прошивок в этой папке.\n',encoding='utf-8')
print('Saved hardware results, source patch, profile and documentation')
