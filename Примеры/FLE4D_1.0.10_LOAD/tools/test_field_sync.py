import tempfile,json,subprocess
from pathlib import Path
from check_http_assets import ROOT,embedded_assets
assets,_=embedded_assets(ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'assets.json';p.write_text(json.dumps(assets),encoding='utf-8')
    subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(p)],check=True)
