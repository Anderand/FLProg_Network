import sys,json,gzip,http.client,hashlib,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'tools'))
from check_http_assets import embedded_assets
root=Path(__file__).resolve().parent
assets,_=embedded_assets(Path(__file__).resolve().parents[2]/'Библиотека/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
variant=sys.argv[1]
def get(path,encoding='gzip',head=False,extra=False):
    c=http.client.HTTPConnection('192.168.100.8',80,timeout=10)
    c.putrequest('HEAD' if head else 'GET',path,skip_accept_encoding=True)
    if extra:
        for i in range(12):c.putheader('X-Test-'+str(i),'optional')
    if encoding is not None:c.putheader('Accept-Encoding',encoding)
    c.endheaders();r=c.getresponse();status=r.status;headers=dict(r.getheaders());body=r.read();c.close();return status,headers,body
result={}
for path,asset in assets.items():
    status,headers,body=get(path)
    assert status==200,(path,status,body)
    if variant=='gzip':
        assert headers.get('Content-Encoding')=='gzip',(path,headers)
        raw=gzip.decompress(body)
        assert headers.get('Vary')=='Accept-Encoding'
    else:raw=body
    assert raw==asset['body'].encode('utf-8'),path
    assert int(headers['Content-Length'])==len(body)
    result[path]=dict(bytes=len(body),sha256=hashlib.sha256(raw).hexdigest())
    time.sleep(.08)
if variant=='gzip':
    for enc in ('identity','gzip;q=0','gzip;q=0, *;q=1'):
        status,h,b=get('/',enc,extra=True);assert status==406,(enc,status)
        assert len(b)==int(h['Content-Length'])==24
    # This adapter registers GET routes only; preserve its existing HEAD policy.
    status,h,b=get('/','gzip',head=True);assert status in (404,405) and b==b''
    status,h,b=get('/',None);assert status==200 and gzip.decompress(b)==assets['/']['body'].encode()
    status,h,b=get('/','gzip',extra=True);assert status==200 and h['Content-Encoding']=='gzip'
    status,h,b=get('/','x'*130+', gzip;q=0',extra=True);assert status==406
status,h,b=get('/flprog-webui/state?page=main');assert status==200
result['state']=json.loads(b)
(root/(variant+'_device.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS',variant,'15 assets, exact bodies, lengths; total bytes',sum(v.get('bytes',0) for v in result.values()),flush=True)
