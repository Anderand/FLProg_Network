"""Sync readable bootstrap; run build_gzip_assets.py afterwards."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
def sync():
 h=ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h'
 text=h.read_text(encoding='utf-8')
 text=re.sub(r'#if FLPROG_WEBUI_GZIP_ASSETS\n.*?\n#else\n','',text,flags=re.S).replace('\n#endif // FLPROG_WEBUI_GZIP_ASSETS','')
 for callback,name in [('index','index.html'),('loaderScript','loader.js')]:
  body=(ROOT/'runtime/FLProg_WebUI/web_assets'/name).read_text(encoding='utf-8').strip()
  pattern=r'(static void FLPROG_WEBUI_HTTP_FLASH '+callback+r'\(FLProgNetworkHttpServer \*value\).*?static const char asset\[\] PROGMEM =\s*)((?:"(?:\\.|[^"\\])*"\s*)+);'
  text,count=re.subn(pattern,lambda m:m[1]+json.dumps(body,ensure_ascii=False)+';',text,count=1,flags=re.S)
  assert count==1,callback
 h.write_text(text,encoding='utf-8')
if __name__=='__main__':sync()
