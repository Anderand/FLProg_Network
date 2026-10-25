from pathlib import Path
import json,re,http.client,gzip,time
W=Path(r'E:\SAI\FLProg_Network\_work\load_fle4d');assets=json.loads((W/'HTTP_VERIFICATION.json').read_text(encoding='utf-8'));version=re.search(r'"(webui175-[0-9a-f]{12})"',(W/'libraries/FLProg_WebUI/src/adapters/FLProgWebUiAssetVersion.h').read_text())[1]
rows=[]
for lap in range(20):
 t=time.monotonic();errors=[]
 for path in assets:
  url=path if path=='/' else path+('&' if '?'in path else '?')+'v='+version
  try:
   c=http.client.HTTPConnection('192.168.100.8',80,timeout=5);c.request('GET',url,headers={'Accept-Encoding':'gzip'});r=c.getresponse();b=r.read();c.close();assert r.status==200,(url,r.status);assert gzip.decompress(b)
  except Exception as e:errors.append(str(e))
  time.sleep(.08)
 row={'lap':lap+1,'s':round(time.monotonic()-t,3),'errors':errors};rows.append(row)
 if lap%5==4:print(json.dumps(row),flush=True)
(W/'REPEATED_READS.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');assert not any(x['errors']for x in rows)
print('PASS: 400 resource reads, 20 laps')
