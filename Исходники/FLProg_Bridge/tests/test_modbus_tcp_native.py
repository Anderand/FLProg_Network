import socket,struct,subprocess,json,time,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,default=Path(r'E:\SAI\FLProg_Network\_work\modbus_lan_bridge_20261029'));args=parser.parse_args();w=args.work.resolve()
def exact(sock,n):
 b=b''
 while len(b)<n:
  v=sock.recv(n-len(b));assert v,'closed early';b+=v
 return b
def adu(tid,pdu,unit=1):return struct.pack('>HHHB',tid,0,len(pdu)+1,unit)+pdu
def receive(s,tid):
 h=exact(s,7);t,protocol,size,unit=struct.unpack('>HHHB',h);assert t==tid and protocol==0 and unit==1;return exact(s,size-1)
def call(s,tid,pdu,fragment=False):
 data=adu(tid,pdu)
 if fragment:
  for b in data:s.sendall(bytes([b]))
 else:s.sendall(data)
 return receive(s,tid)
results={}
for allowed in (False,True):
 p=subprocess.Popen([str(w/'modbus_tcp_native_server.exe')]+(['--allow-writes'] if allowed else []),stdout=subprocess.PIPE)
 try:
  info=json.loads(p.stdout.readline());s=socket.create_connection((info['host'],info['port']),timeout=4)
  with s:
   assert call(s,1,bytes.fromhex('0300000001'),True)==bytes.fromhex('030204d2')
   r=call(s,2,bytes.fromhex('060000002a'))
   if not allowed:assert r==bytes.fromhex('8601')
   else:
    assert r==bytes.fromhex('060000002a');assert call(s,3,bytes.fromhex('0300000001'))==bytes.fromhex('0302002a')
    for i in range(20):
     assert call(s,10+i*2,bytes([6,0,1,0,i]))==bytes([6,0,1,0,i]);assert call(s,11+i*2,bytes.fromhex('0300010001'))==bytes([3,2,0,i])
    # Coalesced TCP requests preserve separate transaction IDs.
    s.sendall(adu(100,bytes.fromhex('0300000001'))+adu(101,bytes.fromhex('0300010001')));assert receive(s,100)==bytes.fromhex('0302002a');assert receive(s,101)==bytes([3,2,0,19])
    multi=bytes([16,0,0,0,123,246])+b''.join(struct.pack('>H',i) for i in range(123));r=call(s,102,multi);assert r==bytes.fromhex('100000007b'),r.hex();assert len(call(s,103,bytes.fromhex('030000007d')))==252
    assert call(s,104,bytes.fromhex('030000007e'))==bytes.fromhex('8303')
   s.sendall(bytes.fromhex('000100010006010300000001'))
   try:assert s.recv(1)==b''
   except ConnectionResetError:pass
  # Reconnect creates a fresh UART session; no stale write is replayed.
  with socket.create_connection((info['host'],info['port']),timeout=4) as s:
   count=call(s,200,bytes.fromhex('04007c0001'));assert count==bytes([4,2,0,22 if allowed else 0]),count
  results['writes_enabled' if allowed else 'read_only']={'fragmented_request':True,'pipeline':allowed,'max_request_response':allowed,'invalid_mbap_closes':True,'reconnect_no_replay':True,'accepted_commands':22 if allowed else 0}
 finally:p.terminate();p.wait()
(w/'TCP_CHECKS.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(json.dumps(results))
