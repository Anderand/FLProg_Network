# coding: utf-8
"""Exercise the packaged EXE through its real loopback HTTP server, no COM."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

exe=Path(sys.argv[1]);report=Path(sys.argv[2])
with tempfile.TemporaryDirectory(prefix='bridge_exe_') as temp:
    status=Path(temp)/'status.json'
    p=subprocess.Popen([str(exe),'--headless','--demo','--allow-writes','--no-browser','--status-file',str(status)],
                       creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    try:
        for _ in range(100):
            if status.is_file():break
            if p.poll() is not None:raise RuntimeError('EXE exited '+str(p.returncode))
            time.sleep(.1)
        url=json.loads(status.read_text())['url'].rstrip('/')
        def get(path):
            with urllib.request.urlopen(url+path,timeout=3) as response:return response.read()
        info=json.loads(get('/api/v1/status'));assert info['demo'] and info['online']
        assert b'/api/v1/channels/' in get('/')
        assert json.loads(get('/api/v1/channels/101'))['value']==25
        data=dict(type='float',value=30.5,session=info['session'])
        request=urllib.request.Request(url+'/api/v1/channels/101',data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-FLProg-Bridge':'1'})
        with urllib.request.urlopen(request,timeout=3) as response:ack=json.load(response)
        assert ack['accepted'] and not ack['confirmed']
        assert json.loads(get('/api/v1/channels/101'))['value']==30.5
        before=json.loads(get('/api/v1/status'))['exchanges'];time.sleep(1.2)
        after=json.loads(get('/api/v1/status'));assert after['online'] and after['exchanges']>before
        report.write_text(json.dumps(dict(ok=True,exe=str(exe),demo=True,read=25,write=30.5,confirmed=ack['confirmed'],heartbeat=True),ensure_ascii=False,indent=2),encoding='utf-8')
        print('Packaged EXE: HTTP/read/write/heartbeat PASS')
    finally:
        p.terminate();p.wait(timeout=5)
