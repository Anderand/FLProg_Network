# coding: utf-8
from pathlib import Path
import gzip,hashlib,json,re,shutil,sys
R=Path(__file__).resolve().parents[2];B=Path(r'E:\SAI\FLProg_Network');W=B/'_work/bridge_flash_20261028';U=B/'_work/bridge_web_20261028/user4';P=Path(r'E:\FLProg_Projects\FLE4D-30MT')
sys.path[:0]=[str(R/'flprog_webui_next/tools')]
from export_bridge import export_bridge,attach_bridge_header
from build_project_package import build
W.mkdir(exist_ok=True)
previous=U/'FLE4D_Profile_Bridge/FLE4D_Profile_Bridge.ino';source=previous.read_text(encoding='utf-8')
assert '1.0.8-BRIDGE-WEB' in source and '.setDhcp();' in source
version='1.0.9-BRIDGE-FLASH';source=source.replace('1.0.8-BRIDGE-WEB',version)
source=source.replace('#include "FLProgWebUiBridge.h"','#include "FLProgWebUiBridge.h"\n#include "FLProgBridgeResources.h"',1)
source=source.replace('FLProgWebUiBridge bridgeWeb(', 'FLProgBridgeResources bridgeResources(FLPROG_BRIDGE_WEB_PACKAGE,FLPROG_BRIDGE_WEB_PACKAGE_SIZE,FLPROG_BRIDGE_WEB_PACKAGE_PLAIN_SIZE,FLPROG_BRIDGE_WEB_PACKAGE_SHA256);\nFLProgWebUiBridge bridgeWeb(',1)
source=source.replace('bridgeWeb.attach(bridgeServer);','bridgeWeb.attach(bridgeServer);\n    bridgeResources.attach(bridgeServer);',1)
folder=W/'FLE4D_Bridge_Flash';folder.mkdir(exist_ok=True);sketch=folder/'FLE4D_Bridge_Flash.ino';sketch.write_text(source,encoding='utf-8')
for header in (R/'flprog_bridge/firmware').glob('*.h'):shutil.copy2(header,folder/header.name)
doc=json.loads((P/'FLE4D-30MT.flpui').read_text(encoding='utf-8'))
export=export_bridge(doc,R/'flprog_webui_next',W/'generated_site')
libraries=W/'libraries';shutil.copytree(U/'libraries',libraries,dirs_exist_ok=True)
build(P/'FLE4D-30MT.flpui',libraries)
shutil.copytree(R/'flprog_webui_next/runtime/FLProg_WebUI',libraries/'FLProg_WebUI',dirs_exist_ok=True)
attach_bridge_header(libraries/'FLProg_WebUI_Project_FLE4D-30MT',export)
header=Path(export['identityHeader']).read_text(encoding='utf-8')
compressed=int(re.search(r'FLPROG_BRIDGE_WEB_PACKAGE_SIZE=(\d+)U',header)[1]);plain=int(re.search(r'FLPROG_BRIDGE_WEB_PACKAGE_PLAIN_SIZE=(\d+)U',header)[1])
raw4=P/'4/4.ino'
info=dict(sketch=str(sketch),libraries=str(libraries),version=version,projectHash=export['projectHash'],compressed_resource_bytes=compressed,plain_resource_bytes=plain,base_source=str(raw4),base_source_sha256=hashlib.sha256(raw4.read_bytes()).hexdigest(),previous_application_sha256='4c4763e1c9b2179037567b12d241750a7453b069f2f8afb899cb877ac5080176')
(W/'PREPARED.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(info,ensure_ascii=False))
