# coding: utf-8
"""Explicit stand test after the user disconnects PLC Ethernet, USB stays on."""
import json,subprocess,time,urllib.error,urllib.request
from pathlib import Path
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_web_20261028\user4')
base='http://127.0.0.1:64016'
def get(path):
    for attempt in range(6):
        try:
            with urllib.request.urlopen(base+path,timeout=5) as response:return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code!=409 or attempt==5:raise
            time.sleep(.15)
def post(number,kind,value,session):
    request=urllib.request.Request(base+'/api/v1/channels/'+str(number),data=json.dumps(dict(type=kind,value=value,session=session)).encode(),headers={'Content-Type':'application/json','X-FLProg-Bridge':'1'})
    try:
        with urllib.request.urlopen(request,timeout=5) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as response:return response.code,json.load(response)
before=get('/api/v1/status');assert before['online'] and not before['demo']
assert before['device']['identity']['firmware']=='1.0.8-BRIDGE-WEB'
pages={page:get('/flprog-webui/state?page='+page) for page in ('main','diagnostics','inputs','outputs')}
assert pages['diagnostics']['values']['network_ready'] is False
assert pages['diagnostics']['values']['network_ip']=='0.0.0.0'
baseline=pages['outputs']['values']
session=before['session'];count=get('/api/v1/channels/243')['value']
code,accepted=post(241,'int32',53002,session);assert code==200,(code,accepted)
time.sleep(.15)
echo=get('/api/v1/channels/242');new_count=get('/api/v1/channels/243')
assert echo['value']==53002 and new_count['value']==count+1
# The user is operating DO1 now: preserve outputs and do not reset their PLC.
enabled=pages['outputs']
assert enabled['values']['web_control_ready'] and enabled['values']['output_source']=='Веб'
reads=[]
for unused in range(10):
    reads.append(get('/flprog-webui/state?page=main'))
    time.sleep(.15)
after_pages={page:get('/flprog-webui/state?page='+page) for page in pages}
assert after_pages['diagnostics']['values']['network_ready'] is False
assert after_pages['diagnostics']['values']['network_ip']=='0.0.0.0'
assert after_pages['diagnostics']['values']['system_uptime']>pages['diagnostics']['values']['system_uptime']
assert get('/api/v1/channels/242')['value']==53002
final=get('/api/v1/status');assert final['badFrames']==0
assert final['session']==session
report=dict(user_confirmed_ethernet_unplugged=True,usb_and_power_connected=True,before=before,pages=pages,echo=echo,count_before=count,count_after=new_count,enabled_without_ethernet=enabled,after=final,after_pages=after_pages,read_samples=len(reads),physical_outputs_written=False,reset_performed=False,reset_skip_reason='User is operating DO1; physical outputs and mode were preserved.',bad_frames=final['badFrames'])
(W/'NO_ETHERNET.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(pages=list(pages),network_ready=False,ip='0.0.0.0',echo=echo['value'],control_enabled_without_ethernet=True,physical_outputs_written=False,reset_performed=False,bad_frames=final['badFrames'])))
