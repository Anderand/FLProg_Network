from pathlib import Path
import hashlib
import json
import shutil
import struct
import sys
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parent
PORTING=ROOT.parent.parent/'STM32_OTA_PORTABILITY'
sys.path.insert(0,str(PORTING))
import build_stm32_ota as builder
from profile_policy import OBSOLETE_IDS

def main():
    release=ROOT/'portable_v6';data=release/'build_tools';data.mkdir(parents=True,exist_ok=True)
    for profile_id in OBSOLETE_IDS:
        old=release/'profiles'/profile_id
        if old.exists():shutil.rmtree(old)
    for name in ['boards_catalog.json','PORTING_STATUS_RU.md','VALIDATION_RU.md']:
        shutil.copy2(PORTING/name,data/name)
    shutil.copytree(PORTING/'STM32_OTA_BOOTLOADER',data/'STM32_OTA_BOOTLOADER',dirs_exist_ok=True)
    catalog=[]
    for name,row in sorted(builder.boards().items()):
        source=PORTING/'output'/name/'bootloader.bin'
        blob=source.read_bytes();sp,entry=struct.unpack('<II',blob[:8])
        layout=builder.LAYOUTS[row['layout']]
        assert 8<=len(blob)<=layout['offset'] and entry&1 and not sp&7
        assert 0x08000000 <= (entry&~1) < 0x08000000+len(blob)
        assert 0x20000000 < sp <= 0x20000000+row['ram']
        digest=hashlib.sha256(blob).hexdigest()
        assert source.with_suffix('.sha256').read_text().strip()==digest
        target=data/'output'/name;target.mkdir(parents=True,exist_ok=True)
        for filename in ['bootloader.bin','bootloader.sha256','bootloader_build.json']:
            shutil.copy2(source.parent/filename,target/filename)
        catalog.append(dict(board=name,label=row['label'],flash=row['flash'],layout=row['layout'],
                            size=len(blob),sha256=digest,file=str((target/'bootloader.bin').relative_to(release)),hardware_verified=False))
        profile_id='board_'+name.lower()
        profile_folder=release/'profiles'/profile_id
        profile_folder.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,profile_folder/'bootloader.bin')
        profile=dict(schema_version=1,id=profile_id,loader_only=True,
            label=row['label']+' / '+str(row['flash']//1024)+' KiB — нужен BIN проекта',
            description='Загрузчик готов. Приложение собирается из вашего проекта FLProg на вкладке «Плата и сборка».',
            target=dict(board=row['label'],mcu=row['mcu'],flash_size=row['flash'],hardware_verified=False),
            flash=dict(bootloader_address='0x08000000',bootloader_size=layout['offset'],
                application_address=hex(0x08000000+layout['offset']),application_max_size=layout['capacity'],
                staging_address=hex(0x08000000+layout['stage']),staging_size=layout['flash']-layout['stage']),
            ota=dict(protocol='FLPOTA2',port=3233,block_size=1024),
            artifacts=dict(bootloader=dict(file='bootloader.bin',max_size=layout['offset'],sha256=digest)))
        (profile_folder/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf-8')
    (release/'bootloaders_catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    shutil.copy2(ROOT/'README_UNIFIED_RU.md',release/'README_RU.md')
    block=release/'FLProg_OTA_Block';block.mkdir(exist_ok=True)
    block_source=ROOT.parent.parent/'FLProg_OTA_Block_v0_4'
    shutil.copy2(block_source/'FLProg_OTA_Universal.ubi',block/'FLProg_OTA_Universal.ubi')
    shutil.copytree(block_source/'src',block/'src',dirs_exist_ok=True)
    for name in ['README_RU.txt']:
        shutil.copy2(block_source/name,block/name)
    with ZipFile(ROOT/'FLProg_STM32_OTA_Manager_v0_7_7_portable.zip','w',ZIP_DEFLATED) as archive:
        for path in release.rglob('*'):
            if path.is_file() and not any(part in ('build','logs','__pycache__') for part in path.relative_to(release).parts):
                archive.write(path,str(path.relative_to(release)))
    print('Packaged loaders:',len(catalog))

if __name__=='__main__':main()
