# coding: utf-8
from pathlib import Path
import json,re,shutil
R=Path(__file__).resolve().parents[2];P=Path(r'E:\FLProg_Projects\FLE4D-30MT')
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_web_20261028');W.mkdir(exist_ok=True)
source=(P/'FLE4D_30MT_Profile/FLE4D_30MT_Profile.ino').read_text(encoding='utf-8')
backup=W/'profile_before_web.ino'
if not backup.exists():backup.write_text(source,encoding='utf-8')
else:source=backup.read_text(encoding='utf-8')
assert '1.0.6-BRIDGE' in source
source=source.replace('1.0.6-BRIDGE','1.0.7-BRIDGE-WEB')
source=source.replace('FLProgWebUiRuntime::publishBool(29, RT_HW_console.dev.ok);','FLProgWebUiRuntime::publishBool(29, bridgeServer.sessionAlive(millis()));')
source=source.replace('#include "FLProgWebUiBridge.h"','#include "FLProgWebUiBridge.h"\n#include <FLE4D-30MT_bridge.h>',1)
start=source.index('static bool bridgeWritePolicy(');end=source.index('static void bridgeBeforeRead',start)
policy='''static bool bridgeControlLease=false;
static bool bridgeWritePolicy(uint8_t channel,const uint8_t *data,uint16_t length) {
    if(channel==241 && length==5 && data[0]==FLPROG_WEBUI_INT32) {
        int32_t value=(int32_t)flprog_bridge::getLE(data+1,4);return value>=-1000000 && value<=1000000;
    }
    if(channel==137 && length==2 && data[0]==FLPROG_WEBUI_BOOL) {
        bridgeControlLease=data[1]!=0;return true;
    }
    if(!profileWebOutputEnabled)return false;
    if(channel>=121 && channel<=134)return length==2 && data[0]==FLPROG_WEBUI_BOOL;
    if((channel==135 || channel==136) && length==5 && data[0]==FLPROG_WEBUI_INT32) {
        int32_t value=(int32_t)flprog_bridge::getLE(data+1,4);return value>=0 && value<=10000;
    }
    return false;
}
'''
source=source[:start]+policy+source[end:]
source=source.replace('    if(channel>100)return;','    if(channel>100)return;\n    FLProgWebUiRuntime::publishBool(29,true);',1)
declaration='flprog_bridge::Server bridgeServer("{\\"projectId\\":\\"FLE4D-30MT\\",\\"model\\":\\"FLE4D-30MT / STM32F407VG\\",\\"firmware\\":\\"1.0.7-BRIDGE-WEB\\",\\"webApi\\":1,\\"webHash\\":\\"" FLPROG_BRIDGE_WEB_HASH "\\"}");'
source,n=re.subn(r'^flprog_bridge::Server bridgeServer\([^\n]+',lambda m:declaration,source,flags=re.M);assert n==1
source=source.replace('    bridgeServer.pool(Serial6,millis(),64);','''    bridgeServer.pool(Serial6,millis(),64);
    if(bridgeControlLease && !bridgeServer.sessionAlive(millis())) {
        profileWebOutputEnabled=false;profileWebDoMask=0;profileWebAo[0]=profileWebAo[1]=0;
        bridgeControlLease=false;
    }''',1)
source=source.replace('profileWebOutputEnabled = webModeRequest && WiznetInterface_165513604.isReady();','profileWebOutputEnabled = webModeRequest && (WiznetInterface_165513604.isReady() || bridgeServer.sessionAlive(millis()));')
source=source.replace('publishBool(42, profileWebOutputEnabled && WiznetInterface_165513604.isReady())','publishBool(42, profileWebOutputEnabled && (WiznetInterface_165513604.isReady() || bridgeServer.sessionAlive(millis())))')
assert source.count('bridgeServer.sessionAlive(millis())')==3
folder=W/'FLE4D_Bridge_Web';folder.mkdir(exist_ok=True)
(folder/'FLE4D_Bridge_Web.ino').write_text(source,encoding='utf-8')
for f in (R/'flprog_bridge/firmware').glob('*.h'):shutil.copy2(f,folder/f.name)
libraries=W/'libraries';shutil.copytree(P/'libraries',libraries,dirs_exist_ok=True)
shutil.copytree(R/'flprog_webui_next/runtime/FLProg_WebUI',libraries/'FLProg_WebUI',dirs_exist_ok=True)
import sys
sys.path.insert(0,str(R/'flprog_webui_next/tools'))
from export_bridge import attach_bridge_header
attach_bridge_header(libraries/'FLProg_WebUI_Project_FLE4D-30MT',dict(identityHeader=str(P/'bridge_web/firmware/FLProgBridgeProject.h')))
manifest=json.loads((P/'bridge_web/bridge.json').read_text(encoding='utf-8'))
identity=dict(protocol=1,services=[1],identity=dict(projectId='FLE4D-30MT',model='FLE4D-30MT / STM32F407VG',firmware='1.0.7-BRIDGE-WEB',webApi=1,webHash=manifest['projectHash']))
assert len(json.dumps(identity,separators=(',',':')).encode())<=254
(W/'PREPARED.json').write_text(json.dumps(dict(sketch=str(folder/'FLE4D_Bridge_Web.ino'),libraries=str(libraries),site=str(P/'bridge_web'),projectHash=manifest['projectHash'],version='1.0.7-BRIDGE-WEB',hello_bytes=len(json.dumps(identity,separators=(',',':')).encode())),indent=2),encoding='utf-8')
print('Prepared firmware and matching site, HELLO bytes:',len(json.dumps(identity,separators=(',',':')).encode()))
