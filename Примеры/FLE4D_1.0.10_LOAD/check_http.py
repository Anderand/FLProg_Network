from pathlib import Path
import sys,socket,time,json,gzip,http.client,hashlib
W=Path(__file__).resolve().parent
sys.path.insert(0,r'E:\FLP\Flprog_network\flprog_webui_next\tools')
from check_http_assets import embedded_assets
deadline=time.monotonic()+40
while time.monotonic()<deadline:
    try:
        with socket.create_connection(('192.168.100.8',3233),timeout=2) as c:
            c.sendall(b'FLPINFO?');d=b''
            while len(d)<108:
                part=c.recv(108-len(d))
                if not part:break
                d+=part
        if d[76:108].split(b'\0')[0]==b'1.0.10-LOAD':break
    except OSError:pass
    time.sleep(.5)
else:raise SystemExit('New firmware not ready')
assets,_=embedded_assets(W/'libraries/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
result={}
import re
version=re.search(r'"(webui175-[0-9a-f]{12})"',(W/'libraries/FLProg_WebUI/src/adapters/FLProgWebUiAssetVersion.h').read_text())[1]
for path,asset in assets.items():
    c=http.client.HTTPConnection('192.168.100.8',80,timeout=5)
    url=path if path=='/' else path+('&' if '?' in path else '?')+'v='+version
    c.request('GET',url,headers={'Accept-Encoding':'gzip'});r=c.getresponse();h=dict(r.getheaders());b=r.read();c.close()
    assert r.status==200 and h.get('Content-Encoding')=='gzip',(path,r.status,h)
    assert int(h['Content-Length'])==len(b) and gzip.decompress(b)==asset['body'].encode('utf-8'),path
    assert h.get('Cache-Control')==('no-store' if path=='/' else 'public, max-age=31536000, immutable'),(path,h)
    time.sleep(.08)
    result[path]=dict(cache=h.get('Cache-Control'),bytes=len(b),sha256=hashlib.sha256(gzip.decompress(b)).hexdigest())
(W/'HTTP_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS 1.0.10-LOAD:',len(result),'resources match exact source bytes')
