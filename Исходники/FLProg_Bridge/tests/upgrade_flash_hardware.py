# coding: utf-8
import hashlib,json,sys,time,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[2];W=Path(r'E:\SAI\FLProg_Network\_work\bridge_flash_20261028')
sys.path[:0]=[str(R/'hardware_gates/STM32_W5500_GATE/OTA_APP_FLE4D'),str(R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER')]
from upload_fle4d_ota import upload_image
from ota_discovery import probe
from flprog_stm32_ota_manager import load_profile
from profile_policy import is_bundled
data=json.loads((W/'BUILD.json').read_text(encoding='utf-8'));ready=json.loads((W/'PROFILE_READY.json').read_text(encoding='utf-8'))
folder=Path(ready['folder']);assert (folder/'Менеджер_прошивок/FLProg_Firmware_Manager.exe').is_file()
profile,files=load_profile(Path(ready['profile']));assert is_bundled(profile)
blob=files['application'].read_bytes();assert hashlib.sha256(blob).hexdigest()==data['sha256']
assert hashlib.sha256(Path(data['base_source']).read_bytes()).hexdigest()==data['base_source_sha256']
host='192.168.100.19';before=probe(host,3233,3)
assert before and '1.0.8-BRIDGE-WEB' in before['detail'] and 'FLE4D-30MT' in before['detail'],before
with urllib.request.urlopen('http://'+host+'/flprog-webui/state?channel=network_mac',timeout=5) as r:mac=json.load(r)['value']
assert mac=='78:AC:C0:5C:44:8D',mac
(W/'PRE_OTA.json').write_text(json.dumps(dict(profile_ready_before_ota=True,manager_sha256=hashlib.sha256((folder/'Менеджер_прошивок/FLProg_Firmware_Manager.exe').read_bytes()).hexdigest(),before=before,mac=mac,sha256=data['sha256']),ensure_ascii=False,indent=2),encoding='utf-8')
print('Target verified:',host,mac,flush=True)
sent=upload_image(host,blob,'',timeout=45);print('Staged',sent,flush=True)
deadline=time.monotonic()+120;after=None
while time.monotonic()<deadline:
    time.sleep(1)
    try:after=probe(host,3233,1)
    except OSError:continue
    if after and data['version'] in after['detail']:break
assert after and data['version'] in after['detail'],after
(W/'OTA_INSTALL.json').write_text(json.dumps(dict(before=before,after=after,mac=mac,staged=sent,application_sha256=data['sha256'],profile_ready_before_ota=True,bootloader_written=False),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(after,ensure_ascii=False))
