"""Explicitly selected TCP link for the ESP UART prototype. No command retry."""
import select
import socket
from urllib.parse import urlsplit


def endpoint(value):
    parts=urlsplit(value if value.startswith('tcp://') else 'tcp://'+value)
    try:port=parts.port
    except ValueError:raise ValueError('TCP-порт должен быть числом 1..65535')
    if parts.scheme!='tcp' or not parts.hostname or port is None or not 1<=port<=65535 or parts.username is not None or parts.password is not None or parts.path or parts.query or parts.fragment:
        raise ValueError('Укажите tcp://IP:порт без пути, пароля и параметров')
    if any(c.isspace() for c in parts.hostname):raise ValueError('В адресе не должно быть пробелов')
    return parts.hostname,port


class TcpPort:
    def __init__(self,value):
        self.host,self.port=endpoint(value);self.sock=None;self.open()
    def open(self):
        self.close()
        sock=socket.create_connection((self.host,self.port),timeout=3)
        sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        sock.setblocking(False);self.sock=sock
    def close(self):
        if self.sock is not None:self.sock.close();self.sock=None
    def write(self,data):
        if self.sock is None:raise OSError('TCP соединение закрыто')
        try:return self.sock.send(data)
        except BlockingIOError:return 0
    def read(self,size):
        if self.sock is None:raise OSError('TCP соединение закрыто')
        if not select.select([self.sock],[],[],.03)[0]:return b''
        try:data=self.sock.recv(size)
        except BlockingIOError:return b''
        if not data:raise OSError('TCP соединение потеряно')
        return data
