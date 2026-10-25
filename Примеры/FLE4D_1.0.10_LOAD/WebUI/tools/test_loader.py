import json,subprocess,tempfile,unittest
from pathlib import Path
from check_http_assets import ROOT,embedded_assets
class LoaderTest(unittest.TestCase):
 def test_bootstrap(self):
  assets,_=embedded_assets(ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'assets.json';p.write_text(json.dumps(assets),encoding='utf-8')
   subprocess.run(['node',str(Path(__file__).with_suffix('.js')),str(p)],check=True)
 def test_cache_version_follows_content(self):
  import build_gzip_assets as generator
  original=generator.ADAPTER
  try:
   with tempfile.TemporaryDirectory() as directory:
    adapter=Path(directory)/'adapter.h';adapter.write_bytes(original.read_bytes());generator.ADAPTER=adapter
    generator.generate();version=(adapter.parent/'FLProgWebUiAssetVersion.h').read_text()
    generator.generate();self.assertEqual(version,(adapter.parent/'FLProgWebUiAssetVersion.h').read_text())
    text=adapter.read_text(encoding='utf-8');self.assertIn('Загрузка интерфейса:',text)
    adapter.write_text(text.replace('Загрузка интерфейса:','Открытие интерфейса:',1),encoding='utf-8')
    generator.generate();self.assertNotEqual(version,(adapter.parent/'FLProgWebUiAssetVersion.h').read_text())
  finally:generator.ADAPTER=original
if __name__=='__main__':unittest.main()
