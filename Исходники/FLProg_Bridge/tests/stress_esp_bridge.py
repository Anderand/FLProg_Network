import subprocess,json,struct,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,default=Path(r'E:\SAI\FLProg_Network\_work\esp32_stability_20261029'));parser.add_argument('--worker',default='stability_preview_peer.exe');args=parser.parse_args();w=args.work
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
import time,hashlib,ctypes
from ctypes import wintypes
old=Path(r'E:\SAI\FLProg_Network\_work\esp32_commands_20261029')
expected=(old/'fixture.gz').read_bytes();expected_sha=hashlib.sha256(expected).hexdigest()
class Counters(ctypes.Structure):
 _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True);kernel.OpenProcess.restype=ctypes.c_void_p;kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.CloseHandle.argtypes=[ctypes.c_void_p];psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(Counters),wintypes.DWORD]
def memory(pid):
 handle=kernel.OpenProcess(0x410,False,pid);assert handle
 try:
  c=Counters();c.cb=ctypes.sizeof(c);assert psapi.GetProcessMemoryInfo(handle,ctypes.byref(c),c.cb);return c.PrivateUsage
 finally:kernel.CloseHandle(handle)
p=Peer();started=time.perf_counter();samples=[];interrupted=0
try:
 p.setup()
 for cycle in range(1000):
  p.req('hello');assert p.call(method='GET',path='/plc-api/session')[1]['readOnly'] is True
  meta=bytes.fromhex(p.req('resources')['payloadHex']);size=int.from_bytes(meta[4:8],'little');assert size==len(expected);data=b''
  while len(data)<size:
   part=bytes.fromhex(p.req('chunk',offset=len(data),count=min(224,size-len(data)))['payloadHex']);assert int.from_bytes(part[:4],'little')==len(data);data+=part[4:]
   if cycle%10==0 and len(data)==2240:
    p.call(method='RESET');broken=p.req('chunk',offset=len(data),count=224);assert broken['state']==5 and broken['status']==3;interrupted+=1
    p.req('hello');data=b''
    # Once per cycle only; resumed transfer starts from byte zero.
    while len(data)<size:
     part=bytes.fromhex(p.req('chunk',offset=len(data),count=min(224,size-len(data)))['payloadHex']);assert int.from_bytes(part[:4],'little')==len(data);data+=part[4:]
    break
  assert data==expected and hashlib.sha256(data).hexdigest()==expected_sha
  p.control(1);p.call(method='OFFLINE');before=p.stats()['commands'];assert p.call('write',requestId=cycle+1,payload=payload(135,cycle))[0]==503
  p.call(method='ONLINE');assert p.call('write',requestId=cycle+1,payload=payload(135,cycle))[0]==403
  p.req('hello');code,mode=p.control(1);assert code==200;request=mode['nextId']
  accepted=p.req('write',requestId=request,payload=payload(135,cycle));assert accepted['state']==3
  assert p.call('write',requestId=request,payload=payload(135,cycle+1))[0]==409
  read=bytes.fromhex(p.req('read',channel=135)['payloadHex']);assert struct.unpack('<i',read[1:])[0]==cycle;assert p.stats()['commands']==before+1
  p.call(method='TCPON');assert p.call('read',channel=135)[0]==409;p.call(method='TCPOFF');p.req('hello');assert p.call('write',requestId=request+1,payload=payload(135,cycle))[0]==403
  if cycle in (19,199,399,599,799,999):samples.append({'cycle':cycle+1,'native_private_bytes':memory(p.p.pid)})
  if cycle%200==199:print('PASS cycles',cycle+1,flush=True)
 p.call(method='CHANGEPROJECT');changed=p.req('read',channel=135);assert changed['state']==5 and changed['status']==3
 changed_hello=json.loads(bytes.fromhex(p.req('hello')['payloadHex']));assert changed_hello['identity']['projectId']=='XLE4D-30MT';(w/'CHANGED_PROJECT_HELLO.json').write_text(json.dumps(changed_hello),encoding='utf-8')
 p.call(method='RESTOREPROJECT');p.req('read',channel=135);restored=json.loads(bytes.fromhex(p.req('hello')['payloadHex']));assert restored['identity']['projectId']=='FLE4D-30MT';assert p.call(method='GET',path='/plc-api/session')[1]['readOnly'] is True
 stats=p.stats();assert stats['commands']==1000
 growth=samples[-1]['native_private_bytes']-samples[0]['native_private_bytes'];assert growth<1048576,('Unexpected native growth',samples)
 report={'cycles':1000,'verified_full_downloads':1000,'interrupted_downloads_restarted':interrupted,'successful_commands':1000,'duplicate_rejections':1000,'offline_write_rejections':1000,'tcp_contentions':1000,'fresh_session_requires_opt_in':True,'stats':stats,'memory_samples':samples,'native_private_growth_after_warmup':growth,'elapsed_seconds':round(time.perf_counter()-started,3),'hardware':False,'esp_heap_measured':False,'firmware_changed':False,'project_change_detected':True,'original_project_restored_read_only':True}
 (w/'STABILITY_CHECKS.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
finally:p.close()
