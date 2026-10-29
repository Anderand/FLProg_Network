# coding: utf-8
"""Adapt the user's new native sketch 4 without changing the original."""
import difflib,hashlib,json,re,shutil,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=Path(r'E:\FLProg_Projects\FLE4D-30MT')
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_web_20261028')
sys.path.insert(0,str(R/'flprog_webui_next/tools'))
from export_bridge import export_bridge,attach_bridge_header
from build_project_package import build
from preview_project import preview_html

raw=P/'4/4.ino';base=raw.read_text(encoding='utf-8-sig')
old=(W/'FLE4D_Bridge_Web/FLE4D_Bridge_Web.ino').read_text(encoding='utf-8')
assert 'profileWebOutputEnabled' not in base
assert 'ExternalEEPROM_252608257(1, 0x50, 6, 246, 0)' in base
assert '.setDhcp();' in base and 'Modbus_246570956' not in base
version='1.0.8-BRIDGE-WEB'
def section(start,end):return old[old.index(start):old.index(end,old.index(start))]
globals=section('// Web output control is RAM-only.','void setup()')
globals=globals.replace('1.0.7-BRIDGE-WEB',version)
globals=globals.replace('    if(channel>100)return;','    if(channel>100)return;\n    FLProgWebUiRuntime::publishBool(29,true);')
base=base.replace('#include <FLE4D-30MT_webui.h>','#include <FLE4D-30MT_webui.h>\n#include "FLProgWebUiBridge.h"\n#include <FLE4D-30MT_bridge.h>')
base=base.replace('void setup()',globals+'void setup()',1)
console=section('        // System channels:','        consoleVarBlock_17_Task.extEN = 1;')
base=base.replace('        consoleVarBlock_17_Task.extEN = 1;',console+'        consoleVarBlock_17_Task.extEN = 1;',1)
control_start=old.index('        // Consume and discard commands while disabled;')
control_end=re.search(r'        AI_block_\d+_outValue =',old[control_start:]).start()+control_start
control=old[control_start:control_end]
anchor=re.search(r'        AI_block_\d+_outValue = \(FLProgADC.AD\[0\].valueDevRAM\);',base)
assert anchor
base=base[:anchor.start()]+control+base[anchor.start():]
publication=section('        // Web UI I/O readback','    }\n    //Плата:11')
old_di=dict(re.findall(r'(DI_block_\d+_outValue) = \(FLProgPin_(\w+).digitalRead\(\)\);',old))
new_di={pin:var for var,pin in re.findall(r'(DI_block_\d+_outValue) = \(FLProgPin_(\w+).digitalRead\(\)\);',base)}
publication=re.sub(r'DI_block_\d+_outValue',lambda m:new_di[old_di[m[0]]],publication)
old_do={f'_VarToBit_{block}_{bit}':pin for pin,block,bit in re.findall(r'FLProgPin_(\w+).digitalWrite\(_VarToBit_(\d+)_(\d+)\);',old)}
new_do={pin:f'_VarToBit_{block}_{bit}' for pin,block,bit in re.findall(r'FLProgPin_(\w+).digitalWrite\(_VarToBit_(\d+)_(\d+)\);',base)}
publication=re.sub(r'_VarToBit_\d+_\d+',lambda m:new_do[old_do[m[0]]],publication)
anchor=base.index('    //Плата:11');brace=base.rfind('    }',0,anchor)
base=base[:brace]+publication+base[brace:]
start=old.index('        if (profileWebOutputEnabled) {');end=old.index('\n        }',start)+len('\n        }')
anchor=re.search(r'        _gtv48 = _mux\d+;',base);assert anchor
base=base[:anchor.end()]+'\n'+old[start:end]+base[anchor.end():]
base=base.replace('flprogOtaUniversal.control(EN, (int32_t)NET_NUM, PASSWORD);','flprogOtaUniversal.control(EN, (int32_t)NET_NUM, PASSWORD, String("'+version+'"));')
# Console must not mix text with binary bridge frames; other UARTs remain native.
base=re.sub(r'^(\s*)(RT_HW_console\.(?:out\w*|PLC_out\w*|setParam)\([^\n]+)$',r'\1if (false) \2 // UART6 reserved for bridge.',base,flags=re.M)
anchor=base.index('    flprog::specialSetup();')
base=base[:anchor]+'    RT_HW_Base.uartSetSpeed(115200,6);\n    RT_HW_Base.uartBegin(6);\n    bridgeWeb.attach(bridgeServer);\n'+base[anchor:]
base=base.replace('void loop()\n{','void loop()\n{\n    bridgePoll();',1)
assert base.count('bridgePoll();')==1 and base.count('publishBool(101,')==1
assert base.count('ExternalEEPROM_252608257(1, 0x50, 6, 246, 0)')==1
assert 'Modbus_246570956' not in base and 'setStatic' not in base
doc=json.loads((P/'FLE4D-30MT.flpui').read_text(encoding='utf-8'))
site=W/'user4/site';result=export_bridge(doc,R/'flprog_webui_next',site)
libraries=W/'user4/libraries';shutil.copytree(P/'libraries',libraries,dirs_exist_ok=True)
build(P/'FLE4D-30MT.flpui',libraries)
shutil.copytree(R/'flprog_webui_next/runtime/FLProg_WebUI',libraries/'FLProg_WebUI',dirs_exist_ok=True)
attach_bridge_header(libraries/'FLProg_WebUI_Project_FLE4D-30MT',result)
folder=W/'user4/FLE4D_Profile_Bridge';folder.mkdir(parents=True,exist_ok=True)
sketch=folder/'FLE4D_Profile_Bridge.ino';sketch.write_text(base,encoding='utf-8')
for header in (R/'flprog_bridge/firmware').glob('*.h'):shutil.copy2(header,folder/header.name)
shutil.copy2(raw,W/'user4/USER4_ORIGINAL.ino')
(W/'user4/ADAPTATIONS.patch').write_text(''.join(difflib.unified_diff(raw.read_text(encoding='utf-8-sig').splitlines(True),base.splitlines(True),fromfile='4/4.ino',tofile=sketch.name)),encoding='utf-8')
(W/'user4/PREVIEW.html').write_text(preview_html(doc,R/'flprog_webui_next'),encoding='utf-8')
info=dict(sketch=str(sketch),libraries=str(libraries),site=str(site),projectHash=result['projectHash'],version=version,source=str(raw),sourceSha256=hashlib.sha256(raw.read_bytes()).hexdigest(),network='DHCP',eepromSignature=246)
(W/'PREPARED.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
print(json.dumps(info,ensure_ascii=False))
