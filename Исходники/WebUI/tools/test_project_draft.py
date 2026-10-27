import subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ProjectDraftTest(unittest.TestCase):
 def test_store_recovery_and_failures(self):
  subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(ROOT/'editor/public/draft.js')],check=True)
 def test_boot_restore_and_flush_are_packaged(self):
  html=(ROOT/'editor/public/index.html').read_text(encoding='utf-8');self.assertLess(html.index('src="draft.js?'),html.index('src="app.js?'))
  app=(ROOT/'editor/public/app.js').read_text(encoding='utf-8');self.assertLess(app.index('const restoredDraft='),app.index('function render()'))
  self.assertIn("window.addEventListener('pagehide',flushProjectDraft)",app)
  self.assertIn('function render(){normalize();scheduleProjectDraft();',app)
if __name__=='__main__':unittest.main()
