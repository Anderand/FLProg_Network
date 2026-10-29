import subprocess,json,hashlib,math,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,default=Path(r'E:\SAI\FLProg_Network\_work\esp32_full_web_20261029'));parser.add_argument('--worker',default='full_web_preview_peer_final.exe');args=parser.parse_args();w=args.work
class Peer:
 def __init__(self,fault=''): self.p=subprocess.Popen([str(w/args.worker)]+([fault] if fault else []),stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 def call(self,op='',**kw):
  fields=[kw.get('method','POST'),kw.get('path','/plc-api/start'),op,kw.get('channel','0'),kw.get('token',''),kw.get('cookie','flpadmin=0123456789abcdef0123456789abcdef'),kw.get('ticket',''),kw.get('offset',''),kw.get('count',''),kw.get('channels','')]
  self.p.stdin.write((' '.join(str(x).encode().hex() or '-' for x in fields)+'\n').encode());self.p.stdin.flush();code,body=self.p.stdout.readline().decode().split();return int(code),bytes.fromhex(body).decode() if body!='-' else ''
 def request(self,op,**kw):
  code,body=self.call(op,token=self.token,**kw);assert code==202,(code,body)
  ticket=json.loads(body)['ticket'];code,body=self.call(method='GET',path='/plc-api/result',ticket=ticket);d=json.loads(body);assert code==200 and d['state']==3,d;return bytes.fromhex(d['payloadHex'])
 def load(self):
  code,body=self.call(method='GET',path='/plc-api/session');assert code==200;self.token=json.loads(body)['token']
  hello=json.loads(self.request('hello'));meta=self.request('resources');size=int.from_bytes(meta[4:8],'little');data=b''
  while len(data)<size:
   part=self.request('chunk',offset=len(data),count=min(224,size-len(data)));assert int.from_bytes(part[:4],'little')==len(data);data+=part[4:]
  return hello,meta,data
 def close(self):self.p.terminate();self.p.wait()
results={}
for fault in ('','corrupt','wrong-id'):
 p=Peer(fault)
 try:
  hello,meta,data=p.load();expected=(w/'fixture.gz').read_bytes();results[fault or 'healthy']={'bytes':len(data),'sha':hashlib.sha256(data).hexdigest(),'identity':hello['identity']['projectId']}
  if not fault:assert data==expected;p.request('batch',channels='0,1');code,stats=p.call(method='STATS');results['stats']=json.loads(stats);assert results['stats']['chunks']==math.ceil(len(expected)/224)
  if fault=='corrupt':assert data!=expected
  if fault=='wrong-id':assert hello['identity']['projectId']!='FLE4D-30MT'
 finally:p.close()
(w/'NATIVE_TRANSFER.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(json.dumps(results))
