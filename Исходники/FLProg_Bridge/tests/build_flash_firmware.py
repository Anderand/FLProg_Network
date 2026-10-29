from pathlib import Path
import hashlib,json,shutil,struct,sys
R=Path(__file__).resolve().parents[2];W=Path(r'E:\SAI\FLProg_Network\_work\bridge_flash_20261028')
sys.path[:0]=[str(R/'flprog_webui_next/tools'),str(R/'hardware_gates/STM32_OTA_PORTABILITY')]
import build_stm32_ota as builder
data=json.loads((W/'PREPARED.json').read_text(encoding='utf-8'));builder.ROOT=W/'build_tools';builder.ROOT.mkdir(exist_ok=True)
shutil.copy2(R/'hardware_gates/STM32_OTA_PORTABILITY/boards_catalog.json',builder.ROOT/'boards_catalog.json')
image=builder.build('FLProg_FLE4D_30MT',Path(data['sketch']),False,libraries=Path(data['libraries']),package=False)
blob=image.read_bytes();sp,pc=struct.unpack('<II',blob[:8]);assert sp==0x20020000 and 0x08010000<=pc&~1<0x08010000+len(blob)<=0x08080000
assert data['version'].encode() in blob and data['projectHash'].encode() in blob
data.update(bin=str(image),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),hardware_tested=False)
(W/'BUILD.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(data))
