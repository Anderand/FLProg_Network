from pathlib import Path
import http.client,time,json
W=Path(r'E:\SAI\FLProg_Network\_work\load_fle4d');checks=[]
for url in ['/flprog-webui/controls.js','/flprog-webui/controls.js?v=old-version']:
 for i in range(3):
  try:
   c=http.client.HTTPConnection('192.168.100.8',80,timeout=5);c.request('GET',url,headers={'Accept-Encoding':'gzip'});r=c.getresponse();r.read();h=r.getheader('Cache-Control');c.close();assert h=='no-store';checks.append({'url':url,'cache':h});break
  except OSError:
   if i==2:raise
   time.sleep(.3)
 time.sleep(.1)
(W/'CACHE_NEGATIVE_CHECKS.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print('PASS: versionless and mismatched resource URLs not cached')
