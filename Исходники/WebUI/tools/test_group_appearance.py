import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from group_style import group_style,validate_group_styles,DEFAULT_GROUP_STYLE
from project_validation import validate_project
from check_http_assets import ROOT,embedded_assets
from build_project_package import build
class GroupAppearanceTest(unittest.TestCase):
 def test_defaults_and_isolation(self):
  page={};before=copy.deepcopy(page);self.assertEqual(group_style(page,'g'),DEFAULT_GROUP_STYLE);self.assertEqual(page,before)
  a={'groupStyles':{'g':{'border':False,'padding':0,'gap':32}}};b={'groupStyles':{'g':{'padding':4}}}
  self.assertEqual(group_style(a,'g'),dict(border=False,padding=0,gap=32));self.assertEqual(group_style(b,'g')['padding'],4)
 def test_invalid_styles(self):
  for style in [None,[],{'gap':True},{'gap':33},{'padding':-1},{'padding':'12'},{'border':0},{'css':'x'}]:
   with self.assertRaises(ValueError):validate_group_styles({'groupStyles':{'g':style}})
  for styles in [None,[],{'':{}},{' g':{}}]:
   with self.assertRaises(ValueError):validate_group_styles({'groupStyles':styles})
 def test_export_preserves_contract(self):
  d=json.loads((ROOT/'projects/grouped_controls.flpui').read_text(encoding='utf-8'));w=d['pages'][0]['widgets'][0];w['group']='Shared';d['pages'][0]['groupStyles']={'Shared':{'border':False,'padding':20,'gap':0}};before=copy.deepcopy(d)
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp)/'p.flpui';p.write_text(json.dumps(d),encoding='utf-8');out=build(p,Path(temp)/'out');source=next((out/'src').glob('*descriptor.h')).read_text(encoding='utf-8');self.assertIn(json.dumps('{"border":false,"padding":20,"gap":0}'),source)
  self.assertEqual(d,before)
  d['pages'][0]['groupStyles']['Shared']['gap']=99;self.assertTrue(any(i['code']=='group-style'for i in validate_project(d)['issues']))
 def test_runtime(self):
  assets,_=embedded_assets(ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp)/'assets.json';p.write_text(json.dumps(assets),encoding='utf-8');subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(p)],check=True)
if __name__=='__main__':unittest.main()

