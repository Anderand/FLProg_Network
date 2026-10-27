import ast
import gzip
import json
import re
import subprocess
import unittest
from pathlib import Path
from check_http_assets import ROOT,embedded_assets
from build_gzip_assets import bundle_source


class FlashBundleTest(unittest.TestCase):
    def test_generated_bundle_matches_all_sources_and_gzip(self):
        adapter=ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h'
        assets,_=embedded_assets(adapter)
        expected=bundle_source(assets)
        header=(adapter.parent/'FLProgWebUiBundle.h').read_text(encoding='utf-8')
        packed=bytes(int(n,16) for n in re.search(r'data\[\] PROGMEM = \{([^}]+)\}',header)[1].split(','))
        self.assertEqual(gzip.decompress(packed),expected.encode('utf-8'))
        self.assertEqual(packed,gzip.compress(expected.encode('utf-8'),compresslevel=9,mtime=0))
        self.assertGreater(len(packed),2048) # Exercise the Flash stream, not the bounded response path.
        self.assertEqual((ROOT/'runtime/FLProg_WebUI/web_assets/bundle.js').read_text(encoding='utf-8'),expected)
        self.assertIn('FLPROG_HTTP_SERVER_HAS_FLASH_STREAM',header)
        self.assertIn('static const unsigned char data[] PROGMEM',header)
        self.assertIn('flprogWebUiSendIdentity',header) # Non-gzip build streams the same script.
        self.assertEqual(ast.literal_eval(re.search(r'static const char data\[\] PROGMEM = (".*");',header)[1]),expected)

    def test_combined_script_executes_once_in_dependency_order(self):
        subprocess.run(['node',str(Path(__file__).with_suffix('.js')),
            str(ROOT/'runtime/FLProg_WebUI/web_assets/bundle.js')],check=True)
