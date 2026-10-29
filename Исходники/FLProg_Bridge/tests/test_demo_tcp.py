import json
import sys
import time
import unittest
import threading
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo_tcp import DemoTcpServer
from tcp_port import TcpPort
from client import Client, BridgeError, encode_value
from http_api import State, make_server


class DemoTcpTests(unittest.TestCase):
    def setUp(self):
        self.sim = DemoTcpServer()
        self.client = Client(TcpPort(self.sim.endpoint), timeout=.3)

    def tearDown(self):
        self.client.close()
        self.sim.close()
        self.assertFalse(self.sim.thread.is_alive())

    def test_fragmented_tcp_read_write(self):
        self.assertEqual(self.sim.server.server_address[0], '127.0.0.1')
        self.client.handshake()
        self.assertEqual(self.client.read_channels([101, 102])[101]['value'], 25.)
        self.client.request(1, 3, bytes([101]) + encode_value('float', 31.5))
        self.assertEqual(self.client.read_channels([101])[101]['value'], 31.5)
        self.assertEqual(self.sim.command_count, 1)
        self.assertEqual(self.client.decoder.errors, 0)

    def test_no_uart_response_is_distinguished_from_tcp_failure(self):
        self.sim.muted = True
        with self.assertRaises(BridgeError) as e:
            self.client.handshake()
        self.assertIn('TCP-соединение', str(e.exception))
        self.assertIn('UART', str(e.exception))
        self.assertNotIn('Результат команды', str(e.exception))
        self.assertFalse(self.client.online)

    def test_lost_command_is_not_replayed_after_new_session(self):
        self.client.handshake()
        old = self.client.session
        self.sim.muted = True
        with self.assertRaises(BridgeError) as e:
            self.client.request(1, 3, bytes([101]) + encode_value('float', 44.))
        self.assertIn('Результат команды неизвестен', str(e.exception))
        self.assertEqual(self.sim.command_count, 1)
        self.sim.muted = False
        self.sim.drop_clients()
        deadline = time.monotonic() + 2
        while self.sim._single.locked() and time.monotonic() < deadline:
            time.sleep(.005)
        self.client.transport.open()
        self.client.handshake()
        self.assertNotEqual(old, self.client.session)
        self.assertEqual(self.client.read_channels([101])[101]['value'], 25.)
        self.assertEqual(self.sim.command_count, 1)

    def test_web_api_is_demo_and_read_only_by_default(self):
        self.client.handshake()
        state = State()
        state.client = self.client
        state.demo = True
        server = make_server(state)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        try:
            with urllib.request.urlopen(base + '/api/v1/status') as response:
                status = json.load(response)
            self.assertTrue(status['online'] and status['demo'])
            self.assertFalse(status['writesEnabled'])
            data = json.dumps(dict(type='float', value=30., session=str(self.client.session))).encode()
            request = urllib.request.Request(base + '/api/v1/channels/101', data=data,
                                             headers={'Content-Type': 'application/json', 'X-FLProg-Bridge': '1'})
            with self.assertRaises(urllib.error.HTTPError) as e:
                urllib.request.urlopen(request)
            self.assertEqual(e.exception.code, 403)
            self.assertEqual(self.sim.command_count, 0)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
