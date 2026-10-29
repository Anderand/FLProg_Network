# coding: utf-8
import unittest,sys,os,struct,tempfile,json
from pathlib import Path
from unittest.mock import patch
r=Path(__file__).resolve().parents[2];w=Path(r'E:\SAI\FLProg_Network\_work\bridge_auto_20261029')
sys.path[:0]=[str(r/'flprog_bridge'),str(r/'flprog_bridge/tests'),str(r/'flprog_webui_next/tools')]
from client import Client,BridgeError,encode_value
from test_bridge import ProcessPort
from device_web import device_site
from build_compatibility import sketch_report
class AutoTests(unittest.TestCase):
 def test_both_blocks_hello_read_only_and_flash(self):
  for kind in ('basic','professional'):
   with self.subTest(kind=kind),patch.dict(os.environ,BRIDGE_TEST_PEER=str(w/(kind+'_auto_peer.exe'))):
    port=ProcessPort();c=Client(port)
    try:
     info=c.handshake();self.assertEqual(info['services'],[1,4]);self.assertEqual(info['identity']['projectId'],'auto-sample');self.assertEqual(info['identity']['firmware'],'1.0.12-AUTO');self.assertEqual(info['identity']['model'],'Test "model"')
     self.assertEqual(c.read_channels([101])[101]['value'],0)
     with self.assertRaises(BridgeError) as e:c.request(1,3,b'\x65'+encode_value('float',3.5))
     self.assertEqual(e.exception.status,403)
     with tempfile.TemporaryDirectory() as folder:
      site,report=device_site(c,cache=Path(folder));self.assertFalse(report['cacheHit']);self.assertEqual(json.loads((site/'project.json').read_text(encoding='utf-8'))['project']['id'],'auto-sample')
    finally:c.close()
 def test_passport_and_direct_bridge_entry(self):
  with tempfile.TemporaryDirectory() as folder:
   sketch=Path(folder)/'test.ino';sketch.write_text('#include <auto-sample_bridge_entry.h>\nvoid setup(){}\nvoid loop(){}',encoding='utf-8')
   result=sketch_report(sketch,Path(r'C:\F-981\FLProg\ideV8'),w/'libraries');self.assertTrue(result['ok'],result)
 def test_catalog_and_bridge_entry_are_covered_by_passport(self):
  lib=w/'libraries/FLProg_WebUI_Project_auto-sample';m=json.loads((lib/'WEBUI_COMPATIBILITY.json').read_text(encoding='utf-8'));self.assertEqual(m['catalogApi'],1);self.assertEqual(m['bridgeBlockApi'],1)
  self.assertIn('src/auto_sample_widget_catalog.h',m['files']);self.assertIn('src/auto-sample_bridge_entry.h',m['files'])
if __name__=='__main__':unittest.main(verbosity=2)
