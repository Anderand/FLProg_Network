"""Local preview of the actual ESP HTML + native C++ HTTP handlers/protocol."""
import argparse,json,threading,subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
p=argparse.ArgumentParser();p.add_argument('--worker',type=Path,required=True);p.add_argument('--status-file',type=Path,required=True);p.add_argument('--fault',default='');args=p.parse_args()
worker=subprocess.Popen([str(args.worker.resolve())]+([args.fault] if args.fault else []),stdin=subprocess.PIPE,stdout=subprocess.PIPE);lock=threading.Lock()
cookie='flpadmin=0123456789abcdef0123456789abcdef'
def call(method,path,values,headers):
 fields=[method,path,values.get('op',''),values.get('channel',''),values.get('token',''),headers,values.get('ticket',''),values.get('offset',''),values.get('count',''),values.get('channels',''),values.get('enable',''),values.get('session',''),values.get('requestId',''),values.get('payload','')]
 wire=' '.join(v.encode('utf-8').hex() or '-' for v in fields)+'\n'
 with lock:
  worker.stdin.write(wire.encode());worker.stdin.flush();response=worker.stdout.readline().decode('ascii').strip()
 code,body=response.split(' ',1);return int(code),bytes.fromhex(body) if body!='-' else b''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):self.handle_call('GET')
 def do_POST(self):self.handle_call('POST')
 def handle_call(self,method):
  path=urlsplit(self.path);values={k:v[0] for k,v in parse_qs(path.query,keep_blank_values=True).items()}
  if method=='POST':
   size=int(self.headers.get('Content-Length','0'))
   if not 0<=size<=1024:self.send_error(413);return
   values.update({k:v[0] for k,v in parse_qs(self.rfile.read(size).decode('utf-8'),keep_blank_values=True).items()})
  root=path.path=='/' and method=='GET'
  code,body=call('STATS' if path.path=='/__test/stats' else method,'/' if root else path.path,values,cookie if root else self.headers.get('Cookie',''))
  html=(path.path in ('/','/plc') and code==200)
  if html:
   body=body.replace(b'<script>',b'<script>window.__FLP_NATIVE_PREVIEW=true;</script><script>',1)
  self.send_response(code);self.send_header('Content-Type','text/html; charset=utf-8' if html else 'application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Frame-Options','DENY')
  if root:self.send_header('Set-Cookie',cookie+'; Path=/; HttpOnly; SameSite=Strict')
  self.end_headers();self.wfile.write(body)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True
url='http://127.0.0.1:'+str(server.server_port)+'/'
args.status_file.write_text(json.dumps(dict(url=url,hardware=False,native_handler=True)),encoding='utf-8');print(url,flush=True)
try:server.serve_forever()
finally:server.server_close();worker.terminate();worker.wait(timeout=3)
