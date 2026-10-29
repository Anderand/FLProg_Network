from pathlib import Path
import json,shutil,sys,hashlib,struct
ROOT=Path(__file__).resolve().parents[2]
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_20261028\hardware')
sys.path.insert(0,str(ROOT/'flprog_webui_next/tools'))
sys.path.insert(0,str(ROOT/'hardware_gates/STM32_OTA_PORTABILITY'))
import build_stm32_ota as b
kind=sys.argv[1]
cfg=json.loads((W/'PREPARED.json').read_text(encoding='utf-8'))
sketch=Path(cfg['normal' if kind=='normal' else 'bridge'])
libs=Path(cfg['normal_libraries' if kind=='normal' else 'bridge_libraries'])
b.ROOT=W/(kind+'_build_tools');b.ROOT.mkdir(exist_ok=True)
shutil.copy2(ROOT/'hardware_gates/STM32_OTA_PORTABILITY/boards_catalog.json',b.ROOT/'boards_catalog.json')
result=b.build('FLProg_FLE4D_30MT',sketch,False,libraries=libs,package=False)
blob=result.read_bytes();sp,pc=struct.unpack('<II',blob[:8])
version='1.0.5-PROFILE' if kind=='normal' else '1.0.6-BRIDGE'
assert version.encode() in blob and len(blob)<=458752 and sp==0x20020000 and 0x08010000<=(pc&~1)<0x08010000+len(blob)
info=dict(version=version,bin=str(result),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),address='0x08010000',sketch=str(sketch),libraries=str(libs),hardware_tested=False)
(W/(kind+'_BUILD.json')).write_text(json.dumps(info,indent=2),encoding='utf-8')
print(json.dumps(info))
