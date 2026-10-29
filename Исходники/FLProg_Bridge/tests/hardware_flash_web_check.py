# coding: utf-8
import hashlib,json,subprocess,time,urllib.error,urllib.request
from pathlib import Path
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_flash_20261028');base=json.loads((W/'LIVE_STATUS.json').read_text())['url'].rstrip('/')
def get(path):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(base+path,timeout=5) as r:return json.load(r)
        except urllib.error.HTTPError as error:
            if error.code!=409 or attempt==4:raise
            time.sleep(.15)
before=get('/api/v1/status');assert before['online'] and not before['demo'] and before['webSource']=='device'
assert before['device']['identity']['firmware']=='1.0.9-BRIDGE-FLASH' and before['resources']['cacheHit'] is False
assert before['resources']['bytes']==15438 and before['badFrames']==0
with urllib.request.urlopen(base+'/',timeout=5) as r:
    url=r.geturl();html=r.read();assert '?web='+before['device']['identity']['webHash'] in url
pages={page:get('/flprog-webui/state?page='+page) for page in ('main','diagnostics','inputs','outputs')}
assert pages['diagnostics']['values']['firmware_version']=='1.0.9-BRIDGE-FLASH'
session=before['session'];old_count=get('/api/v1/channels/243')['value']
req=urllib.request.Request(base+'/api/v1/channels/241',data=json.dumps(dict(type='int32',value=54009,session=session)).encode(),headers={'Content-Type':'application/json','X-FLProg-Bridge':'1'})
with urllib.request.urlopen(req,timeout=5) as r:accepted=json.load(r)
time.sleep(.2);echo=get('/api/v1/channels/242');count=get('/api/v1/channels/243')
assert echo['value']==54009 and count['value']==old_count+1
boot=W/'boot_after.bin';read=subprocess.run([r'C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe','-c','port=SWD','sn=006500585900000B56314C4D','mode=HOTPLUG','-u','0x08000000','0x10000',str(boot)],capture_output=True)
(W/'BOOT_AFTER.log').write_bytes(read.stdout+read.stderr);assert read.returncode==0
assert boot.read_bytes()==(W/'boot_before.bin').read_bytes()
final=get('/api/v1/status');assert final['badFrames']==0
result=dict(before=before,html_bytes=len(html),url=url,pages=pages,accepted=accepted,echo=echo,count=count,after=final,boot_unchanged=True,boot64k_sha256=hashlib.sha256(boot.read_bytes()).hexdigest(),static_ram=51644,previous_static_ram=51628,flash_used=366572,previous_flash_used=350724,physical_outputs_written=False,local_site_argument_used=False)
(W/'HARDWARE_WEB.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(webSource='device',cacheHit=before['resources']['cacheHit'],pages=list(pages),echo=echo['value'],bad_frames=final['badFrames'],boot_unchanged=True)))
