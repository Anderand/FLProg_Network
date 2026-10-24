from pathlib import Path
import hashlib
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parent
IDE = Path(r'C:\F-981\FLProg\ideV8')
OUT = ROOT / 'build'
OUT.mkdir(exist_ok=True)
command = [str(IDE/'arduino-builder.exe'), '-compile', '-jobs=4', '-logger=human']
for folder in ['hardware', 'portable/packages']:
    command += ['-hardware', str(IDE/folder)]
for folder in ['tools-builder', 'hardware/tools/avr', 'portable/packages']:
    command += ['-tools', str(IDE/folder)]
command += ['-built-in-libraries', str(IDE/'libraries'), '-libraries',
            str(IDE/'portable/sketchbook/libraries'), '-fqbn',
            'STMicroelectronics:stm32:GenFLProgF4:pnum=FLProg_FLE4D_30MT_OTA',
            '-build-path', str(OUT)]
for pref in ['compiler.optimization_flags=-Os', 'build.flash_offset=0x10000',
             'upload.maximum_size=458752', 'upload.maximum_data_size=131072',
             'build.extra_flags=-DFLPROG_FLE4D_30MT_OTA_PROFILE=1 -DFLPROG_OTA_BOARD_FLE4D_30MT=1']:
    command += ['-prefs', pref]
command += [str(ROOT/'FLE4D_OTA_BLOCK_1_0_1.ino')]
with (ROOT/'build.log').open('w', encoding='utf-8') as log:
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
print((ROOT/'build.log').read_text(encoding='utf-8', errors='replace')[-3000:])
if result.returncode:
    raise SystemExit(result.returncode)
source = OUT/'FLE4D_OTA_BLOCK_1_0_1.ino.bin'
blob = source.read_bytes()
sp, entry = struct.unpack('<II', blob[:8])
assert 8 <= len(blob) <= 458752
assert sp == 0x20020000 and entry & 1
assert 0x08010000 <= (entry & ~1) < 0x08010000+len(blob)
assert b'FLE4D-30MT / STM32F407VG' in blob and b'1.0.1' in blob
target = ROOT/'FLE4D_OTA_BLOCK_1_0_1.bin'
shutil.copy2(source, target)
target.with_suffix('.bin.sha256').write_text(hashlib.sha256(blob).hexdigest()+'\n')
print('BIN:', target, 'bytes:', len(blob), 'SP:', hex(sp), 'entry:', hex(entry))
