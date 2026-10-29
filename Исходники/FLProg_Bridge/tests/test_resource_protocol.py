import os,struct,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).parent)]
from test_bridge import ProcessPort
from client import Client,BridgeError

@unittest.skipUnless(os.environ.get('BRIDGE_RESOURCE_PEER'),'Resource C++ peer required')
class ResourceProtocolTests(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ,BRIDGE_TEST_PEER=os.environ['BRIDGE_RESOURCE_PEER']):self.port=ProcessPort()
        self.client=Client(self.port);self.client.handshake()
    def tearDown(self):self.port.close()
    def test_metadata(self):
        self.assertEqual(self.client.info['services'],[4])
        meta=self.client.request(4,1)
        self.assertEqual(len(meta),44)
        self.assertEqual(struct.unpack('<BBHII',meta[:12]),(1,1,224,512,1024))
    def test_chunks_and_last_partial(self):
        for offset,count in ((0,224),(224,224),(448,224),(511,1)):
            data=self.client.request(4,2,struct.pack('<IH',offset,count))
            self.assertEqual(struct.unpack('<I',data[:4])[0],offset)
            self.assertEqual(data[4:],bytes(i%256 for i in range(offset,min(512,offset+count))))
    def test_bounds_and_no_write_operations(self):
        for op,payload in ((1,b'x'),(2,b''),(2,struct.pack('<IH',512,1)),(2,struct.pack('<IH',0,0)),(2,struct.pack('<IH',0,225)),(2,struct.pack('<IH',0xffffffff,1)),(3,b'')):
            with self.assertRaises(BridgeError):self.client.request(4,op,payload)
        self.assertEqual(len(self.client.request(4,1)),44)
if __name__=='__main__':unittest.main(verbosity=2)
