import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from check_http_assets import ROOT,embedded_assets
from build_project_package import polling_settings,build,validate
class PollingTest(unittest.TestCase):
 def test_default_and_explicit(self):
  self.assertEqual(polling_settings({}),{'intervalMs':1300,'pauseWhenHidden':True})
  self.assertEqual(polling_settings({'polling':{'intervalMs':60000,'pauseWhenHidden':False}}),{'intervalMs':60000,'pauseWhenHidden':False})
 def test_invalid_settings(self):
  for value in [None,[],{'intervalMs':True},{'intervalMs':499},{'intervalMs':60001},{'intervalMs':1000.5},{'intervalMs':'2000'},{'pauseWhenHidden':'false'}]:
   with self.assertRaises(ValueError):polling_settings({'polling':value})
 def test_generated_contract(self):
  d=json.loads((ROOT/'projects/preview_busy_demo.flpui').read_text(encoding='utf-8'));d['polling']={'intervalMs':2500,'pauseWhenHidden':False};before=copy.deepcopy(d)
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp)/'project.flpui';p.write_text(json.dumps(d),encoding='utf-8');out=build(p,Path(temp)/'out')
   self.assertIn('pollIntervalMs = 2500UL',next((out/'src').glob('*descriptor.h')).read_text())
   self.assertIn('pauseWhenHidden = false',next((out/'src').glob('*descriptor.h')).read_text())
   self.assertIn('webUi.setPolling',next((out/'src').glob('*_webui.h')).read_text())
  self.assertEqual(d,before)
  d['polling']['intervalMs']=0
  with self.assertRaisesRegex(ValueError,'Период'):validate(d)
 def test_runtime(self):
  assets,_=embedded_assets(ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp)/'assets.json';p.write_text(json.dumps(assets),encoding='utf-8');subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(p)],check=True)
if __name__=='__main__':unittest.main()
