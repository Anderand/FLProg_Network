"""Regenerate deterministic gzip branches from the adapter's plain assets."""
import gzip
import hashlib
import json
import re
from pathlib import Path
from check_http_assets import embedded_assets

ROOT=Path(__file__).resolve().parents[3]
ADAPTER=ROOT/'Библиотека/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h'

def generate():
    text=ADAPTER.read_text(encoding='utf-8')
    text=re.sub(r'#if FLPROG_WEBUI_GZIP_ASSETS\n.*?\n#else\n', '', text, flags=re.S)
    text=text.replace('\n#endif // FLPROG_WEBUI_GZIP_ASSETS','')
    assets,_=embedded_assets(ADAPTER)
    pattern=r'(static void FLPROG_WEBUI_HTTP_FLASH (\w+)\(FLProgNetworkHttpServer \*value\)\s*\{.*?)(static const char asset\[\] PROGMEM =.*?value->sendProgmem\(200, "([^"]+)", asset\);)'
    callbacks=dict((callback,path) for path,callback in re.findall(r'server.addHandler\("([^"]+)",\s*(\w+),',text))
    callbacks.update(re.findall(r'// asset-route: (\w+) (\S+)',text))
    measurements={}
    def replace(m):
        path=callbacks[m[2]];raw=assets[path]['body'].encode('utf-8')
        compressed=gzip.compress(raw,compresslevel=9,mtime=0)
        assert gzip.decompress(compressed)==raw
        header=('HTTP/1.1 200 OK\r\nContent-Type: '+m[4]+'\r\nContent-Encoding: gzip\r\nVary: Accept-Encoding\r\nContent-Length: '+str(len(compressed))+'\r\nConnection: close\r\n\r\n').encode()
        assert len(header)+len(compressed)<=2048
        values=', '.join('0x%02x'%v for v in compressed)
        branch='#if FLPROG_WEBUI_GZIP_ASSETS\n        static const unsigned char assetGzip[] PROGMEM = {'+values+'};\n        static_assert(sizeof(assetGzip) + 192U <= FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES, "gzip response budget");\n        flprogWebUiSendGzip(value, "'+m[4]+'", assetGzip, sizeof(assetGzip));\n#else\n        '
        measurements[path]=dict(raw=len(raw),gzip=len(compressed),http_bytes=len(header)+len(compressed),sha256=hashlib.sha256(raw).hexdigest())
        return m[1]+branch+m[3]+'\n#endif // FLPROG_WEBUI_GZIP_ASSETS'
    text,count=re.subn(pattern,replace,text,flags=re.S)
    assert count==len(assets),(count,len(assets))
    if '#include "FLProgWebUiGzipHttp.h"' not in text:
        text=text.replace('#include <flprogNetwork.h>','#include <flprogNetwork.h>\n#include "FLProgWebUiGzipHttp.h"')
    ADAPTER.write_text(text,encoding='utf-8')
    return measurements

if __name__=='__main__':print(json.dumps(generate(),ensure_ascii=False,indent=2))
