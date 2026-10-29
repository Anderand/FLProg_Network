# coding: utf-8
from pathlib import Path
import sys,json,shutil,subprocess,re,xml.etree.ElementTree as X
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\bridge_auto_20261029');w.mkdir(exist_ok=True)
sys.path[:0]=[str(r/'flprog_webui_next/tools'),str(r/'flprog_bridge/tests')]
from export_bridge import export_bridge,attach_bridge_header
from build_project_package import build
from test_web_project import document
libs=w/'libraries'
if not libs.exists():shutil.copytree(Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028\libraries'),libs)
shutil.copytree(r/'flprog_webui_next/runtime/FLProg_WebUI',libs/'FLProg_WebUI',dirs_exist_ok=True)
p=Path(r'E:\FLProg_Projects\FLE4D-30MT\FLE4D-30MT.flpui');data=json.loads(p.read_text(encoding='utf-8'));build(p,libs);result=attach_bridge_header(libs/'FLProg_WebUI_Project_FLE4D-30MT',export_bridge(data,r/'flprog_webui_next',w/'generated_site'))
# A small second project validates independent ID selection and the generic UBI.
doc=document();doc['project']['id']='auto-sample';source=w/'auto-sample.flpui';source.write_text(json.dumps(doc),encoding='utf-8');lib=build(source,libs);attach_bridge_header(lib,export_bridge(doc,r/'flprog_webui_next',w/'sample_site'))
blocks=w/'Блоки_FLProg/Bridge_UART'
def named(n,name):return next(x for x in n if x.get('sixx.name')==name)
base=named(X.parse(blocks/'Basic/FLProg_Bridge_UART.ubi').getroot(),'typeClass');body=named(named(base,'loopCodePart'),'code').text
for f in (blocks/'Professional').glob('*.ubi'):
 root=X.parse(f).getroot();ids={x.get('sixx.id'):x for x in root.iter() if x.get('sixx.id')}
 def resolve(x):return ids[x.get('sixx.idref')] if x.get('sixx.idref') else x
 parts=[];declarations=[]
 for fragment in root.iter():
  if fragment.get('sixx.type')!='UserCodeMultiBlockCodePartsInstance':continue
  section=named(fragment,'section').text
  if section not in ('loop','declare'):continue
  chunks=[]
  for n in named(fragment,'codeText'):
   v=resolve(named(n,'value'))
   if named(n,'type').text=='codeTag':
    obj=resolve(named(v,'object'));chunks.append(named(obj,'name').text if obj.get('sixx.type')=='UserCodeMultiBlockInputOutput' else 'auto-sample')
   else:chunks.append(v.text or '')
  (parts if section=='loop' else declarations).append(''.join(chunks))
 code=''.join(parts);assert code.strip()[1:-1].strip()==body.strip()
 if 'Project_' in f.name:assert '#include <auto-sample_bridge_entry.h>' in ''.join(declarations)
stubs=w/'stubs';stubs.mkdir(exist_ok=True);shutil.copy2(r/'flprog_bridge/tests/Arduino.h',stubs/'Arduino.h')
(stubs/'flprogUtilites.h').write_text('''#pragma once
#include <Arduino.h>
#include <deque>
#include <vector>
static uint32_t clockNow=1;inline uint32_t millis(){return clockNow;}
struct FakeRT {std::deque<uint8_t> input;std::vector<uint8_t> output;bool started=false;bool uartCheckNum(uint8_t n){return n==6;}int uartGetStatus(uint8_t){return started?1:0;}void uartSetSpeed(uint32_t,uint8_t){}void uartBegin(uint8_t){started=true;}void uartEnd(uint8_t){started=false;}int uartGetCodeErr(uint8_t){return 0;}int uartAvailable(uint8_t){return input.size();}int uartRead(uint8_t){int x=input.front();input.pop_front();return x;}int uartAvailableForWrite(uint8_t){return 64;}int uartWrite(uint8_t b,uint8_t){output.push_back(b);return 1;}};
static FakeRT RT_HW_Base;
''',encoding='utf-8')
head='''#include <flprogBridgeUserBlocks.h>
#include <auto-sample_bridge_entry.h>
#include <cassert>
#include <iostream>
#include <stdio.h>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
bool EN=false,READY=false,CONNECTED=false,ERROR=false;long UART=6,BAUD=115200,BUDGET=64,ERR=0,RX_BYTES=0,TX_BYTES=0,BAD_FRAMES=0;
String VERSION="1.0.12-AUTO",MODEL="Test \\\"model\\\"";
'''
footer='''
bool permit(uint8_t,const uint8_t*,uint16_t){return true;}
int main(int argc,char**argv){
#ifdef _WIN32
_setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);
#endif
 if(argc>1){loop();assert(!READY && !RT_HW_Base.started);EN=true;VERSION="";loop();assert(ERR==7 && !READY);VERSION="1.0.12-AUTO";loop();assert(READY);VERSION=String(400,'x');loop();assert(READY);EN=false;loop();assert(!READY && !RT_HW_Base.started);EN=true;loop();assert(ERR==7 && !READY);puts("PASS identity validation, freeze, disable and reconfigure");return 0;}
 EN=true;loop();assert(READY);
 // Optional explicit hook only in a separate native test invocation via requests is not enabled by default.
 for(int ch;(ch=std::cin.get())!=EOF;){RT_HW_Base.input.push_back((uint8_t)ch);for(int i=0;i<12;i++){clockNow++;loop();}for(auto b:RT_HW_Base.output)std::cout.put((char)b);RT_HW_Base.output.clear();std::cout.flush();}
}
'''
for kind in ('basic','professional'):
 path=w/(kind+'_auto_peer.cpp');path.write_text(head+'void loop(){\n'+(body if kind=='basic' else '{\n'+body+'\n}')+'\n}\n'+footer,encoding='utf-8')
 command=[str(r/'audit/host-tools/ziglang/zig.exe'),'c++','-std=c++17','-O2','-UNDEBUG','-I',str(stubs),'-I',str(libs/'FLProg_WebUI/src'),'-I',str(lib/'src'),str(path),'-o',str(w/(kind+'_auto_peer.exe'))];subprocess.run(command,check=True);subprocess.run([str(w/(kind+'_auto_peer.exe')),'--selftest'],check=True)
# Prepare the actual FLE4D app without hand-created Server/services/resources.
old=Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028\FLE4D_Link/FLE4D_Link.ino');s=old.read_text(encoding='utf-8').replace('1.0.10-BRIDGE-LINK','1.0.12-BRIDGE-AUTO')
s=s.replace('#include "FLProgWebUiBridge.h"','#include <flprogBridgeUserBlocks.h>').replace('#include "FLProgBridgeResources.h"','')
a=s.index('flprog_bridge::Server bridgeServer(');z=s.index('FLProgWebUiBridge bridgeWeb(',a);z=s.index('\n',z)
s=s[:a]+'#define bridgeServer flprog_bridge_selected::binding().server\n'+s[z:]
s=s.replace('bridgeServer.pool(Serial6,millis(),64);','auto &project = flprog_bridge_selected::binding();\n    project.setHooks(bridgeWritePolicy,bridgeBeforeRead);\n    if(project.configure("1.0.12-BRIDGE-AUTO", "FLE4D-30MT / STM32F407VG"))\n        flpBridgeUartBlocks().pool(project.server,true,6,115200,64,millis());')
s=s.replace('    RT_HW_Base.uartSetSpeed(115200,6);\n    RT_HW_Base.uartBegin(6);\n','').replace('    bridgeWeb.attach(bridgeServer);\n    bridgeResources.attach(bridgeServer);\n','')
folder=w/'FLE4D_Auto';folder.mkdir(exist_ok=True);sketch=folder/'FLE4D_Auto.ino';sketch.write_text(s,encoding='utf-8')
info=json.loads(Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028\BUILD.json').read_text(encoding='utf-8'));info.update(sketch=str(sketch),libraries=str(libs),version='1.0.12-BRIDGE-AUTO',projectHash=result['projectHash'],hardware_tested=False);(w/'PREPARED.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
(w/'AUTO_CHECKS.json').write_text(json.dumps(dict(two_projects=True,basic_professional_code_equal=True,professional_id_parameter=True,identity_self_tests=True,controller_flashed=False),indent=2),encoding='utf-8');print('PASS automatic project binding and both UBI formats')
