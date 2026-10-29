import json,sys,urllib.request,time
from pathlib import Path
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028');sys.path.insert(0,str(r/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER'))
from ota_discovery import probe
info=probe('192.168.100.19',3233,3);assert info and '1.0.10-BRIDGE-LINK' in info['detail']
pages={}
for page in ('main','diagnostics','inputs','outputs'):
 for attempt in range(4):
  try:
   with urllib.request.urlopen('http://192.168.100.19/flprog-webui/state?page='+page,timeout=5) as f:pages[page]=json.load(f)
   break
  except OSError:
   if attempt==3:raise
   time.sleep(.2)
assert pages['diagnostics']['values']['firmware_version']=='1.0.10-BRIDGE-LINK'
(w/'HARDWARE_RECONNECTED.json').write_text(json.dumps(dict(ota=info,pages=pages,boot_unchanged=(w/'boot_before.bin').read_bytes()==(w/'boot_after.bin').read_bytes()),ensure_ascii=False,indent=2),encoding='utf-8');print('PASS: restored Ethernet, OTA identity and four HTTP pages')
