# coding: utf-8
import hashlib,json,sys,time,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[2];W=Path(r'E:\SAI\FLProg_Network\_work\bridge_web_20261028');U=W/'user4'
sys.path[:0]=[str(R/'hardware_gates/STM32_W5500_GATE/OTA_APP_FLE4D'),str(R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER')]
from upload_fle4d_ota import upload_image
from ota_discovery import probe
ready=json.loads((U/'PROFILE_READY.json').read_text(encoding='utf-8'));data=ready['build']
assert (Path(ready['folder'])/'Менеджер_прошивок/FLProg_Firmware_Manager.exe').is_file()
assert hashlib.sha256(Path(data['source']).read_bytes()).hexdigest()==data['sourceSha256']
profile=json.loads((Path(ready['profile'])/'profile.json').read_text(encoding='utf-8'))
blob=(Path(ready['profile'])/'application.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()==profile['artifacts']['application']['sha256']==data['sha256']
host='192.168.100.19';before=probe(host,3233,3)
assert before and '1.0.7-BRIDGE-WEB' in before['detail'] and 'FLE4D-30MT' in before['detail'],before
with urllib.request.urlopen('http://'+host+'/flprog-webui/state?channel=network_mac',timeout=5) as response:mac=json.load(response)['value']
assert mac=='78:AC:C0:5C:44:8D',mac
sent=upload_image(host,blob,'',timeout=30);print('Staged',sent,flush=True)
deadline=time.monotonic()+120;after=None
while time.monotonic()<deadline:
    time.sleep(1)
    try:after=probe(host,3233,1)
    except OSError:continue
    if after and data['version'] in after['detail']:break
assert after and data['version'] in after['detail'],after
(U/'OTA_INSTALL.json').write_text(json.dumps(dict(before=before,after=after,mac=mac,staged=sent,sha256=data['sha256'],profile_ready_before_ota=True,source=data['source'],sourceSha256=data['sourceSha256'],bootloader_written=False),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(after,ensure_ascii=False))
