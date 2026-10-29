# coding: utf-8
import json
import os
from pathlib import Path
import queue
import random
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from protocol import Frame, Decoder, cobs_encode, cobs_decode, MAX_ENCODED
from client import Client, BridgeError, encode_value, decode_value
from demo import DemoPort
from http_api import State, make_server


class ProcessPort:
    def __init__(self):
        self.p=subprocess.Popen([os.environ['BRIDGE_TEST_PEER']],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.output=queue.Queue()
        def pump():
            while True:
                data=self.p.stdout.read(1)
                if not data:break
                self.output.put(data)
        threading.Thread(target=pump,daemon=True).start()
    def write(self,raw):self.p.stdin.write(raw);self.p.stdin.flush();return len(raw)
    def read(self,n):
        try:return self.output.get(timeout=0.03)
        except queue.Empty:return b''
    def close(self):
        self.p.stdin.close();self.p.wait(timeout=2)
        if self.p.returncode:raise RuntimeError(self.p.stderr.read().decode(errors='replace'))
        self.p.stdout.close();self.p.stderr.close()


class ProtocolTests(unittest.TestCase):
    def test_vectors(self):
        rng=random.Random(14)
        for n in range(257):
            p=bytes(rng.randrange(256) for _ in range(n));f=Frame(1,3,123,998877,p)
            self.assertEqual(Frame.decode(f.encode()[:-1]),f)
            self.assertLessEqual(len(f.encode())-1,MAX_ENCODED)
        for data in (bytes(256),bytes([255])*256,b'a\0b',bytes(range(256))):
            self.assertEqual(cobs_decode(cobs_encode(data)),data)
    def test_noise_fragmentation_and_crc(self):
        d=Decoder();f=Frame(1,2,1,2,b'hello');broken=bytearray(f.encode());broken[5]^=1
        stream=b'garbage\0'+bytes(broken)+bytes([1])*2000+b'\0'+f.encode()
        output=[]
        for b in stream:output.extend(d.feed(bytes([b])))
        self.assertEqual(output,[f]);self.assertGreaterEqual(d.errors,3)
    def test_typed_values(self):
        for kind,val in [('bool',False),('bool',True),('int32',-2147483648),('float',12.5),('text','Привет')]:
            self.assertEqual(decode_value(encode_value(kind,val)),val)
        for kind,val in [('bool',1),('int32',True),('int32',2**31),('float',float('nan')),('text','я'*32),('text','a\0b')]:
            with self.assertRaises(ValueError):encode_value(kind,val)
    def test_timeout_does_not_replay(self):
        class Silent:
            writes=0
            def write(self,data):self.writes+=1;return len(data)
            def read(self,n):time.sleep(.001);return b''
        p=Silent();c=Client(p,timeout=.02);c.online=True;c.info={'services':[1]};c.session=99
        with self.assertRaises(BridgeError):c.request(1,3,b'abc')
        self.assertEqual(p.writes,1);self.assertFalse(c.online)


@unittest.skipUnless(os.environ.get('BRIDGE_TEST_PEER'),'C++ peer not built')
class CrossLanguageTests(unittest.TestCase):
    def setUp(self):
        self.port=ProcessPort();self.c=Client(self.port)
        try:self.c.handshake()
        except Exception:self.port.close();raise
    def tearDown(self):self.port.close()
    def test_discovery_and_read(self):
        self.assertEqual(self.c.request(0,2),b'')
        self.assertEqual(self.c.info['services'],[1]);self.assertEqual(self.c.info['identity']['projectId'],'host-test')
        self.assertEqual(decode_value(self.c.request(1,1,b'\x65')),25)
        self.assertEqual(self.c.request(1,2,b'\x65'),b'\x65\x01\x02setpoint')
    def test_system_channel_refresh_before_read(self):
        self.assertEqual(decode_value(self.c.request(1,1,b'\x0a')),456)
    def test_batch_reads_and_rejects_secret(self):
        result=self.c.read_channels([10,101,102,103]);self.assertEqual(result[10]['value'],456);self.assertEqual(result[101]['value'],25)
        self.assertEqual(result[102]['value'],False)
        with self.assertRaises(BridgeError):self.c.read_channels([101,104])
    def test_batch_capacity_is_bounded(self):
        self.c.request(1,3,bytes([103])+encode_value('text','x'*63))
        raw=self.c.request(1,4,bytes([103])*16)
        self.assertEqual(raw[0],3);self.assertLessEqual(len(raw),254)
        with self.assertRaises(BridgeError):self.c.request(1,4,bytes([103])*17)
    def test_write_and_policy(self):
        self.c.request(1,3,b'\x65'+encode_value('int32',42),self.c.session)
        self.assertEqual(decode_value(self.c.request(1,1,b'\x65')),42)
        for ch,payload in [(10,encode_value('int32',1)),(101,encode_value('int32',200)),(101,encode_value('bool',True))]:
            with self.assertRaises(BridgeError):self.c.request(1,3,bytes([ch])+payload,self.c.session)
        self.assertEqual(decode_value(self.c.request(1,1,b'\x65')),42)
    def test_no_secret_read_or_stale_session(self):
        with self.assertRaises(BridgeError):self.c.request(1,1,b'\x68')
        with self.assertRaises(BridgeError):self.c.request(1,3,b'\x65'+encode_value('int32',45),self.c.session+1)
        self.assertEqual(decode_value(self.c.request(1,1,b'\x65')),25)
    def test_unconsumed_command_not_overwritten(self):
        self.c.request(1,3,b'\x65'+encode_value('int32',41))
        with self.assertRaises(BridgeError) as result:self.c.request(1,3,b'\x65'+encode_value('int32',42))
        self.assertEqual(result.exception.status,409)
        self.assertEqual(decode_value(self.c.request(1,1,b'\x65')),41)
    def test_bool_and_utf8(self):
        for ch,kind,value in [(102,'bool',True),(103,'text','Привет')]:
            self.c.request(1,3,bytes([ch])+encode_value(kind,value),self.c.session)
            self.assertEqual(decode_value(self.c.request(1,1,bytes([ch]))),value)
    def test_duplicate_request_rejected(self):
        self.c.request(1,3,b'\x65'+encode_value('int32',41))
        self.c.sequence-=1
        with self.assertRaises(BridgeError):self.c.request(1,3,b'\x65'+encode_value('int32',42))
        self.assertEqual(decode_value(self.c.request(1,1,b'\x65')),41)
    def test_corrupt_and_oversize_recover(self):
        self.port.write(b'\1'*3000+b'\0bad\0')
        self.assertEqual(decode_value(self.c.request(1,1,b'\x65')),25)
    def test_reset_requires_handshake(self):
        old=self.c.session;self.port.close();self.port=ProcessPort();self.c.transport=self.port
        with self.assertRaises(BridgeError):self.c.request(1,3,b'\x65'+encode_value('int32',50))
        self.assertFalse(self.c.online);self.c.handshake();self.assertNotEqual(old,self.c.session)
        self.assertEqual(decode_value(self.c.request(1,1,b'\x65')),25)


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.state=State();self.state.client=Client(DemoPort());self.state.client.handshake();self.state.demo=True
        self.server=make_server(self.state);self.url='http://127.0.0.1:'+str(self.server.server_port)
        threading.Thread(target=self.server.serve_forever,daemon=True).start()
    def tearDown(self):self.server.shutdown();self.server.server_close()
    def request(self,path,body=None,headers=None):
        h={'Content-Type':'application/json','X-FLProg-Bridge':'1'};h.update(headers or {})
        r=urllib.request.Request(self.url+path,data=json.dumps(body).encode() if body is not None else None,headers=h)
        try:
            with urllib.request.urlopen(r) as response:return response.status,response.read()
        except urllib.error.HTTPError as response:return response.code,response.read()
    def test_read_and_no_write_default(self):
        self.assertEqual(json.loads(self.request('/api/v1/channels/101')[1])['value'],25)
        self.assertEqual(self.request('/api/v1/channels/101',{})[0],403)
    def test_command_ack_and_stale_session(self):
        self.state.allow_writes=True;s=str(self.state.client.session)
        body=dict(type='float',value=30.5,session=s)
        code,raw=self.request('/api/v1/channels/101',body);self.assertEqual(code,200)
        self.assertFalse(json.loads(raw)['confirmed'])
        self.state.client.handshake()
        self.assertEqual(self.request('/api/v1/channels/101',body)[0],409)
    def test_origin_and_header_guards(self):
        self.state.allow_writes=True
        for headers in ({'Origin':'http://evil.invalid'},{'X-FLProg-Bridge':'0'},{'Host':'evil.invalid'}):
            self.assertEqual(self.request('/api/v1/channels/101',{},headers)[0],403)
    def test_static_manifest_and_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'index.html').write_text('test');(root/'bridge.json').write_text(json.dumps(dict(api='flprog.bridge/1',projectId='other')))
            site=State(root);self.state.site=site.site;self.state.manifest=site.manifest
            self.assertEqual(self.request('/')[0],409)
            self.state.manifest['projectId']='bridge-demo'
            self.assertEqual(self.request('/')[1],b'test')
            self.assertEqual(self.request('/%2e%2e/secret')[0],403)
            self.assertEqual(self.request('/bridge.json')[0],404)
    def test_bounds_and_system_protection(self):
        self.state.allow_writes=True
        self.assertEqual(self.request('/api/v1/channels/256')[0],400)
        self.assertEqual(self.request('/api/v1/channels/10',{})[0],403)
        self.assertEqual(self.request('/api/v1/channels/101',{'type':'float','value':1})[0],400)

if __name__=='__main__':unittest.main(verbosity=2)
