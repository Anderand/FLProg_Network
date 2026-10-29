# coding: utf-8
"""Explicit local stand check; intentionally excluded from test_*.py discovery."""
import hashlib,json,subprocess,time,urllib.error,urllib.request
from pathlib import Path
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_web_20261028');U=W/'user4'
base='http://127.0.0.1:64016'
cli=r'C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe'
def get(path):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(base+path,timeout=5) as response:return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code!=409 or attempt==4:raise
            time.sleep(.2)
def post(number,value,session):
    request=urllib.request.Request(base+'/api/v1/channels/'+str(number),data=json.dumps(dict(type='int32',value=value,session=session)).encode(),headers={'Content-Type':'application/json','X-FLProg-Bridge':'1'})
    try:
        with urllib.request.urlopen(request,timeout=5) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as response:return response.code,json.load(response)
status=get('/api/v1/status');assert status['online'] and not status['demo']
assert status['device']['identity']['firmware']=='1.0.8-BRIDGE-WEB'
project=json.loads((U/'site/project.json').read_text(encoding='utf-8'))
pages={p['id']:get('/flprog-webui/state?page='+p['id']) for p in project['pages']}
assert pages['outputs']['values']['web_control'] is False
assert pages['outputs']['values']['ao_0']==0 and pages['outputs']['values']['do_01'] is False
assert pages['diagnostics']['values']['network_ip']=='192.168.100.19'
session=status['session'];code,accepted=post(241,52838,session);assert code==200,(code,accepted)
deadline=time.monotonic()+5
while time.monotonic()<deadline:
    echo=get('/api/v1/channels/242');count=get('/api/v1/channels/243')
    if echo['value']==52838:break
assert echo['value']==52838 and count['value']>=1
started=time.monotonic()
reset=subprocess.run([cli,'-c','port=SWD','sn=006500585900000B56314C4D','mode=UR','-rst','-run'],capture_output=True)
(U/'RESET.log').write_bytes(reset.stdout+reset.stderr);assert reset.returncode==0
deadline=time.monotonic()+45
while time.monotonic()<deadline:
    time.sleep(.5);after=get('/api/v1/status')
    if after['online'] and after['session']!=session:break
assert after['online'] and after['session']!=session,after
duration=time.monotonic()-started
echo_after=get('/api/v1/channels/242');count_after=get('/api/v1/channels/243')
assert echo_after['value']==0 and count_after['value']==0
code,stale=post(241,52838,session);assert code==409,(code,stale)
assert get('/api/v1/channels/243')['value']==0
after_pages={p['id']:get('/flprog-webui/state?page='+p['id']) for p in project['pages']}
assert after_pages['outputs']['values']['web_control'] is False
boot=U/'BOOT_AFTER.bin'
read=subprocess.run([cli,'-c','port=SWD','sn=006500585900000B56314C4D','mode=HOTPLUG','-u','0x08000000','0x10000',str(boot)],capture_output=True)
(U/'BOOT_AFTER.log').write_bytes(read.stdout+read.stderr);assert read.returncode==0 and boot.stat().st_size==65536
boot_hash=hashlib.sha256(boot.read_bytes()).hexdigest()
assert boot_hash==hashlib.sha256((U/'BOOT_BEFORE.bin').read_bytes()).hexdigest()
result=dict(before=status,pages=pages,echo=echo,count=count,reset_reconnect_seconds=round(duration,3),after=after,echo_after=echo_after,count_after=count_after,stale_write_status=code,stale_write=stale,after_pages=after_pages,boot64k_sha256=boot_hash,boot_unchanged=True,no_command_replay=True,physical_ethernet_unplugged=False)
(U/'COM_HARDWARE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(pages=list(pages),reconnect_seconds=round(duration,3),boot_unchanged=True,no_command_replay=True)))
