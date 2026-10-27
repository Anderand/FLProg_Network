import importlib.util, json, tempfile, threading, unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]

class ProjectStorageServerTest(unittest.TestCase):
    def test_save_and_build_external_without_installing_into_ide(self):
        spec=importlib.util.spec_from_file_location('storage_test_server',ROOT/'editor/server.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);ide=root/'fake_ide';ide.mkdir()
            sentinel=ide/'unchanged.txt';sentinel.write_text('unchanged')
            server.FLPROG_LIBRARIES=ide
            http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
            try:
                document=json.loads((ROOT/'projects/preview_busy_demo.flpui').read_text(encoding='utf-8'))
                document['projectFolder']=str(root/'User projects'/'a123')
                document['project']['id']='a123'
                document['transport']['id']='w5500-http-1'
                def post(path,payload):
                    request=Request('http://127.0.0.1:%d%s'%(http.server_port,path),json.dumps(payload).encode(),{'Content-Type':'application/json'})
                    with urlopen(request) as response:return json.load(response)
                contract=post('/api/contract',document)
                self.assertEqual(contract['report']['project_id'],'a123')
                self.assertIn('Каналы для FLProg',contract['markdown'])
                self.assertFalse((root/'User projects/a123').exists())
                compatibility=post('/api/compatibility',document)
                self.assertTrue(compatibility['ok'])
                self.assertFalse((root/'User projects/a123').exists())
                self.assertEqual(list(ide.iterdir()),[sentinel])
                invalid=dict(document,installToIde=True)
                self.assertFalse(post('/api/compatibility',invalid)['ok'])
                from urllib.error import HTTPError
                with self.assertRaises(HTTPError) as failure:
                    post('/api/build',{'document':invalid,'allowWarnings':True})
                self.assertEqual(failure.exception.code,422)
                self.assertFalse((root/'User projects/a123').exists())
                saved=post('/api/save',document)
                self.assertEqual(Path(saved['file']),root/'User projects/a123/a123.flpui')
                built=post('/api/build',{'document':document,'allowWarnings':True})
                self.assertIsNone(built['installed'])
                self.assertEqual(Path(built['package']),root/'User projects/a123/libraries/FLProg_WebUI_Project_a123')
                self.assertTrue((Path(built['package'])/'src/a123_webui.h').is_file())
                self.assertTrue((Path(built['libraries'])/'FLProg_WebUI/src/FLProgWebUi.h').is_file())
                self.assertEqual(json.loads((Path(built['package'])/'CHANNELS.json').read_text(encoding='utf-8')),contract['report'])
                self.assertEqual(list(ide.iterdir()),[sentinel])
            finally:
                http.shutdown();http.server_close();thread.join()
