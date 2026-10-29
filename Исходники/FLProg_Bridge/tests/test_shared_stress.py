"""Software-only MQTT broker faults while actual PLC blocks share UART with WebUI."""
import argparse,json,re,socket,subprocess,threading,traceback
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);w=p.parse_args().work
listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(1);listener.settimeout(30)
errors=[];seen=[];connections=0
def exact(s,n):
 b=b''
 while len(b)<n:
  part=s.recv(n-len(b));assert part;b+=part
 return b
def packet(s):
 kind=exact(s,1)[0];size=0;shift=0
 while True:
  b=exact(s,1)[0];size+=(b&127)<<shift;shift+=7;assert shift<=28
  if not b&128:break
 assert size<1024
 return kind,exact(s,size)
def field(b,at):
 size=int.from_bytes(b[at:at+2],'big');return b[at+2:at+2+size],at+2+size
def message(s,text):
 b=b'\0\x0bplc/command'+text.encode();s.sendall(bytes([0x30,len(b)])+b)
def accept():
 global connections
 s=listener.accept()[0];s.settimeout(30);connections+=1
 kind,b=packet(s);assert kind==16
 proto,at=field(b,0);assert proto==b'MQTT';at+=4
 client,at=field(b,at);user,at=field(b,at);password,at=field(b,at)
 assert client==b'PLC-blocks' and user==b'plc-user' and password==b'test-only-password'
 s.sendall(bytes.fromhex('20020000'));kind,b=packet(s);assert kind==0x82
 topic,at=field(b,2);assert topic==b'plc/command';s.sendall(bytes([0x90,3])+b[:2]+b'\0')
 return s
def broker():
 s=None
 try:
  s=accept();kind,b=packet(s);topic,at=field(b,0);assert kind==0x30 and topic==b'plc/value' and b[at:]==b'A'*400
  message(s,'on!!!')
  for i in range(200):
   kind,b=packet(s);topic,at=field(b,0);assert kind==0x30 and topic==b'plc/value'
   assert b[at:]==('seq:'+str(i)).encode(),(i,b[at:]);seen.append(i);message(s,'ack:'+str(i))
   if (i+1)%20==0 and i+1<200:
    s.shutdown(socket.SHUT_RDWR);s.close();s=accept();message(s,'ready:'+str(connections))
  kind,b=packet(s);assert kind==0xe0 and not b
  try:assert s.recv(1)==b''
  except ConnectionResetError:pass
 except BaseException:errors.append(traceback.format_exc())
 finally:
  if s:s.close()
t=threading.Thread(target=broker,daemon=True);t.start();lines=[]
with (w/'STRESS_STDERR.log').open('wb') as err:
 proc=subprocess.Popen([str(w/'mqtt_blocks_stress.exe'),'localhost',str(listener.getsockname()[1])],stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf-8')
 for line in proc.stdout:
  lines.append(line);print(line.rstrip(),flush=True)
 rc=proc.wait(timeout=10)
t.join(5);listener.close();(w/'STRESS.log').write_text(''.join(lines),encoding='utf-8')
assert rc==0 and not errors and not t.is_alive(),(rc,len(seen),connections,errors,(w/'STRESS_STDERR.log').read_text(errors='replace'))
assert seen==list(range(200)) and connections==10
match=re.search(r'STRESS cycles=200 reconnects=9 reads=(\d+) chunks=(\d+) bytes=(\d+) private_start=(\d+) private_end=(\d+)',''.join(lines));assert match
reads,chunks,byte_count,start,end=map(int,match.groups())
samples=[int(x) for x in re.findall(r'PROGRESS.*private=(\d+)',''.join(lines))]
result=dict(software_only=True,cycles=200,mqtt_publications=201,broker_disconnects=9,tcp_connections=connections,publications_replayed=0,web_reads=reads,flash_chunks=chunks,complete_flash_packages=chunks//69,flash_bytes=byte_count,native_private_samples=samples,native_private_after_warmup=start,native_private_end=end,esp_heap_measured=False,hardware_tested=False)
(w/'STRESS_CHECKS.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
