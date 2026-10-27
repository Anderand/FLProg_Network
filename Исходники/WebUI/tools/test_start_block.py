import copy,json,tempfile,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from build_start_block import start_block_bytes,START_NAME
from build_project_package import build,project_entry_header
ROOT=Path(__file__).resolve().parents[1]
class StartBlockTest(unittest.TestCase):
 def test_text_format_runs_cover_all_characters(self):
  r=ET.fromstring(start_block_bytes())
  for text in r.iter():
   if text.get('sixx.type')!='Text':continue
   fields={n.get('sixx.name'):n for n in text};value=fields['string'].text or ''
   runs={n.get('sixx.name'):n for n in fields['runs']}
   self.assertEqual(sum(int(n.text)for n in runs['runs']),len(value))
   self.assertEqual(len(runs['runs']),len(runs['values']))
   if value:self.assertGreater(len(runs['values']),0)
 def test_professional_schema_and_parameter_reference(self):
  b=start_block_bytes();r=ET.fromstring(b)
  self.assertEqual(r.get('sixx.type'),'UserCodeMultiBlockBlockLibraryElement')
  nodes=list(r.iter());ids={n.get('sixx.id')for n in nodes if n.get('sixx.id')is not None}
  for n in nodes:
   if n.get('sixx.idref')is not None:self.assertIn(n.get('sixx.idref'),ids)
  params=[n for n in nodes if n.get('sixx.type')=='UserCodeMultiBlockStandartParametr'];self.assertEqual(len(params),1)
  self.assertTrue(any(n.get('sixx.name')=='isInsertWithoutBrackets'and n.get('sixx.type')=='True'for n in params[0]))
  self.assertTrue(any(n.get('sixx.name')=='isUseItOnce'and n.get('sixx.type')=='True'for n in nodes))
  self.assertFalse(any(n.get('sixx.type')in ['VirtualFile','VirtualDirectory']for n in nodes))
  self.assertEqual(b,start_block_bytes())
  seen=set()
  for n in nodes:
   if n.get('sixx.idref')is not None:self.assertIn(n.get('sixx.idref'),seen)
   if n.get('sixx.id')is not None:seen.add(n.get('sixx.id'))
 def test_same_block_for_distinct_projects_and_headers(self):
  d=json.loads((ROOT/'projects/preview_busy_demo.flpui').read_text(encoding='utf-8'));before=copy.deepcopy(d)
  with tempfile.TemporaryDirectory()as folder:
   results=[]
   for id in ['web_slave','web-slave']:
    project=copy.deepcopy(d);project['project']['id']=id;src=Path(folder)/(id+'.flpui');src.write_text(json.dumps(project),encoding='utf-8');out=build(src,Path(folder)/'out');results.append(out)
    self.assertEqual((out/START_NAME).read_bytes(),start_block_bytes())
    self.assertEqual(len(list(out.glob('*.ubi'))),1)
    wrapper=(out/'src'/f'{id}_webui.h').read_text(encoding='utf-8')
    self.assertIn('namespace flprog_webui_selected = flprog_webui_web_slave;',wrapper)
    self.assertIn('#include "web_slave_descriptor.h"',wrapper)
   self.assertNotEqual(results[0],results[1]);self.assertTrue(all(x.exists()for x in results))
  self.assertEqual(d,before)
 def test_transport_guards(self):
  for transport,macro in [('wifi-http','FLPROG_WIFI_INTERFACE1'),('w5500-http-1','FLPROG_WIZNET_INTERFACE1'),('w5500-http-2','FLPROG_WIZNET_INTERFACE2')]:
   h=project_entry_header('web_slave',transport);self.assertIn('flprog_webui_selected::begin('+macro+')',h);self.assertIn('return webUi.begin(network)',h);self.assertIn('#error',h)
if __name__=='__main__':unittest.main()
