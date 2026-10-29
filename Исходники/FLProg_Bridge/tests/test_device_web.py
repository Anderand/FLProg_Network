# coding: utf-8
import gzip,hashlib,json,re,struct,sys,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'flprog_bridge'),str(R/'flprog_webui_next/tools'),str(Path(__file__).parent)]
from export_bridge import export_bridge
from test_web_project import document
from device_web import device_site,synchronize,MAX_PLAIN
from client import BridgeError
from http_api import State,make_server

class Device:
    def __init__(self,doc,folder):
        result=export_bridge(doc,R/'flprog_webui_next',folder)
        header=Path(result['identityHeader']).read_text(encoding='utf-8')
        array=re.search(r'FLPROG_BRIDGE_WEB_PACKAGE\[\].*?\{(.*?)\};',header,re.S)[1]
        self.data=bytes(int(v,16) for v in re.findall(r'0x([0-9a-f]{2})',array))
        self.plain=len(gzip.decompress(self.data));self.sha=hashlib.sha256(self.data).digest()
        self.info=dict(services=[1,4],identity=dict(projectId=doc['project']['id'],webApi=1,webHash=result['projectHash']))
        self.online=True;self.session=123;self.calls=[];self.offset_error=False;self.session_error=False
    def request(self,service,op,payload,expected_session=None):
        self.calls.append((service,op,payload));assert service==4
        if self.session_error and op==2:raise BridgeError('Сеанс изменился',409)
        if op==1:return struct.pack('<BBHII',1,1,224,len(self.data),self.plain)+self.sha
        offset,count=struct.unpack('<IH',payload)
        return struct.pack('<I',offset+(1 if self.offset_error else 0))+self.data[offset:offset+count]
    def status(self):return dict(online=self.online,session=str(self.session),device=self.info)

class DeviceWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.device=Device(document(),self.root/'export');self.cache=self.root/'cache'
    def tearDown(self):self.temp.cleanup()
    def test_header_contains_full_verified_page_and_document(self):
        package=json.loads(gzip.decompress(self.device.data))
        self.assertIn('bridgeSessionChanged',package['files']['index.html'])
        self.assertEqual(json.loads(package['files']['project.json'])['project']['id'],'bridge-demo')
        self.assertLess(len(self.device.data),self.device.plain)
    def test_download_and_cache_hit_only_read_metadata(self):
        progress=[];folder,info=device_site(self.device,lambda a,b:progress.append((a,b)),self.cache)
        self.assertFalse(info['cacheHit']);self.assertTrue((folder/'index.html').is_file())
        self.assertEqual(progress[-1],(len(self.device.data),len(self.device.data)))
        for service,op,payload in self.device.calls:
            if op==2:self.assertLessEqual(struct.unpack('<IH',payload)[1],224)
        self.device.calls=[];again,info=device_site(self.device,cache=self.cache)
        self.assertTrue(info['cacheHit']);self.assertEqual(folder,again);self.assertEqual(len(self.device.calls),1)
    def test_digest_failure_never_accepts_resources(self):
        self.device.sha=bytes(32)
        with self.assertRaises(BridgeError):device_site(self.device,cache=self.cache)
        self.assertEqual(list(self.cache.glob('*/bridge.json')),[])
    def test_wrong_offset_is_rejected(self):
        self.device.offset_error=True
        with self.assertRaises(BridgeError):device_site(self.device,cache=self.cache)
    def test_size_limit_is_checked_before_download(self):
        self.device.plain=MAX_PLAIN+1
        with self.assertRaises(BridgeError):device_site(self.device,cache=self.cache)
        self.assertEqual(len(self.device.calls),1)
    def test_gzip_expansion_must_equal_declared_size(self):
        self.device.plain=10
        with self.assertRaises(BridgeError):device_site(self.device,cache=self.cache)
    def test_device_identity_must_match_package(self):
        self.device.info['identity']['webHash']='0'*64
        with self.assertRaises(BridgeError):device_site(self.device,cache=self.cache)
    def test_session_failure_does_not_accept_partial_files(self):
        self.device.session_error=True
        with self.assertRaises(BridgeError):device_site(self.device,cache=self.cache)
        self.assertEqual(list(self.cache.glob('*/bridge.json')),[])
    def test_tampered_cache_is_not_served(self):
        folder,_=device_site(self.device,cache=self.cache);(folder/'index.html').write_text('tampered')
        again,info=device_site(self.device,cache=self.cache)
        self.assertFalse(info['cacheHit']);self.assertNotEqual(folder,again)
        self.assertIn('bridgeSessionChanged',(again/'index.html').read_text(encoding='utf-8'))
    def test_state_replaces_old_project_only_after_validation(self):
        state=State();state.client=self.device;synchronize(state,self.device,cache=self.cache)
        self.assertEqual(state.webSource,'device');state.active();old=state.manifest['projectHash']
        changed=document();changed['pages'][0]['widgets'][0]['label']='New label'
        other=Device(changed,self.root/'other');state.client=other
        with self.assertRaises(BridgeError):state.active()
        synchronize(state,other,cache=self.cache);state.active()
        self.assertNotEqual(old,state.manifest['projectHash'])
    def test_old_firmware_clears_previous_device_site(self):
        state=State();state.client=self.device;synchronize(state,self.device,cache=self.cache)
        self.device.info['services']=[1]
        self.assertIsNone(synchronize(state,self.device,cache=self.cache))
        self.assertEqual(state.webSource,'generic');self.assertIsNone(state.site)
    def test_http_loading_page_and_content_hash_redirect(self):
        state=State();state.client=self.device;server=make_server(state)
        threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)
        try:
            state.resourceLoading=True;state.resourceProgress=dict(received=12,total=100)
            with urllib.request.urlopen(base+'/') as response:self.assertIn('Flash',response.read().decode('utf-8'))
            with self.assertRaises(urllib.error.HTTPError) as failure:urllib.request.urlopen(base+'/flprog-webui/state?page=main')
            self.assertEqual(failure.exception.code,503)
            state.resourceLoading=False;synchronize(state,self.device,cache=self.cache)
            with urllib.request.urlopen(base+'/') as response:
                self.assertEqual(response.geturl(),base+'/?web='+state.manifest['projectHash'])
                self.assertIn('bridgePageHash',response.read().decode('utf-8'))
            with urllib.request.urlopen(base+'/api/v1/status') as response:
                status=json.load(response);self.assertEqual(status['webSource'],'device');self.assertFalse(status['resourceLoading'])
        finally:server.shutdown();server.server_close()
if __name__=='__main__':unittest.main(verbosity=2)
