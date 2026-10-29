# coding: utf-8
import hashlib,json,re,shutil,urllib.parse,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent.parent;B=Path(r'E:\SAI\FLProg_Network');U=B/'_work/bridge_web_20261028/user4'
info=json.loads((U/'SERIAL_TRANSFER_READY.json').read_text(encoding='utf-8'));out=Path(info['folder']);archive=out.parent/(out.name+'.zip');assert not archive.exists()
shutil.copy2(U/'SERIAL_MANAGER_UI.png',out/'Проверки/SERIAL_MANAGER_UI.png')
shutil.copy2(U/'SERIAL_MANAGER_REGRESSION.log',out/'Проверки/SERIAL_MANAGER_REGRESSION.log')
shutil.copy2(R/'flprog_bridge/LICENSE_PYSERIAL.md',out/'Менеджер_прошивок/LICENSE_PYSERIAL.md')
missing=[]
for p in [out/'Инструкция.md',out/'ПРОЧИТАТЬ.md']+list((out/'Документация').glob('*.md')):
    for target in re.findall(r'!?\[[^\]\n]*\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
        target=target.strip('<>').split('#')[0]
        if not target or re.match(r'^[a-zA-Z]+:',target) or target.startswith('//'):continue
        if not (p.parent/urllib.parse.unquote(target.replace('\\','/'))).exists():missing.append((str(p),target))
assert not missing,missing
files={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file() and p.name not in ('MANIFEST_SHA256.json','settings.json')}
(out/'MANIFEST_SHA256.json').write_text(json.dumps(files,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for relative in list(files)+['MANIFEST_SHA256.json']:z.write(out/relative,out.name+'/'+relative)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for relative,digest in files.items():assert hashlib.sha256(z.read(out.name+'/'+relative)).hexdigest()==digest,relative
    assert len(z.namelist())==len(files)+1
    assert all(not p.endswith('/settings.json') for p in z.namelist())
digest=hashlib.sha256(archive.read_bytes()).hexdigest();archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n',encoding='utf-8')
info.update(archive=str(archive),sha256=digest,bytes=archive.stat().st_size,files=len(files)+1,zip_crc_verified=True,all_hashes_verified=True,documentation_links_checked=True,com_selection_gui_verified=True,serial_tests=8,editor_regression_tests=100,physical_uart_flash_tested=False,application_changed=False,git_updated=False)
(U/'TRANSFER_PACKAGE.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
(B/'CURRENT_TRANSFER.md').write_text('# Пакет для передачи\n\n[Скачать ZIP](releases/'+archive.name+').\n\nМенеджер0.8.0-preview.4: выбор COM, веб-мост, первичная STM32 ROM UART-запись.\nПрошивкаFLE4D1.0.8 без изменений. UART-запись проверена программными тестами; аппаратно ещё не испытывалась.\n\nАрхив: '+str(info['bytes'])+' байт; SHA-256: `'+digest+'`. CRC и все контрольные суммы проверены.\nGitHub не обновлялся.\n',encoding='utf-8')
note='''
28.10.2026 — по замечанию пользователя в менеджер добавлена вкладка COM / UART.
0.8.0-preview.4: перечисление портов без открытия, скорость, запуск отдельного
моста с выбранным портом/папкой; STM32 ROM UART probe и первичная запись двух
образов через CubeCLI, с Device ID/Flash guard и verify каждого файла, без
массового стирания, повторов и автоматического запуска при BOOT0=1.
F407 ROM поддерживает USART1/USART3, не UART6: текущий COM5 PC6/PC7 подходит
веб-мосту, для первичной записи требуется другое подключение и режим BOOT0.
UART8E1, веб8N1; подсказка и ссылка ST AN2606 в руководстве. Аппаратная ROM UART
запись не выполнялась. 8 программных тестов и100 редакторских прошли;
GUI нового EXE с выборомCOM5 проверен, сам порт не открывали. SWD больше не
требуетIP. Активные программы/ПЛК не останавливали и не прошивали.
Новый пакет в releases/FLProg_Network_FLE4D_1.0.8_COM_2026-10-28_r2.zip,
путь и SHA в CURRENT_TRANSFER.md. Три библиотеки, блоки, триEXE, проект4,
точный снимок сборкиBIN, API/документация, все SHA иCRC архива проверены.
Нативная прошивка1.0.8 не менялась; UART-блоки Basic/Pro остаются будущими.
GitHub не обновляли. Старые релизы и работающий COM-мост64016 сохранены.
'''
for p in (B/'AGENTS.md',Path(r'E:\SAI\Правила для Codex\Проекты\FLProg_Network.md'),U.parent/'ACTIVE_TASK.md'):
    with p.open('a',encoding='utf-8') as f:f.write(note)
print(json.dumps(info,ensure_ascii=False))
