import json,subprocess,tempfile,unittest
from pathlib import Path
from check_http_assets import ROOT,embedded_assets
class NoticesTest(unittest.TestCase):
    def test_lifecycle(self):
        assets,_=embedded_assets(ROOT/'Библиотека/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'assets.json';p.write_text(json.dumps(assets),encoding='utf-8')
            subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(p)],check=True)
if __name__=='__main__':unittest.main()
