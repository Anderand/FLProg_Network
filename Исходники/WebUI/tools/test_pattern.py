import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from field_pattern import parse_pattern,pattern_matches
from pattern_vectors import vectors,INVALID,GOLDEN
from project_validation import validate_project
from check_http_assets import ROOT,embedded_assets
from build_project_package import build
class PatternTest(unittest.TestCase):
 def test_python_contract(self):
  for p,v,e in GOLDEN:self.assertEqual(pattern_matches(p,v),e,(p,v))
  for p in INVALID:
   with self.assertRaises(ValueError):parse_pattern(p)
  for x in vectors():
   try:actual=pattern_matches(x['pattern'],x['value'])
   except ValueError:actual=False
   self.assertEqual(actual,x['expected'],x)
 def test_project_diagnostics(self):
  d=json.loads((ROOT/'projects/preview_busy_demo.flpui').read_text(encoding='utf-8'));w=d['pages'][0]['widgets'][0];w['pattern']='(bad)';before=copy.deepcopy(d);r=validate_project(d);issue=next(i for i in r['issues']if i['code']=='field-pattern');self.assertEqual(issue['widgetIndex'],0);self.assertEqual(issue['tab'],'behavior');self.assertEqual(d,before)
 def test_generated_fields(self):
  d=json.loads((ROOT/'projects/pattern_controls.flpui').read_text(encoding='utf-8'));w=next(w for w in d['pages'][0]['widgets'] if w.get('pattern'))
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp)/'p.flpui';p.write_text(json.dumps(d),encoding='utf-8');out=build(p,Path(temp)/'out');source=next((out/'src').glob('*descriptor.h')).read_text(encoding='utf-8');self.assertIn(w['pattern'],source);self.assertIn(w['validationMessage'],source)
 def test_message_limits(self):
  d=json.loads((ROOT/'projects/pattern_controls.flpui').read_text(encoding='utf-8'));w=next(w for w in d['pages'][0]['widgets'] if w.get('pattern'))
  for message in ['x'*97,'line\nbreak',[]]:
   w['validationMessage']=message;self.assertFalse(validate_project(d)['valid'])
 def test_browser_parity_and_field_error(self):
  assets,_=embedded_assets(ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp)/'data.json';p.write_text(json.dumps(dict(assets=assets,vectors=vectors())),encoding='utf-8');subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(p)],check=True)
if __name__=='__main__':unittest.main()
