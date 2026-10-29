"""Software-only pair of HTTP ports, actual bridge C++ handlers, no PC Bridge/hardware."""
import argparse,json,threading,subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
p=argparse.ArgumentParser();p.add_argument('--worker',type=Path,required=True);p.add_argument('--status-file',type=Path,required=True);args=p.parse_args()
worker=subprocess.Popen([str(args.worker.resolve())],stdin=subprocess.PIPE,stdout=subprocess.PIPE);lock=threading.Lock()
def call(dest,method,path='',cookie='',body='',query=''):
 fields=[dest,method,path,cookie,body,query];wire=' '.join(v.encode('utf-8').hex() or '-' for v in fields)+'\n'
 with lock:
  worker.stdin.write(wire.encode());worker.stdin.flush();response=worker.stdout.readline().decode('ascii').split()
 if len(response)!=3:raise RuntimeError('Native worker stopped')
 code,b,h=response;return int(code),bytes.fromhex(b) if b!='-' else b'',bytes.fromhex(h).decode() if h!='-' else ''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):self.respond('GET')
 def do_POST(self):self.respond('POST')
 def respond(self,method):
  u=urlsplit(self.path);n=int(self.headers.get('Content-Length','0'))
  if n<0 or n>1024:self.send_error(413);return
  body=self.rfile.read(n).decode('utf-8') if n else ''
  special={'/__stand/reboot':'REBOOT','/__stand/offline':'OFFLINE','/__stand/online':'ONLINE','/__stand/stats':'STATS'}
  code,data,headers=call(self.server.dest,special.get(u.path,method),u.path,self.headers.get('Cookie',''),body,u.query)
  html=data.startswith(b'<!doctype html>')
  if html and self.server.dest=='admin':
   toolbar='''<section style="border:1px solid #6aa;padding:12px"><strong>ДЕМО на PC · ESP и ПЛК не используются</strong><p>Пароль стенда: demo12345. Все изменения относятся к модели.</p><button type="button" id="stand-reboot">Виртуальный перезапуск</button><button type="button" id="stand-off">Потеря сети</button><button type="button" id="stand-on">Восстановить сеть</button></section><script>for(const [id,url]of [['stand-reboot','reboot'],['stand-off','offline'],['stand-on','online']])document.getElementById(id).onclick=async()=>{await fetch('/__stand/'+url,{method:'POST'});if(url==='reboot')location.href='/'};</script>'''
   data=data.replace(b'<h1>',toolbar.encode()+b'<h1>',1)
  if html and self.server.dest=='project':data=data.replace(b'<script>',b'<script>window.__FLP_NATIVE_PREVIEW=true;</script><script>',1)
  if self.server.dest=='admin' and u.path=='/config' and data.startswith(b'{'):
   d=json.loads(data);d['projectPort']=project.server_port;data=json.dumps(d,ensure_ascii=False).encode()
  self.send_response(code)
  for header in headers.splitlines():
   key,value=header.split(': ',1)
   if key.lower() not in ('content-length','content-type','cache-control','connection'):self.send_header(key,value)
  self.send_header('Content-Type','text/html; charset=utf-8' if html else 'application/json; charset=utf-8' if data.startswith(b'{') else 'text/plain; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
admin=ThreadingHTTPServer(('127.0.0.1',0),Handler);admin.dest='admin';admin.daemon_threads=True
project=ThreadingHTTPServer(('127.0.0.1',0),Handler);project.dest='project';project.daemon_threads=True
threading.Thread(target=project.serve_forever,daemon=True).start()
status=dict(settings='http://127.0.0.1:'+str(admin.server_port)+'/',project='http://127.0.0.1:'+str(project.server_port)+'/',hardware=False,native_handlers=True,pc_bridge=False)
args.status_file.write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status),flush=True)
try:admin.serve_forever()
finally:project.shutdown();admin.server_close();project.server_close();worker.terminate();worker.wait(timeout=3)
