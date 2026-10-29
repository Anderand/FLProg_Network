# coding: utf-8
"""Re-upload the same image by OTA; check old COM session cannot survive reset."""
from pathlib import Path
import gzip,json,sys,time,urllib.request
R=Path(__file__).resolve().parents[2];W=Path(r'E:\SAI\FLProg_Network\_work\bridge_20261028\hardware')
sys.path[:0]=[str(R/'flprog_bridge'),str(W.parent/'deps'),str(R/'hardware_gates/STM32_W5500_GATE/OTA_APP_FLE4D'),str(R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER')]
from app import serial_port
from client import Client,BridgeError,decode_value
from upload_fle4d_ota import upload_image
from ota_discovery import probe

original=json.loads((W/'COM_HARDWARE.json').read_text(encoding='utf-8'))
host=original['ip'];assert host=='192.168.100.19' and original['mac']=='78:AC:C0:5C:44:8D'
info=probe(host,3233,2);assert info and '1.0.6-BRIDGE' in info['detail'] and 'FLE4D-30MT' in info['detail']
request=urllib.request.Request('http://'+host+'/',headers={'Accept-Encoding':'gzip'})
with urllib.request.urlopen(request,timeout=5) as response:
    html=response.read();encoding=response.headers.get('Content-Encoding');status=response.status
    if encoding=='gzip':html=gzip.decompress(html)
assert status==200 and b'flprog-webui' in html
c=Client(serial_port('COM5',115200),timeout=1.5);report=dict(before=info,web_status=status)
try:
    c.handshake();old=c.session;build=json.loads((W/'bridge_BUILD.json').read_text());blob=Path(build['bin']).read_bytes()
    report['staged_bytes']=upload_image(host,blob,'',timeout=30);assert report['staged_bytes']==len(blob)
    deadline=time.monotonic()+20
    reset_error=None
    while time.monotonic()<deadline:
        try:c.request(0,2);time.sleep(.15)
        except BridgeError as e:reset_error=str(e);break
    assert reset_error and not c.online,'No reset/session invalidation detected'
    report['old_session_rejected']=True;report['reset_error']=reset_error
    deadline=time.monotonic()+20
    while True:
        try:c.handshake();break
        except BridgeError:
            if time.monotonic()>deadline:raise
            time.sleep(.3)
    assert c.session!=old
    echo=decode_value(c.request(1,1,bytes([242])));count=decode_value(c.request(1,1,bytes([243])))
    assert echo==0 and count==0,'An old command was replayed after reset'
    report.update(new_identity=c.info,new_session=str(c.session),old_session=str(old),echo_after_reset=echo,count_after_reset=count,automatic_replay=False)
    deadline=time.monotonic()+40
    while True:
        ready=decode_value(c.request(1,1,b'\x01'))
        if ready:break
        if time.monotonic()>deadline:raise AssertionError('DHCP did not recover')
        time.sleep(.25)
    ip=decode_value(c.request(1,1,b'\0'));report['ip_after_reset']=ip
    after=probe(ip,3233,2);assert after and '1.0.6-BRIDGE' in after['detail'];report['after']=after
    (W/'RESTART_HARDWARE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
finally:c.close()
