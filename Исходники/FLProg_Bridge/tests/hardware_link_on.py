from pathlib import Path
import sys,json,time
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028')
sys.path[:0]=[str(r/'flprog_bridge'),r'E:\SAI\FLProg_Network\_work\bridge_20261028\deps']
from app import serial_port
from client import Client
c=Client(serial_port('COM5',115200))
try:
 identity=c.handshake();assert identity['identity']['firmware']=='1.0.10-BRIDGE-LINK'
 doc=json.loads(Path(r'E:\SAI\FLProg_Network\_work\bridge_flash_20261028\generated_site\project.json').read_text(encoding='utf-8'));ids={x['id']:x['index'] for x in doc['channels']}
 values=c.read_channels([ids[x] for x in ('network_ready','network_ip','firmware_version')]);assert values[ids['network_ready']]['value'] is True
 (w/'LINK_ON.json').write_text(json.dumps(dict(identity=identity,values=values,ids=ids),ensure_ascii=False,indent=2),encoding='utf-8')
 print(identity['identity']['firmware'],values)
finally:c.close()
