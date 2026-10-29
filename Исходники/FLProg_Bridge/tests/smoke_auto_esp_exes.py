# coding: utf-8
import sys,threading,subprocess,tempfile,json,time,urllib.request,socket
from pathlib import Path
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\esp32_bridge_20261029');a=Path(r'E:\SAI\FLProg_Network\_work\bridge_auto_20261029')
sys.path[:0]=[str(r/'flprog_bridge/tests'),str(r/'flprog_webui_next/tools')]
from test_tcp_port import Server
from test_web_project import document
results={}
def get(url):
 with urllib.request.urlopen(url,timeout=2) as f:return json.load(f)
server=Server();threading.Thread(target=server.serve_forever,daemon=True).start()
exe=w/'bridge_dist/FLProg_Bridge/FLProg_Bridge.exe';status=w/'EXE_STATUS_FINAL.json'
p=subprocess.Popen([str(exe),'--headless','--tcp','127.0.0.1:'+str(server.server_address[1]),'--no-browser','--status-file',str(status)])
try:
 deadline=time.monotonic()+40
 while time.monotonic()<deadline:
  try:
   url=json.loads(status.read_text(encoding='utf-8'))['url'];state=get(url+'api/v1/status');break
  except (OSError,ValueError):time.sleep(.2)
 else:raise RuntimeError('Frozen Bridge did not start')
 assert state['online'] and state['webSource']=='device' and not state['writesEnabled'] and state['version']=='0.4.0-preview.1',state
 results['bridge']=dict(version=state['version'],webSource=state['webSource'],identity=state['device']['identity'],writesEnabled=state['writesEnabled'],tcp_target='local mock UART peer',hardware=False)
finally:p.terminate();p.wait(timeout=5);server.shutdown();server.server_close()
with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
exe=a/'editor_final_dist/FLProg_WebUI_Editor/FLProg_WebUI_Editor.exe';p=subprocess.Popen([str(exe),str(port),'--no-browser'])
try:
 url='http://127.0.0.1:'+str(port);deadline=time.monotonic()+30
 while time.monotonic()<deadline:
  try:get(url+'/api/network-api');break
  except OSError:time.sleep(.2)
 else:raise RuntimeError('Frozen editor did not start')
 with tempfile.TemporaryDirectory(prefix='flprog_auto_exe_') as folder:
  doc=document();doc['project']['id']='auto-exe';doc['projectFolder']=folder;doc['installToIde']=False
  req=urllib.request.Request(url+'/api/bridge/export',data=json.dumps(doc).encode('utf-8'),headers={'Content-Type':'application/json'})
  response=get_response=None
  with urllib.request.urlopen(req,timeout=10) as f:response=json.load(f)
  header=Path(response['identityHeader']);manifest=json.loads((header.parent.parent/'WEBUI_COMPATIBILITY.json').read_text(encoding='utf-8'))
  assert manifest['bridgeBlockApi']==1 and manifest['catalogApi']==1 and (header.parent/'auto-exe_bridge_entry.h').is_file()
  assert (header.parent.parent/'Bridge_UART/Basic/FLProg_Bridge_UART.ubi').is_file()
  results['editor']=dict(automatic_bridge_binding=True,projectId='auto-exe',catalogApi=1,bridgeBlockApi=1,ide_unchanged=True)
finally:p.terminate();p.wait(timeout=5)
(w/'EXE_SMOKE.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(results,ensure_ascii=False))
