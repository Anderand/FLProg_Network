"""Loopback-only TCP/UART simulator. Never connects to ESP, COM or a real PLC."""
import socket
import socketserver
import threading
from demo import DemoPort
from protocol import Decoder


class DemoTcpServer:
    def __init__(self):
        owner = self
        self.muted = False
        self.closed = False
        self.command_count = 0
        self._peer = None
        self._lock = threading.Lock()
        self._single = threading.Lock()

        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                if not owner._single.acquire(False):
                    return
                port = DemoPort()
                decoder = Decoder()
                with owner._lock:
                    owner._peer = self.request
                self.request.settimeout(.1)
                try:
                    while not owner.closed:
                        try:
                            raw = self.request.recv(64)
                        except socket.timeout:
                            continue
                        if not raw:
                            break
                        for frame in decoder.feed(raw):
                            if frame.service == 1 and frame.operation == 3:
                                owner.command_count += 1
                        if owner.muted:
                            continue  # Missing UART: discard; do not queue for later replay.
                        port.write(raw)
                        while port.output:
                            self.request.sendall(port.read(17))
                except OSError:
                    pass
                finally:
                    port.close()
                    with owner._lock:
                        if owner._peer is self.request:
                            owner._peer = None
                    owner._single.release()

        class Server(socketserver.ThreadingTCPServer):
            daemon_threads = True
            allow_reuse_address = True

        self.server = Server(('127.0.0.1', 0), Handler)
        self.endpoint = 'tcp://127.0.0.1:' + str(self.server.server_address[1])
        self.thread = threading.Thread(target=lambda: self.server.serve_forever(poll_interval=.05), daemon=True)
        self.thread.start()

    def drop_clients(self):
        with self._lock:
            peer = self._peer
            if peer is not None:
                try:
                    peer.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.drop_clients()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1)
