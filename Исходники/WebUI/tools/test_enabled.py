import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from check_http_assets import ROOT,embedded_assets
from project_validation import validate_project
from build_project_package import build
class EnabledTest(unittest.TestCase):
 def doc(self):
  return dict(schema='flprog.webui/1.0',project=dict(id='enabled_test'),channels=[dict(id='sp',type='float',direction='duplex',index=101),dict(id='permit',type='bool',direction='publish',index=102)],pages=[dict(id='main',title='Main',widgets=[dict(id='field',type='number-input',channel='sp',bindings=[dict(role='enabled',channel='permit',direction='publish')])])])
 def test_validation_and_generation(self):
  d=self.doc();before=copy.deepcopy(d);self.assertTrue(validate_project(d)['valid'])
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp)/'p.flpui';p.write_text(json.dumps(d));out=build(p,Path(temp)/'out');self.assertIn('"enabled", "permit", "publish"',next((out/'src').glob('*descriptor.h')).read_text())
  self.assertEqual(d,before)
 def test_bad_bindings(self):
  for change in ['type','direction','missing','duplicate','display']:
   d=self.doc();w=d['pages'][0]['widgets'][0]
   if change=='type':d['channels'][1]['type']='int32'
   if change=='direction':d['channels'][1]['direction']='command'
   if change=='missing':w['bindings'][0]['channel']='gone'
   if change=='duplicate':w['bindings']*=2
   if change=='display':w['type']='text'
   self.assertFalse(validate_project(d)['valid'],change)
 def test_browser_guards(self):
  assets,_=embedded_assets(ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp)/'assets.json';p.write_text(json.dumps(assets),encoding='utf-8');subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(p)],check=True)
if __name__=='__main__':unittest.main()
