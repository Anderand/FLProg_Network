from pathlib import Path
import socket,http.client,time,gzip,hashlib,json,struct
W=Path(__file__).resolve().parent;HOST='192.168.100.8'
result={}
def get(path='/',slow=False):
    c=http.client.HTTPConnection(HOST,80,timeout=12)
    if slow:
        c.sock=socket.socket();c.sock.settimeout(12)
        c.sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,4096)
        c.sock.connect((HOST,80))
    else:c.connect()
    c.request('GET',path,headers={'Accept-Encoding':'gzip'});r=c.getresponse();headers=dict(r.getheaders());parts=[];start=time.monotonic()
    while True:
        try:part=r.read(257 if slow else 8192)
        except OSError:
            print('Read failed after',sum(map(len,parts)),'bytes in',time.monotonic()-start,'seconds',flush=True)
            c.close();raise
        if not part:break
        parts.append(part)
        if slow:time.sleep(.012)
    body=b''.join(parts);status=r.status;c.close()
    assert status==200,(path,status)
    assert int(headers['Content-Length'])==len(body),(path,len(body),headers)
    return headers,body,time.monotonic()-start
def ready():
    deadline=time.monotonic()+15
    while True:
        try:
            h,b,_=get();assert h.get('Content-Encoding')=='gzip';return
        except (OSError,http.client.HTTPException):
            if time.monotonic()>deadline:raise
            time.sleep(.3)
def identify():
    start=time.monotonic()
    with socket.create_connection((HOST,3233),timeout=2) as c:
        c.sendall(b'FLPINFO?');data=c.recv(24);assert data.startswith(b'FLPOTA2\0'),data
    return time.monotonic()-start
ready()
for kind in ('identity','gzip'):
    h,b,elapsed=get('/?stream-test='+kind)
    expected=(W/('test_payload.gz' if kind=='gzip' else 'test_payload.bin')).read_bytes()
    assert b==expected,kind
    if kind=='gzip':assert gzip.decompress(b)==(W/'test_payload.bin').read_bytes()
    result[kind]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),seconds=elapsed)
h,b,elapsed=get('/?stream-test=identity',slow=True)
assert b==(W/'test_payload.bin').read_bytes();result['slow_reader_seconds']=elapsed
for i in range(4):
    c=socket.create_connection((HOST,80),timeout=5);c.sendall(b'GET /?stream-test=identity HTTP/1.1\r\nHost: test\r\n\r\n');c.recv(512)
    c.setsockopt(socket.SOL_SOCKET,socket.SO_LINGER,struct.pack('hh',1,0));c.close();ready()
result['aborts_recovered']=4
# Keep the receive window blocked; OTA identity must still be serviced by loop().
c=socket.socket();c.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,1024);c.settimeout(5);c.connect((HOST,80));c.sendall(b'GET /?stream-test=identity HTTP/1.1\r\nHost: test\r\n\r\n')
c.recv(256);latencies=[]
for i in range(8):
    latencies.append(identify());time.sleep(1)
# Do not close the blocked peer yet: the server must reclaim its own slot.
ready();c.close();result['stall_timeout_recovered']=True;result['ota_identity_during_stall_seconds']=latencies
h,b,_=get('/flprog-webui/state?page=main');result['state_after']=json.loads(b)
(W/'DEVICE_TEST.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print('PASS',json.dumps(result,ensure_ascii=False))
