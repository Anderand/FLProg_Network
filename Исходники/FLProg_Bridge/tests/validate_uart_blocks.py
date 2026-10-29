# coding: utf-8
from pathlib import Path
import xml.etree.ElementTree as X
import subprocess,json,re,shutil,hashlib
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\uart_blocks_20261028');blocks=w/'Блоки_FLProg/Bridge_UART'
def named(n,name):return next(x for x in n if x.get('sixx.name')==name)
basic=X.parse(blocks/'Basic/FLProg_Bridge_UART.ubi').getroot();main=named(basic,'typeClass');code=named(named(main,'loopCodePart'),'code').text
pro=X.parse(blocks/'Professional/FLProg_Bridge_UART_Professional.ubi').getroot();byid={x.get('sixx.id'):x for x in pro.iter() if x.get('sixx.id')}
def resolve(x):return byid[x.get('sixx.idref')] if x.get('sixx.idref') else x
parts=[]
for fragment in pro.iter():
 if fragment.get('sixx.type')=='UserCodeMultiBlockCodePartsInstance' and any(c.get('sixx.name')=='section' and c.text=='loop' for c in fragment):
  for chunk in named(fragment,'codeText'):
   typ=named(chunk,'type').text;v=resolve(named(chunk,'value'))
   parts.append(named(resolve(named(v,'object')),'name').text if typ=='codeTag' else (v.text or ''))
pcode=''.join(parts);assert pcode.strip()[1:-1].strip()==code.strip()
(w/'basic_loop.cpp.txt').write_text(code,encoding='utf-8');(w/'professional_loop.cpp.txt').write_text(pcode,encoding='utf-8')
# Compile code recovered from both UBI formats against the actual helper and fake RT_HW backend.
stubs=w/'stubs';stubs.mkdir(exist_ok=True)
(stubs/'flprogUtilites.h').write_text('''#pragma once
#include <stdint.h>
#include <stddef.h>
inline uint32_t millis(){return 1;}
struct FakeRT {bool started=false;bool uartCheckNum(uint8_t n){return n==6;}int uartGetStatus(uint8_t){return started?1:0;}void uartSetSpeed(uint32_t,uint8_t){}void uartBegin(uint8_t){started=true;}void uartEnd(uint8_t){started=false;}int uartGetCodeErr(uint8_t){return 0;}int uartAvailable(uint8_t){return 0;}int uartRead(uint8_t){return 0;}int uartAvailableForWrite(uint8_t){return 64;}int uartWrite(uint8_t,uint8_t){return 1;}};
static FakeRT RT_HW_Base;
''',encoding='utf-8')
libs=w/'libraries'
if not libs.exists():shutil.copytree(Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028\libraries'),libs)
shutil.copytree(r/'flprog_webui_next/runtime/FLProg_WebUI',libs/'FLProg_WebUI',dirs_exist_ok=True)
header='''#include <flprogBridgeUserBlocks.h>
#include <cassert>
flprog_bridge::Server bridgeServer("{\\\"projectId\\\":\\\"block-check\\\"}");
#define FLPROG_BRIDGE_SERVER bridgeServer
bool EN=false,READY=false,CONNECTED=false,ERROR=false;long UART=6,BAUD=115200,BUDGET=64,ERR=0,RX_BYTES=0,TX_BYTES=0,BAD_FRAMES=0;
'''
for kind,body in [('basic',code),('professional',pcode)]:
 path=w/(kind+'_generated.cpp');path.write_text(header+'void loop(){\n'+body+'\n}\nint main(){loop();assert(!READY && !RT_HW_Base.started);EN=true;loop();assert(READY && RT_HW_Base.started && !CONNECTED && !ERROR);EN=false;loop();assert(!READY && !RT_HW_Base.started);}\n',encoding='utf-8')
 command=[str(r/'audit/host-tools/ziglang/zig.exe'),'c++','-std=c++17','-O2','-UNDEBUG','-I',str(stubs),'-I',str(libs/'FLProg_WebUI/src'),str(path),'-o',str(w/(kind+'_generated.exe'))]
 subprocess.run(command,check=True);subprocess.run([str(w/(kind+'_generated.exe'))],check=True)
# Full current FLE4D application with UART ownership moved from manual calls to block.
old=Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028\FLE4D_Link/FLE4D_Link.ino');s=old.read_text(encoding='utf-8')
s=s.replace('1.0.10-BRIDGE-LINK','1.0.11-BRIDGE-BLOCK')
assert '#include "flprogUtilites.h"' in s
s=s.replace('#include "flprogUtilites.h"','#include "flprogUtilites.h"\n#include <flprogBridgeUserBlocks.h>',1)
s=s.replace('    RT_HW_Base.uartSetSpeed(115200,6);\n    RT_HW_Base.uartBegin(6);\n','')
assert 'bridgeServer.pool(Serial6,millis(),64);' in s
s=s.replace('bridgeServer.pool(Serial6,millis(),64);','flpBridgeUartBlocks().pool(bridgeServer,true,6,115200,64,millis());',1)
# All bridge services share the same updated Server header through the packaged library.
s=s.replace('#include "FLProgWebUiBridge.h"','#include <bridge/FLProgWebUiBridge.h>').replace('#include "FLProgBridgeResources.h"','#include <bridge/FLProgBridgeResources.h>')
folder=w/'FLE4D_UartBlock';folder.mkdir(exist_ok=True);sketch=folder/'FLE4D_UartBlock.ino';sketch.write_text(s,encoding='utf-8')
data=json.loads(Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028\BUILD.json').read_text(encoding='utf-8'));data.update(sketch=str(sketch),libraries=str(libs),version='1.0.11-BRIDGE-BLOCK',hardware_tested=False);(w/'PREPARED.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(w/'UBI_CHECKS.json').write_text(json.dumps(dict(xml_backward_references=True,basic_and_professional_loop_equivalent=True,generated_code_compile_and_runtime=['Basic','Professional'],controller_firmware_installed=False),indent=2),encoding='utf-8')
print('PASS: Basic/Professional XML, identical recovered code, both generated loops compiled and exercised; F407 sketch prepared')
