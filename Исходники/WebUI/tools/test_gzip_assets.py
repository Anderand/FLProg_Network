import gzip
import re
import unittest
from check_http_assets import ROOT,embedded_assets

class GzipAssetsTest(unittest.TestCase):
    def test_all_generated_assets(self):
        adapter=ROOT/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h'
        text=adapter.read_text(encoding='utf-8');assets,_=embedded_assets(adapter)
        routes=dict((callback,path) for path,callback in re.findall(r'server.addHandler\("([^"]+)",\s*(\w+),',text))
        routes.update(re.findall(r'// asset-route: (\w+) (\S+)',text))
        pairs=re.findall(r'static void FLPROG_WEBUI_HTTP_FLASH (\w+)\(FLProgNetworkHttpServer \*value\).*?static const unsigned char assetGzip\[\] PROGMEM = \{([^}]+)\};.*?flprogWebUiSendGzip\(value, "([^"]+)"',text,re.S)
        self.assertEqual(len(pairs),len(assets))
        for callback,array,mime in pairs:
            data=bytes(int(x.strip(),16) for x in array.split(','));asset=assets[routes[callback]]
            raw=asset['body'].encode('utf-8')
            self.assertEqual(gzip.decompress(data),raw)
            self.assertEqual(data,gzip.compress(raw,compresslevel=9,mtime=0))
            self.assertEqual(mime,asset['type'])
            self.assertLessEqual(len(data)+192,2048)

if __name__=='__main__':unittest.main()
