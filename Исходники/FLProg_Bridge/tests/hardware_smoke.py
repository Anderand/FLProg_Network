# coding: utf-8
"""Explicit COM5/FLE4D smoke. Writes only the dedicated RAM echo channel 241."""
from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[1]
W=Path(r'E:\SAI\FLProg_Network\_work\bridge_20261028\hardware')
sys.path[:0]=[str(ROOT),str(W.parent/'deps')]
from app import serial_port
from client import Client,BridgeError,encode_value,decode_value

c=Client(serial_port('COM5',115200),timeout=2.0)
results={}
try:
    results['identity']=c.handshake();assert results['identity']['identity']['firmware']=='1.0.6-BRIDGE'
    assert results['identity']['identity']['model']=='FLE4D-30MT / STM32F407VG'
    def read(ch):return decode_value(c.request(1,1,bytes([ch])))
    network_until=time.monotonic()+30
    while not read(1) and time.monotonic()<network_until:time.sleep(.25)
    results['ip']=read(0);results['network_ready']=read(1);results['mac']=read(2)
    results['model']=read(5);results['version']=read(6)
    channels={}
    # Metadata covers both system diagnostics and real DI/AI/DO/AO readback.
    for ch in [0,1,2,5,6,11,13,17,22,40,101,116,117,120,121,134,135,136,137,241,242,243]:
        meta=c.request(1,2,bytes([ch]));value=read(ch)
        channels[str(ch)]={'id':meta[3:].decode('utf-8'),'type':meta[1],'direction':meta[2],'value':value}
    results['channels']=channels
    before=read(243);sent=31725
    c.request(1,3,bytes([241])+encode_value('int32',sent),c.session)
    # Distinct readback + execution count, never accept the command slot alone as proof.
    until=time.monotonic()+2
    while time.monotonic()<until:
        actual=read(242);count=read(243)
        if actual==sent and count==before+1:break
    assert actual==sent and count==before+1
    results['software_echo']=dict(sent=sent,result=actual,count_before=before,count_after=count)
    try:c.request(1,3,bytes([121])+encode_value('bool',True),c.session)
    except BridgeError as e:results['physical_output_write_blocked']=e.status==403
    else:raise AssertionError('DO write was unexpectedly accepted')
    assert results['physical_output_write_blocked']
    started=time.monotonic()
    for _ in range(100):assert read(242)==sent
    results['read_100_seconds']=time.monotonic()-started
    results['bad_frames']=c.decoder.errors;results['requests']=c.exchanges
    results['session']=str(c.session)
    results['hardware_tested']=True
    (W/'COM_HARDWARE.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False,indent=2))
finally:c.close()
