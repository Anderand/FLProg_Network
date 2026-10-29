import subprocess,json,hashlib,struct,argparse
from pathlib import Path
from urllib.parse import urlencode
parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,default=Path(r'E:\SAI\FLProg_Network\_work\esp32_lan_web_20261029'));w=parser.parse_args().work
p=subprocess.Popen([str(w/'lan_web_preview_peer.exe')],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
def call(dest='admin',method='GET',path='/config',cookie='',data=None,query=''):
 body=urlencode(data or {});fields=[dest,method,path,cookie,body,query];p.stdin.write((' '.join(v.encode().hex() or '-' for v in fields)+'\n').encode());p.stdin.flush();c,b,h=p.stdout.readline().decode().split();return int(c),bytes.fromhex(b) if b!='-' else b'',bytes.fromhex(h).decode() if h!='-' else ''
def login():
 c,b,h=call(method='POST',path='/login',data={'password':'demo12345'});assert c==303
 return next(v.split(': ',1)[1].split(';')[0] for v in h.splitlines() if v.startswith('Set-Cookie:'))
def config(cookie):c,b,h=call(cookie=cookie);assert c==200;d=json.loads(b);assert b'saved-demo-pass' not in b and 'password' not in d;return d
cookie=login();report={}
try:
 for kind in (0,1,2):
  d=config(cookie);data={'token':d['token'],'network':kind,'rx':32 if kind==2 else 16,'tx':33 if kind==2 else 17,'baud':115200,'format':0,'port':3234,'idle':60000,'sck':18,'miso':19,'mosi':23,'cs':5,'mdc':23,'mdio':18,'power':-1,'reset':-1,'phy':0,'clock':0}
  c,b,h=call(method='POST',path='/save',cookie=cookie,data=data);assert c==200,b
  call(method='REBOOT',path='');assert call(cookie=cookie)[1].startswith(b'<!doctype')
  cookie=login();d=config(cookie);assert d['network']==kind and d['ssid']=='stand-wifi' and d['passwordStored'] is True
  c,stats,_=call(method='STATS',path='');stats=json.loads(stats);assert stats['networkReady'] and stats['legacyPreserved'] and stats['wifiReady']==(kind==0)
  assert call(dest='project',path='/')[0]==403
  c,html,_=call(dest='project',path='/',cookie=cookie);assert c==200 and len(html)>20000
  c,body,_=call(dest='project',path='/plc-api/session',cookie=cookie);token=json.loads(body)['token'];assert token!=d['token']
  def request(op,**kw):
   c,b,_=call(dest='project',method='POST',path='/plc-api/start',cookie=cookie,data={'token':token,'channel':'0','op':op,**kw});assert c==202,(c,b)
   ticket=json.loads(b)['ticket'];c,b,_=call(dest='project',path='/plc-api/result',cookie=cookie,query=urlencode({'ticket':ticket}));result=json.loads(b);assert c==200 and result['state']==3,result
   return result,bytes.fromhex(result['payloadHex'])
  hello,_=request('hello');_,meta=request('resources');size=int.from_bytes(meta[4:8],'little');data=b'';chunks=0
  while len(data)<size:
   _,part=request('chunk',offset=len(data),count=min(224,size-len(data)));assert int.from_bytes(part[:4],'little')==len(data);data+=part[4:];chunks+=1
  assert data==(w/'fixture.gz').read_bytes() and hashlib.sha256(data).digest()==meta[12:]
  _,values=request('batch',channels='135,121,42');assert values[0]==3
  call(method='OFFLINE',path='');assert call(dest='project',path='/plc-api/session',cookie=cookie)[0]==503
  call(method='ONLINE',path='');assert call(dest='project',path='/plc-api/session',cookie=cookie)[0]==200
  report[str(kind)]={'authenticated_settings':True,'old_wifi_preserved':True,'legacy_record_preserved':True,'wifi_ready':stats['wifiReady'],'network_ready':stats['networkReady'],'viewer_token_distinct':True,'full_flash_package_bytes':len(data),'chunks':chunks,'sha_verified':True,'batch':True,'offline_503_and_recovery':True}
 (w/'LAN_TRANSFER_CHECKS.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
finally:p.terminate();p.wait()
