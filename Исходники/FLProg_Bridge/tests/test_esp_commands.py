import subprocess,json,struct,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,default=Path(r'E:\SAI\FLProg_Network\_work\esp32_commands_20261029'));parser.add_argument('--worker',default='command_web_preview_peer_final.exe');args=parser.parse_args();w=args.work
class Peer:
 def __init__(self,fault=''):self.p=subprocess.Popen([str((w/args.worker).resolve())]+([fault] if fault else []),stdin=subprocess.PIPE,stdout=subprocess.PIPE);self.token='';self.session=''
 def call(self,op='',**kw):
  fields=[kw.get('method','POST'),kw.get('path','/plc-api/start'),op,kw.get('channel','0'),kw.get('token',self.token),kw.get('cookie','flpadmin=0123456789abcdef0123456789abcdef'),kw.get('ticket',''),kw.get('offset',''),kw.get('count',''),kw.get('channels',''),kw.get('enable',''),kw.get('session',self.session),kw.get('requestId',''),kw.get('payload','')]
  self.p.stdin.write((' '.join(str(x).encode().hex() or '-' for x in fields)+'\n').encode());self.p.stdin.flush();code,body=self.p.stdout.readline().decode().split();return int(code),json.loads(bytes.fromhex(body)) if body!='-' else {}
 def result(self,ticket):return self.call(method='GET',path='/plc-api/result',ticket=ticket)[1]
 def req(self,op,**kw):
  code,d=self.call(op,**kw);assert code==202,(code,d);r=self.result(d['ticket']);self.session=r['session'];return r
 def setup(self):
  code,d=self.call(method='GET',path='/plc-api/session');assert code==200;self.token=d['token'];assert self.req('hello')['state']==3
 def control(self,enable):return self.call(path='/plc-api/control',enable=enable)
 def stats(self):return self.call(method='STATS')[1]
 def close(self):self.p.terminate();self.p.wait()
def payload(channel,value):return (bytes([channel,1])+struct.pack('<i',value)).hex()
results={};p=Peer()
try:
 p.setup();data=payload(135,1234)
 assert p.call('write',requestId=1,payload=data)[0]==403
 assert p.call(path='/plc-api/control',enable=1,token='wrong')[0]==403
 assert p.control(1)[0]==200
 assert p.call(method='GET',path='/plc-api/session')[1]['readOnly'] is False
 assert p.call('write',requestId=1,payload=data,session='0'*16)[0]==409
 for bad in ['010001','8704','87020000807f','870300','xx','87']:
  assert p.call('write',requestId=1,payload=bad)[0]==400,bad
 accepted=p.req('write',requestId=1,payload=data);assert accepted['state']==3
 value=bytes.fromhex(p.req('read',channel=135)['payloadHex']);assert struct.unpack('<i',value[1:])[0]==1234
 for changed in [data,payload(135,3333)]:assert p.call('write',requestId=1,payload=changed)[0]==409
 assert p.stats()['commands']==1
 refused=p.req('write',requestId=2,payload=payload(135,20000));assert refused['state']==5 and refused['status']==5
 assert p.stats()['commands']==1
 assert p.control(0)[0]==200;assert p.call('write',requestId=3,payload=data)[0]==403
 p.control(1);p.req('hello');assert p.call('write',requestId=3,payload=data)[0]==403
 p.control(1);p.call(method='RESET');stale=p.req('write',requestId=3,payload=data);assert stale['state']==5 and stale['status']==3
 assert p.stats()['commands']==1
 results['normal']={'accepted_and_readback':1234,'duplicate_and_modified_duplicate_rejected':True,'default_off':True,'csrf':True,'invalid_payloads':6,'plc_range_policy':True,'new_hello_disables':True,'reset_session_rejected':True,'commands':1}
finally:p.close()
p=Peer('drop-ack')
try:
 p.setup();p.control(1);code,d=p.call('write',requestId=1,payload=payload(135,2222));assert code==202;ticket=d['ticket'];assert p.stats()['commands']==1
 p.call(method='ADVANCE');assert p.result(ticket)['state']==4
 for _ in range(5):p.result(ticket)
 assert p.stats()['commands']==1
 assert p.call('write',requestId=1,payload=payload(135,2222))[0]==403
 p.req('hello');p.control(1);assert p.call('write',requestId=1,payload=payload(135,2222))[0]==409
 assert p.stats()['commands']==1
 results['lost_ack']={'timeout':True,'accepted_once':True,'poll_no_replay':True,'duplicate_after_new_session_rejected':True}
finally:p.close()
(w/'COMMAND_CHECKS.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(json.dumps(results))
