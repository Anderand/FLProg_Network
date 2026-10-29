# coding: utf-8
from pathlib import Path
import json,re,subprocess,hashlib,shutil
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\uart_blocks_20261028')
data=json.loads((w/'BUILD.json').read_text(encoding='utf-8'));assert data['version']=='1.0.11-BRIDGE-BLOCK' and not data['hardware_tested']
log=(w/'build_tools/logs/FLProg_FLE4D_30MT_application.log').read_text(encoding='utf-8',errors='replace')
flash=int(re.search(r'Sketch uses (\d+) bytes',log)[1]);ram=int(re.search(r'Global variables use (\d+) bytes',log)[1]);assert 'flprogBridgeUserBlocks' not in '\n'.join(line for line in log.splitlines() if 'error:' in line)
run=subprocess.run([str(w/'uart_block_test.exe')],capture_output=True,check=True)
report=dict(flash=flash,static_ram=ram,previous_flash=366556,previous_static_ram=51644,flash_delta=flash-366556,static_ram_delta=ram-51644,application_sha256=data['sha256'],application_bytes=data['bytes'],hardware_tested=False,installed_firmware_unchanged='1.0.10-BRIDGE-LINK',native_transport_result=run.stdout.decode(),basic_professional=json.loads((w/'UBI_CHECKS.json').read_text(encoding='utf-8')))
(w/'CHECKS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
text='''# UART-блоки FLProg Bridge v0.1

Подготовлены Basic и Professional с общей логикой управления свободным UART. Файлы: Блоки_FLProg/Bridge_UART. Для использования нужна согласованная FLProg_WebUI из libraries. Штатные библиотеки не менялись.

Это блок транспорта, а не автоматическая привязка веб-проекта по ID: нужен настроенный Server и FLPROG_BRIDGE_SERVER. Импорт UBI в живой редактор FLProg и аппаратное испытание блока ещё не выполнялись. ПЛК оставлен на проверенной1.0.10; контрольный BIN1.0.11 не установлен и не помещён в профиль менеджера.

Проверены уникальныеID и обратныеXML-ссылки; восстановленный код обоих форматов одинаков; оба варианта скомпилированы и исполнены на нативном стенде. РеальныйC++helper проходит владениеUART, ошибкипараметров/запуска, порционныеRX/TX, HELLO, таймаут,TXbackpressure,disable/resetсеанса иошибкикадров.3ресурсных тестаPASS.

Полный проектFLE4D с реальнымRT_HW и STM32core3.0.0 собран: Flash {flash} ({fd:+d}), staticRAM {ram} ({rd:+d}) байт относительно1.0.10. BIN {size} байт, SHA256 {sha}. Проверены адресприложения0x08010000, векторы истрокаверсии. Это успешнаясборка, неаппаратноеиспытание.

Автоматическаяпривязкамодели/службпроектакблоку — следующийэтап. ГотовыеEXE/архивы/Git не менялись.
'''.format(flash=flash,fd=flash-366556,ram=ram,rd=ram-51644,size=data['bytes'],sha=data['sha256'])
(w/'README_RU.md').write_text(text,encoding='utf-8')
guide=r/'flprog_bridge/docs/UART_BLOCKS_RU.md'
with guide.open('a',encoding='utf-8') as f:f.write('\n## Контрольная сборка F407\n\nFlash {} ({:+d}), staticRAM {} ({:+d}) байт к1.0.10; BIN{} байт. SHA256 `{}`. BIN1.0.11-BRIDGE-BLOCK не прошит. Подробности: CHECKS.json рабочей папки.\n'.format(flash,flash-366556,ram,ram-51644,data['bytes'],data['sha256']))
shutil.copy2(guide,w/'Блоки_FLProg/Bridge_UART/README_RU.md')
for target in [r/'flprog_bridge/ROADMAP_RU.md',Path(r'E:\SAI\Правила для Codex\Проекты\FLProg_Network.md'),Path(r'E:\SAI\FLProg_Network\AGENTS.md')]:
 with target.open('a',encoding='utf-8') as f:f.write('\nUARTv0.1: сборкаF407 завершена, Flash{} ({:+d}),RAM{} ({:+d}), BIN{} SHA{}. _work/uart_blocks_20261028/CHECKS.json. Контрольная1.0.11непрошита, ПЛК1.0.10. Basic/ProXMLиэквивалентныйкод/нативныевызовыPASS;3resourceтестаPASS. Живойимпорт/аппаратныйблокиавтосвязкапроектаещёвпереди. Git/EXE/архивынеменялись.\n'.format(flash,flash-366556,ram,ram-51644,data['bytes'],data['sha256']))
print(json.dumps(report,ensure_ascii=False))
