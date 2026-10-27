import json,subprocess,tempfile,unittest
from pathlib import Path
from build_project_package import build
from project_validation import validate_project
ROOT=Path(__file__).resolve().parents[1]
class DiagnosticsTemplateTest(unittest.TestCase):
 def test_plan_and_export(self):
  with tempfile.TemporaryDirectory()as folder:
   p=Path(folder)/'project.json';subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(ROOT/'editor/public/diagnostics.js'),str(ROOT/'integration/flprog_network_api_catalog.json'),str(p)],check=True)
   d=json.loads(p.read_text(encoding='utf-8'));self.assertTrue(validate_project(d)['valid']);out=build(p,Path(folder)/'out');source=next((out/'src').glob('*descriptor.h')).read_text(encoding='utf-8')
   for c in ['network_ip','network_ready','network_mac','network_gateway','network_subnet']:self.assertIn(c,source)
   self.assertNotIn('tcp_rx_bytes',source)
 def test_helper_is_packaged_in_editor(self):
  html=(ROOT/'editor/public/index.html').read_text(encoding='utf-8');self.assertIn('src="diagnostics.js?',html);self.assertLess(html.index('src="diagnostics.js?'),html.index('src="app.js?'))
if __name__=='__main__':unittest.main()
