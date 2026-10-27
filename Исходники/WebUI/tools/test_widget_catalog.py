import ast,gzip,json,re,tempfile,unittest
from pathlib import Path
from build_project_package import build,validate,widget_catalog_payloads
from check_http_assets import ROOT

class WidgetCatalogTest(unittest.TestCase):
    def setUp(self):
        self.doc=json.loads((ROOT/'projects/preview_busy_demo.flpui').read_text(encoding='utf-8'))

    def test_catalog_preserves_global_order_pages_and_properties(self):
        _,channels=validate(self.doc)
        payloads=widget_catalog_payloads(channels,self.doc['pages'])
        expected=0
        for page,payload in zip(self.doc['pages'],payloads):
            self.assertEqual(payload['page'],page['id'])
            for source,(index,item) in zip(page['widgets'],payload['items']):
                self.assertEqual(index,expected);expected+=1
                self.assertEqual(item['id'],source['id']);self.assertEqual(item['page'],page['id'])
                self.assertEqual(item['type'],source['type'])
                for binding in item['bindings']:
                    self.assertEqual(set(binding),{'role','channel','direction'})
        self.assertEqual(expected,sum(len(p['widgets']) for p in self.doc['pages']))

    def test_generated_flash_bytes_and_identity_are_same_catalog(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'demo.flpui';path.write_text(json.dumps(self.doc),encoding='utf-8')
            package=build(path,Path(d)/'libraries')
            header=next((package/'src').glob('*_descriptor.h')).read_text(encoding='utf-8')
            arrays=re.findall(r'static const unsigned char data\[\] PROGMEM = \{([^}]+)\}',header)
            texts=re.findall(r'static const char data\[\] PROGMEM = (".*");',header)
            self.assertEqual(len(arrays),len(self.doc['pages']));self.assertEqual(len(texts),len(arrays))
            for array,text in zip(arrays,texts):
                packed=bytes(int(v,16) for v in array.split(','))
                raw=ast.literal_eval(text).encode('utf-8')
                self.assertEqual(gzip.decompress(packed),raw)
                self.assertEqual(packed,gzip.compress(raw,compresslevel=9,mtime=0))
            self.assertIn('#if defined(FLPROG_HTTP_SERVER_HAS_FLASH_STREAM)',header)
            self.assertIn('FLPROG_WEBUI_WIDGET_CATALOG(server, page)',header)
