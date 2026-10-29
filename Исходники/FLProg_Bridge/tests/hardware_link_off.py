from pathlib import Path
import sys,json,time,socket,hashlib
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028')
sys.path[:0]=[str(r/'flprog_bridge'),r'E:\SAI\FLProg_Network\_work\bridge_20261028\deps']
from app import serial_port
from client import Client
from device_web import device_site
c=Client(serial_port('COM5',115200))
try:
 identity=c.handshake();assert identity['identity']['firmware']=='1.0.10-BRIDGE-LINK'
 doc=json.loads(Path(r'E:\SAI\FLProg_Network\_work\bridge_flash_20261028\generated_site\project.json').read_text(encoding='utf-8'));ids={x['id']:x['index'] for x in doc['channels']}
 samples=[]
 for i in range(40):
  values=c.read_channels([ids['network_ready'],ids['network_ip'],ids['system_uptime']]);samples.append(values);assert values[ids['network_ready']]['value'] is False,values;time.sleep(.05)
 cache=w/'offline_cache';assert not cache.exists()
 start=time.monotonic();folder,resources=device_site(c,cache=cache);elapsed=time.monotonic()-start;assert resources['cacheHit'] is False
 try:
  with socket.create_connection(('192.168.100.19',80),timeout=2):raise AssertionError('Ethernet still reachable')
 except OSError:pass
 assert c.decoder.errors==0
 result=dict(identity=identity,samples=samples,sample_count=len(samples),all_network_ready_false=True,ethernet_tcp_reachable=False,resources=resources,download_seconds=round(elapsed,3),bad_frames=c.decoder.errors,physical_outputs_written=False,boot64k_unchanged=(w/'boot_before.bin').read_bytes()==(w/'boot_after.bin').read_bytes())
 (w/'HARDWARE_LINK_OFF.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:result[k] for k in ['sample_count','all_network_ready_false','download_seconds','bad_frames','boot64k_unchanged']}))
finally:c.close()
