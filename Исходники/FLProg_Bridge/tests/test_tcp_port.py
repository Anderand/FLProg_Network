# coding: utf-8
import socket,socketserver,threading,subprocess,queue,select,time,sys,tempfile,json,unittest
from pathlib import Path
r=Path(__file__).resolve().parents[2];w=Path(r'E:\SAI\FLProg_Network\_work\esp32_bridge_20261029');sys.path[:0]=[str(r/'flprog_bridge')]
from tcp_port import TcpPort,endpoint
from client import Client,BridgeError
from device_web import device_site
from protocol import Decoder
class Handler(socketserver.BaseRequestHandler):
 def handle(self):
  if self.server.silent:
   decoder=Decoder();self.request.settimeout(.05)
   while True:
    try:raw=self.request.recv(512)
    except socket.timeout:continue
    if not raw:break
    self.server.frames.extend(decoder.feed(raw))
   return
  p=subprocess.Popen([str(Path(r'E:\SAI\FLProg_Network\_work\bridge_auto_20261029\basic_auto_peer.exe'))],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out=queue.Queue()
  def pump():
   while True:
    b=p.stdout.read(1)
    if not b:return
    out.put(b)
  thread=threading.Thread(target=pump,daemon=True);thread.start()
  try:
   while True:
    if select.select([self.request],[],[],.002)[0]:
     try:raw=self.request.recv(512)
     except ConnectionError:break
     if not raw:break
     # Deliberately split TCP input before the native UART peer.
     for i in range(0,len(raw),3):p.stdin.write(raw[i:i+3]);p.stdin.flush()
    pending=[]
    for i in range(17):
     try:pending.append(out.get_nowait())
     except queue.Empty:break
    if pending:
     try:self.request.sendall(b''.join(pending))
     except ConnectionError:break
  finally:
   p.stdin.close();p.wait(timeout=3);thread.join(timeout=1);p.stdout.close();p.stderr.close()
class Server(socketserver.ThreadingTCPServer):
 allow_reuse_address=True;daemon_threads=True
 def __init__(self,silent=False):super().__init__(('127.0.0.1',0),Handler);self.silent=silent;self.frames=[]
class TcpTests(unittest.TestCase):
 def setUp(self):self.server=None
 def tearDown(self):
  if self.server:self.server.shutdown();self.server.server_close()
 def start(self,silent=False):
  self.server=Server(silent);threading.Thread(target=self.server.serve_forever,daemon=True).start();return 'tcp://127.0.0.1:'+str(self.server.server_address[1])
 def test_endpoint_validation(self):
  self.assertEqual(endpoint('127.0.0.1:3234'),('127.0.0.1',3234));self.assertEqual(endpoint('tcp://[::1]:3234'),('::1',3234))
  for s in ('host','tcp://user:pass@host:3234','host:0','host:65536','host:abc','host:3234/path','host:3234?q=1','http://host:3234'):
   with self.subTest(value=s),self.assertRaises(ValueError):endpoint(s)
 def test_real_protocol_and_flash_over_fragmented_tcp(self):
  transport=TcpPort(self.start());c=Client(transport)
  try:
   first=c.handshake();self.assertEqual(first['identity']['projectId'],'auto-sample');self.assertEqual(c.read_channels([101])[101]['value'],0)
   with tempfile.TemporaryDirectory() as d:
    folder,report=device_site(c,cache=Path(d));self.assertFalse(report['cacheHit']);self.assertEqual(json.loads((folder/'project.json').read_text(encoding='utf-8'))['project']['id'],'auto-sample')
   old=c.session;transport.open();c.handshake();self.assertNotEqual(c.session,old);self.assertEqual(c.decoder.errors,0)
  finally:c.close()
 def test_timeout_sends_command_only_once(self):
  transport=TcpPort(self.start(silent=True));c=Client(transport,timeout=.1);c.online=True;c.session=123;c.info={'services':[1]}
  try:
   with self.assertRaises(BridgeError):c.request(1,3,b'command')
   time.sleep(.15);self.assertEqual(len(self.server.frames),1);self.assertFalse(c.online)
  finally:c.close()
if __name__=='__main__':unittest.main(verbosity=2)
