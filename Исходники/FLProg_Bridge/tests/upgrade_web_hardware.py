# coding: utf-8
from pathlib import Path
import json,sys,time,hashlib,urllib.request
R=Path(__file__).resolve().parents[2];W=Path(r'E:\SAI\FLProg_Network\_work\bridge_web_20261028')
sys.path[:0]=[str(R/'hardware_gates/STM32_W5500_GATE/OTA_APP_FLE4D'),str(R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER')]
from upload_fle4d_ota import upload_image
from ota_discovery import probe
host='192.168.100.19';before=probe(host,3233,2)
assert before and '1.0.6-BRIDGE;' in before['detail'] and 'FLE4D-30MT' in before['detail']
with urllib.request.urlopen('http://'+host+'/flprog-webui/state?channel=network_mac',timeout=5) as response:mac=json.load(response)['value']
assert mac=='78:AC:C0:5C:44:8D'
build=json.loads((W/'BUILD.json').read_text());blob=Path(build['bin']).read_bytes()
assert hashlib.sha256(blob).hexdigest()==build['sha256'] and build['projectHash'].encode() in blob
sent=upload_image(host,blob,'',timeout=30);print('Staged',sent,flush=True)
deadline=time.monotonic()+45;after=None
while time.monotonic()<deadline:
    time.sleep(1)
    after=probe(host,3233,1)
    if after and '1.0.7-BRIDGE-WEB' in after['detail']:break
assert after and '1.0.7-BRIDGE-WEB' in after['detail']
(W/'OTA_INSTALL.json').write_text(json.dumps(dict(before=before,after=after,mac=mac,staged=sent,sha256=build['sha256'],address='0x08010000',bootloader_written=False),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(after,ensure_ascii=False))
