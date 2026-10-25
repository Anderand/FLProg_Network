"""Refresh embedded notification JS from readable sources; regenerate gzip after this."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[3]
def sync():
    h=ROOT/'Библиотека/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h'
    text=h.read_text(encoding='utf-8')
    text=re.sub(r'#if FLPROG_WEBUI_GZIP_ASSETS\n.*?\n#else\n','',text,flags=re.S).replace('\n#endif // FLPROG_WEBUI_GZIP_ASSETS','')
    for name in ('notice-view','notice-track','notice-sync'):
        js=''.join(line.strip() for line in (ROOT/'Библиотека/FLProg_WebUI/web_assets'/f'{name}.js').read_text(encoding='utf-8').splitlines())
        assert len(js.encode('utf-8'))+128<=2048,(name,len(js.encode('utf-8')))
        callback=name.replace('-','_')+'Script'
        pattern=r'(static void FLPROG_WEBUI_HTTP_FLASH '+callback+r'\(FLProgNetworkHttpServer \*value\).*?static const char asset\[\] PROGMEM =\s*)((?:"(?:\\.|[^"\\])*"\s*)+);'
        text,count=re.subn(pattern,lambda m:m[1]+json.dumps(js,ensure_ascii=False)+';',text,count=1,flags=re.S)
        assert count==1,name
    pattern=r'(static void FLPROG_WEBUI_HTTP_FLASH formApplyScript\(FLProgNetworkHttpServer \*value\).*?static const char asset\[\] PROGMEM =\s*)((?:"(?:\\.|[^"\\])*"\s*)+);'
    match=re.search(pattern,text,re.S)
    import ast
    body=''.join(ast.literal_eval(s) for s in re.findall(r'"(?:\\.|[^"\\])*"',match[2]))
    if 'Ошибка ввода:' not in body:
        body=body.replace("i.reportValidity();", "if(typeof noticeInfo==='function')noticeInfo('Ошибка ввода: '+w.label);i.reportValidity();")
        assert len(body.encode('utf-8'))+128<=2048
        text=re.sub(pattern,lambda m:m[1]+json.dumps(body,ensure_ascii=False)+';',text,count=1,flags=re.S)
    h.write_text(text,encoding='utf-8')
if __name__=='__main__':sync()
