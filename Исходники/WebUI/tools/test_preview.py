import copy
import json
import subprocess
import unittest
import tempfile
import shutil
from pathlib import Path
from preview_project import preview_html

ROOT=Path(__file__).resolve().parents[1]

class PreviewTest(unittest.TestCase):
    def test_bundled_demo_contract(self):
        d=json.loads((ROOT/'projects/preview_busy_demo.flpui').read_text(encoding='utf-8'))
        self.assertIn('async function q()',preview_html(d,ROOT))
        channels={c['id']:c for c in d['channels']}
        button=next(w for p in d['pages'] for w in p['widgets'] if w['type']=='button')
        bindings={b['role']:b['channel'] for b in button['bindings']}
        self.assertEqual(channels[bindings['busy']]['type'],'bool')
        self.assertEqual(channels[bindings['result']]['direction'],'publish')
        self.assertTrue(button['confirmation'])
        self.assertTrue(any(w['type']=='number-input' for p in d['pages'] for w in p['widgets']))
    def test_embedded_runtime_and_no_mutation(self):
        d=json.loads((ROOT/'projects/grouped_controls.flpui').read_text(encoding='utf-8'))
        before=copy.deepcopy(d)
        html=preview_html(d,ROOT)
        self.assertEqual(d,before)
        self.assertIn("connect-src 'none'",html)
        self.assertIn('async function q()',html)
        self.assertIn('Синхронизировано',html)
        self.assertNotIn('<script src=',html)

    def test_invalid_rejected(self):
        with self.assertRaises(ValueError):preview_html({},ROOT)

    def test_portable_layout(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            shutil.copytree(ROOT/'runtime',root/'runtime')
            (root/'public').mkdir()
            shutil.copy2(ROOT/'editor/public/preview-simulator.js',root/'public')
            d=json.loads((ROOT/'projects/grouped_controls.flpui').read_text(encoding='utf-8'))
            self.assertIn('window.fetch=',preview_html(d,root))

    def test_json_script_escape(self):
        d=json.loads((ROOT/'projects/grouped_controls.flpui').read_text(encoding='utf-8'))
        d['project']['title']='</script><script>alert(1)</script>'
        html=preview_html(d,ROOT)
        self.assertNotIn('</script><script>alert(1)',html)

    def test_simulation(self):
        subprocess.run(['node',str(ROOT/'tools/test_preview.js'),str(ROOT/'editor/public/preview-simulator.js')],check=True)

if __name__=='__main__':unittest.main()
