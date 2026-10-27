import json,subprocess,tempfile,unittest
from pathlib import Path
from check_http_assets import ROOT,embedded_assets
class DeviceIdentityTest(unittest.TestCase):
 def test_placeholder_and_readonly(self):
  assets,_=embedded_assets(ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
  with tempfile.TemporaryDirectory()as folder:
   p=Path(folder)/'data.json';p.write_text(json.dumps(dict(assets=assets)),encoding='utf-8');subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(p),str(ROOT/'editor/public/preview-simulator.js')],check=True)
 def test_catalog_contract(self):
  d=json.loads((ROOT/'integration/flprog_network_api_catalog.json').read_text(encoding='utf-8'));items={x['id']:x for x in d['systemParameters']}
  for id in ['device_model','firmware_version']:
   self.assertEqual(items[id]['type'],'text');self.assertEqual(items[id]['direction'],'publish');self.assertIn('identity provider',items[id]['source'])
if __name__=='__main__':unittest.main()
