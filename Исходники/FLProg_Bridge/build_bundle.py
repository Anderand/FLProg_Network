# coding: utf-8
"""Build a new local preview bundle; never overwrite a release or touch Git."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parent
EDITOR=WORKSPACE/'flprog_webui_next'
MANAGER=WORKSPACE/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER'


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--work',required=True,type=Path)
    p.add_argument('--base-release',required=True,type=Path);p.add_argument('--deps',required=True,type=Path)
    p.add_argument('--profile',action='append',type=Path,default=[],help='Prepared profile folders override application profiles from the base release')
    a=p.parse_args();out=a.output.resolve();work=a.work.resolve()
    if out.exists():p.error('Output must be new')
    out.mkdir(parents=True);work.mkdir(parents=True,exist_ok=True)
    def freeze(name,source,paths=(),data=()):
        command=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--windowed','--onedir','--name',name,
                 '--distpath',str(work/'dist'),'--workpath',str(work/name),'--specpath',str(work)]
        for folder in paths:command+=['--paths',str(folder)]
        for source_path,target in data:command+=['--add-data',str(source_path)+';'+target]
        subprocess.run(command+[str(source)],check=True)
        return work/'dist'/name
    bridge=freeze('FLProg_Bridge',ROOT/'app.py',[a.deps],[(ROOT/'public','public')])
    shutil.copytree(bridge,out/'Мост_связи')
    for item in ('README_RU.md','PROTOCOL_RU.md','API_RU.md','CHECKS_RU.md','HARDWARE_RU.md','ROADMAP_RU.md','LICENSE_PYSERIAL.md'):shutil.copy2(ROOT/item,out/'Мост_связи'/item)
    for folder in ('firmware','docs'):shutil.copytree(ROOT/folder,out/'Мост_связи'/folder)
    shutil.copytree(EDITOR/'runtime/FLProg_WebUI',out/'Библиотека/FLProg_WebUI',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    m=freeze('FLProg_Firmware_Manager',MANAGER/'flprog_stm32_ota_manager.py',
             [MANAGER,MANAGER.parent/'OTA_APP_FLE4D',MANAGER.parent.parent/'STM32_OTA_PORTABILITY',EDITOR/'tools'])
    shutil.copytree(m,out/'Менеджер_прошивок')
    shutil.copytree(a.base_release/'OTA_Менеджер/build_tools',out/'Менеджер_прошивок/build_tools',ignore=shutil.ignore_patterns('__pycache__','*.pyc','settings.json'))
    shutil.copy2(EDITOR/'tools/build_compatibility.py',out/'Менеджер_прошивок/build_tools/build_compatibility.py')
    profiles=out/'Менеджер_прошивок/profiles';profiles.mkdir()
    for folder in (a.base_release/'OTA_Менеджер/profiles').iterdir():
        if not folder.is_dir():continue
        row=json.loads((folder/'profile.json').read_text(encoding='utf-8'))
        if a.profile and not row.get('loader_only'):continue
        shutil.copytree(folder,profiles/folder.name)
    for folder in a.profile:
        row=json.loads((folder/'profile.json').read_text(encoding='utf-8'))
        shutil.copytree(folder,profiles/row['id'])
    shutil.copy2(ROOT/'MANAGER_RU.md',out/'Менеджер_прошивок'/'README_RU.md')
    subprocess.run([sys.executable,str(EDITOR/'tools/build_editor.py'),'--output',str(work/'editor_dist')],check=True)
    shutil.copytree(work/'editor_dist/FLProg_WebUI_Editor',out/'Редактор')
    shutil.copytree(ROOT,out/'Исходники/Мост_связи',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    (out/'ПРОЧИТАТЬ.md').write_text('# Предварительный комплект FLProg Network\n\nТри самостоятельные программы: Мост_связи, Редактор, Менеджер_прошивок.\nНачните с [инструкции моста](Мост_связи/README_RU.md).\n\nЭто локальный прототип, не замена опубликованного r16. ПЛК не прошивался.\n',encoding='utf-8')
    manifest={str(f.relative_to(out)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}
    (out/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(folder=str(out),files=len(manifest)),ensure_ascii=False))

if __name__=='__main__':main()
