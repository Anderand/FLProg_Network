import json,re,hashlib,sys,gzip
from pathlib import Path
root=Path(__file__).resolve().parent
result={}
for variant in ('plain','gzip'):
    folder=root/variant
    log=(folder/'build.log').read_text(encoding='utf-8')
    flash=int(re.search(r'Sketch uses (\d+) bytes',log)[1])
    ram=int(re.search(r'Global variables use (\d+) bytes',log)[1])
    image=folder/'build/FLE4D_WEBUI_1_0_7.ino.bin'
    blob=image.read_bytes()
    result[variant]=dict(flash=flash,static_ram=ram,bin_bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
for metric in ('flash','static_ram','bin_bytes'):
    result[metric+'_delta']=result['gzip'][metric]-result['plain'][metric]
sys.path.insert(0,r'E:\FLP\Flprog_network\flprog_webui_next\tools')
from check_http_assets import embedded_assets
assets,_=embedded_assets(Path(r'E:\FLP\Flprog_network\flprog_webui_next\runtime\FLProg_WebUI\src\adapters\FLProgWebUiFlprogNetworkPagedHttp.h'))
result['assets_raw_bytes']=sum(len(v['body'].encode('utf-8')) for v in assets.values())
result['assets_gzip_bytes']=sum(len(gzip.compress(v['body'].encode('utf-8'),compresslevel=9,mtime=0)) for v in assets.values())
(root/'comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
