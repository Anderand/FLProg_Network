# coding: utf-8
import copy,json,subprocess,sys,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'flprog_bridge'),str(R/'flprog_webui_next/tools')]
from export_bridge import export_bridge
from http_api import State,make_server
from client import Client,BridgeError
from demo import DemoPort


def document():
    return dict(schema='flprog.webui/1.0',project=dict(id='bridge-demo',title='Bridge demo'),
      channels=[dict(id='setpoint',type='float',direction='duplex',index=101,source='user'),dict(id='switch',type='bool',direction='duplex',index=102,source='user')],
      pages=[dict(id='main',title='Главная',widgets=[dict(id='setpoint_field',type='number-input',channel='setpoint',label='Уставка',x=1,y=1,w=4,h=2,min=0,max=100,step=.5),dict(id='switch_widget',type='switch',channel='switch',label='Переключатель',x=5,y=1,w=4,h=2)])])


class WebProjectTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.site=Path(self.temp.name)/'site'
        self.doc=document();self.export=export_bridge(self.doc,R/'flprog_webui_next',self.site)
        self.state=State(self.site,True);self.state.client=Client(DemoPort());self.state.client.handshake()
        self.state.client.info['identity'].update(webApi=1,webHash=self.export['projectHash'])
        self.server=make_server(self.state);threading.Thread(target=self.server.serve_forever,daemon=True).start()
        self.base='http://127.0.0.1:'+str(self.server.server_port)
    def tearDown(self):self.server.shutdown();self.server.server_close();self.temp.cleanup()
    def call(self,path,post=False,session=None):
        h={'Content-Type':'application/json','X-FLProg-Bridge':'1'}
        if session is not None:h['X-FLProg-Session']=session
        req=urllib.request.Request(self.base+path,data=b'{}' if post else None,headers=h)
        try:
            with urllib.request.urlopen(req) as response:return response.status,response.read()
        except urllib.error.HTTPError as response:return response.code,response.read()
    def test_exact_renderer_export_and_paths_do_not_change_hash(self):
        html=(self.site/'index.html').read_text(encoding='utf-8')
        self.assertNotIn('preview-simulator',html);self.assertIn('bridgeSessionChanged(d)',html);self.assertIn('noticeStart',html)
        self.assertIn('.el.row{display:flex;',html)
        self.assertIn('gap:12px',html)
        self.assertIn('padding:7px 12px',html)
        self.assertIn('overflow-wrap:anywhere',html)
        changed=copy.deepcopy(self.doc);changed['projectFolder']='X:/Other';changed['installToIde']=True
        result=export_bridge(changed,R/'flprog_webui_next',Path(self.temp.name)/'other')
        self.assertEqual(result['projectHash'],self.export['projectHash'])
    def test_layout_and_resources_change_hash(self):
        changed=copy.deepcopy(self.doc);changed['pages'][0]['widgets'][0]['label']='Другая уставка'
        result=export_bridge(changed,R/'flprog_webui_next',Path(self.temp.name)/'other')
        self.assertNotEqual(result['projectHash'],self.export['projectHash'])
        frozen=self.call('/')[1]
        (self.site/'index.html').write_text('tampered')
        self.assertEqual(self.call('/')[1],frozen)
        with self.assertRaises(ValueError):State(self.site)
    def test_wrong_identity_or_hash_is_rejected(self):
        identity=self.state.client.info['identity'];identity['webHash']='0'*64
        self.assertEqual(self.call('/')[0],409)
        identity['webHash']=self.export['projectHash'];identity['webApi']=2
        self.assertEqual(self.call('/')[0],409)
    def test_metadata_and_batch_snapshot(self):
        self.assertEqual(self.call('/')[0],200)
        meta=json.loads(self.call('/flprog-webui/item?page=0')[1]);self.assertTrue(meta['widgetCatalog'])
        items=json.loads(self.call('/flprog-webui/item?widgets=main')[1]);self.assertEqual(len(items['items']),2)
        state=json.loads(self.call('/flprog-webui/state?page=main')[1]);self.assertEqual(state['values'],dict(setpoint=25.,switch=False))
        self.assertEqual(state['session'],str(self.state.client.session))
    def test_write_requires_fresh_session_and_does_not_retry(self):
        path='/flprog-webui/write?channel=setpoint&value=30.5&widget=setpoint_field'
        self.assertEqual(self.call(path,True)[0],409)
        self.assertEqual(self.call(path,True,str(self.state.client.session-1))[0],409)
        status,raw=self.call(path,True,str(self.state.client.session));self.assertEqual(status,202);self.assertTrue(json.loads(raw)['queued'])
        state=json.loads(self.call('/flprog-webui/state?page=main')[1]);self.assertEqual(state['values']['setpoint'],30.5)
    def test_range_step_widget_and_disabled_commands(self):
        s=str(self.state.client.session)
        for path in ['/flprog-webui/write?channel=setpoint&value=101&widget=setpoint_field','/flprog-webui/write?channel=setpoint&value=1.25&widget=setpoint_field','/flprog-webui/write?channel=switch&value=true&widget=setpoint_field']:
            self.assertIn(self.call(path,True,s)[0],(400,422))
        self.state.allow_writes=False
        self.assertEqual(self.call('/flprog-webui/write?channel=switch&value=true&widget=switch_widget',True,s)[0],403)
    def test_busy_and_enabled_are_read_again_before_write(self):
        w=self.state.project.widgets[0];w['bindings']=[dict(role='enabled',channel='switch')]
        p='/flprog-webui/write?channel=setpoint&value=31&widget=setpoint_field';s=str(self.state.client.session)
        self.assertEqual(self.call(p,True,s)[0],409)
        self.state.client.transport.values[102]=('bool',True)
        self.assertEqual(self.call(p,True,s)[0],202)
        w['bindings']=[dict(role='busy',channel='switch')]
        self.assertEqual(self.call(p,True,s)[0],409)
    def test_files_not_in_manifest_are_not_served(self):
        self.assertEqual(self.call('/firmware/FLProgBridgeProject.h')[0],404)
        self.assertEqual(self.call('/bridge.json')[0],404)

if __name__=='__main__':unittest.main(verbosity=2)
