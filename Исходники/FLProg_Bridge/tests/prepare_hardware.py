# coding: utf-8
"""Prepare the UART6/DHCP profile; normal variant is a legacy compile baseline only."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil

ROOT=Path(__file__).resolve().parents[2]
P=Path(r'E:\FLProg_Projects\FLE4D-30MT')
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_20261028\hardware')
W.mkdir(exist_ok=True)
original=(P/'FLE4D_30MT_Profile/FLE4D_30MT_Profile.ino').read_text(encoding='utf-8-sig')
backup=W/'profile_before_dhcp.ino'
if not backup.exists():backup.write_text(original,encoding='utf-8')
else:original=backup.read_text(encoding='utf-8')
normal=original.replace('1.0.4-PROFILE','1.0.5-PROFILE')
pattern=r'    WiznetInterface_165513604.resetDhcp\(\);\n(?:    WiznetInterface_165513604\.(?:localIP|dns|gateway|subnet)\(IPAddress\([^\n]+\n){4}'
normal,n=re.subn(pattern,'    WiznetInterface_165513604.setDhcp(); // Portable profile: router supplies IP, mask, gateway and DNS.\n',normal)
assert n==1 and 'IPAddress(192, 168, 0, 191)' not in normal
normal_dir=W/'FLE4D_DHCP';normal_dir.mkdir(exist_ok=True)
(normal_dir/'FLE4D_DHCP.ino').write_text(normal,encoding='utf-8')
bridge=normal.replace('1.0.5-PROFILE','1.0.6-BRIDGE')
bridge=bridge.replace('#include <FLE4D-30MT_webui.h>','#include <FLE4D-30MT_webui.h>\n#include "FLProgWebUiBridge.h"')
code=r'''
// UART6 is dedicated to the bridge ONLY in this experimental build.
// User reserved UART6 for the bridge, excluding it from console and Modbus RTU.
static bool bridgeWritePolicy(uint8_t channel,const uint8_t *data,uint16_t length) {
    if(channel!=241 || length!=5 || data[0]!=FLPROG_WEBUI_INT32) return false;
    int32_t value=(int32_t)flprog_bridge::getLE(data+1,4);
    return value>=-1000000 && value<=1000000; // Software echo only, no physical output.
}
static void bridgeBeforeRead(uint8_t channel) {
    if(channel>100)return;
    FLProgWebUiFlprogNetworkPagedHttp::refreshSystemChannels();
    FLProgWebUiRuntime::publishText(5,"FLE4D-30MT / STM32F407VG");
    FLProgWebUiRuntime::publishText(6,"1.0.6-BRIDGE");
    int16_t slot=flprog_webui_selected::model.indexOf("system_uptime");
    if(slot>=0)flprog_webui_selected::model.publishInt((uint8_t)slot,(int32_t)(millis()/1000));
}
flprog_bridge::Server bridgeServer("{\"projectId\":\"FLE4D-30MT\",\"model\":\"FLE4D-30MT / STM32F407VG\",\"firmware\":\"1.0.6-BRIDGE\"}");
FLProgWebUiBridge bridgeWeb(flprog_webui_selected::model,bridgeWritePolicy,bridgeBeforeRead);
static uint32_t bridgeEchoCount=0;
static void bridgePoll() {
    bridgeServer.pool(Serial6,millis(),64);
    int16_t input=flprog_webui_selected::model.fbdSlot(241);int32_t value;
    if(input>=0 && flprog_webui_selected::model.takeInt((uint8_t)input,value)) {
        FLProgWebUiRuntime::publishInt(242,value);
        FLProgWebUiRuntime::publishInt(243,(int32_t)++bridgeEchoCount);
    }
}
'''
bridge=bridge.replace('void setup()',code+'\nvoid setup()',1)
bridge=bridge.replace('    flprog::specialSetup();\n}', '''    flprog::specialSetup();
    Modbus_246570956.setEnable(false); // UART6 belongs exclusively to bridge.
    RT_HW_Base.uartBegin(6);
    bridgeWeb.attach(bridgeServer);
}\n''',1)
bridge=bridge.replace('void loop()\n{','void loop()\n{\n    bridgePoll();',1)
bridge=bridge.replace('        Modbus_246570956.pool();','        // Modbus UART6 suspended during bridge test; other ports unchanged.')
bridge,n=re.subn(r'^(\s*)(RT_HW_console\.(?:setParam|out\w*)\([^\n]+;)',r'\1if (false) \2 // UART6 bridge: console output disabled.',bridge,flags=re.M)
assert n>10
folder=W/'FLE4D_Bridge';folder.mkdir(exist_ok=True)
(folder/'FLE4D_Bridge.ino').write_text(bridge,encoding='utf-8')
for source in (ROOT/'flprog_bridge/firmware').glob('*.h'):shutil.copy2(source,folder/source.name)
libraries=W/'libraries'
shutil.copytree(P/'libraries',libraries,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(ROOT/'flprog_webui_next/runtime/FLProg_WebUI',libraries/'FLProg_WebUI',dirs_exist_ok=True)
import sys
sys.path.insert(0,str(ROOT/'flprog_webui_next/tools'))
from build_project_package import build
original_project=W/'project_before_bridge/FLE4D-30MT.flpui'
project=json.loads((original_project if original_project.is_file() else P/'FLE4D-30MT.flpui').read_text(encoding='utf-8'))
for number,cid,direction in [(241,'bridge_echo_command','duplex'),(242,'bridge_echo_result','publish'),(243,'bridge_echo_count','publish')]:
    project['channels'].append(dict(id=cid,label=cid,type='int32',direction=direction,source='user',index=number))
project['projectFolder']=str(W);project['installToIde']=False
source=W/'FLE4D-30MT_bridge.flpui';source.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
build(source,libraries)
for kind,text in [('DHCP',normal),('BRIDGE',bridge)]:
    (W/(kind+'_changes.patch')).write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='profile1.0.4',tofile=kind)),encoding='utf-8')
(W/'PREPARED.json').write_text(json.dumps(dict(original_sha256=hashlib.sha256(original.encode()).hexdigest(),normal=str(normal_dir/'FLE4D_DHCP.ino'),bridge=str(folder/'FLE4D_Bridge.ino'),normal_libraries=str(P/'libraries'),bridge_libraries=str(libraries),writes='only RAM echo 241; physical outputs denied',uart='COM5 UART6 PC6/PC7 115200; confirmed by user',network='DHCP confirmed by user'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared DHCP profile and separate bridge variant')
