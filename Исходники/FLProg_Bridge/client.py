# coding: utf-8
"""One outstanding request; no automatic replay of commands."""
import json
import math
import secrets
import struct
import threading
import time
from protocol import Frame, Decoder, OK, SESSION


class BridgeError(Exception):
    def __init__(self, message, status=503):
        super().__init__(message); self.status = status


def encode_value(kind, value):
    if kind == 'bool' and type(value) is bool: return b'\0' + bytes([value])
    if kind == 'int32' and type(value) is int and -(2**31) <= value < 2**31:
        return b'\1' + struct.pack('<i', value)
    if kind == 'float' and type(value) in (int, float) and math.isfinite(value):
        try: result = struct.pack('<f', value)
        except (OverflowError, struct.error): raise ValueError('Число не помещается в float32')
        if not math.isfinite(struct.unpack('<f', result)[0]): raise ValueError('Неконечное число')
        return b'\2' + result
    if kind == 'text' and isinstance(value, str) and '\0' not in value:
        raw = value.encode('utf-8')
        if len(raw) <= 63: return b'\3' + raw
    raise ValueError('Неверный тип, значение или длина канала')


def decode_value(data):
    if not data: raise BridgeError('Пустое значение канала', 502)
    if data[0] == 0 and len(data) == 2 and data[1] in (0, 1): return bool(data[1])
    if data[0] in (1, 2) and len(data) == 5:
        result = struct.unpack('<i' if data[0] == 1 else '<f', data[1:])[0]
        if isinstance(result, float) and not math.isfinite(result): raise BridgeError('Неконечное значение', 502)
        return result
    if data[0] == 3 and len(data) <= 64: return data[1:].decode('utf-8')
    raise BridgeError('Неверное значение канала', 502)


class Client:
    def __init__(self, transport, timeout=1.5):
        self.transport = transport; self.timeout = timeout; self.lock = threading.Lock()
        self.decoder = Decoder(); self.session = 0; self.sequence = 0
        self.info = None; self.online = False; self.last_error = ''
        self.exchanges = 0

    def close(self):
        with self.lock:
            self.online = False; self.transport.close()

    def handshake(self):
        with self.lock:
            self.session = secrets.randbits(64) or 1; self.sequence = 0; self.online = False
            self.decoder = Decoder()
            raw = self._exchange(0, 1, b'FLPBRIDGE1')
            try: info = json.loads(raw.decode('utf-8'))
            except (ValueError, UnicodeError): raise BridgeError('Неверное описание контроллера', 502)
            if info.get('protocol') != 1 or not isinstance(info.get('services'), list):
                raise BridgeError('Несовместимый протокол контроллера', 502)
            self.info = info; self.online = True; self.last_error = ''
            return info

    def request(self, service, operation, payload=b'', expected_session=None):
        if not self.lock.acquire(timeout=0.1): raise BridgeError('Мост занят другим запросом', 409)
        try:
            if not self.online: raise BridgeError('Нет связи. Подключитесь заново.')
            if expected_session is not None and expected_session != self.session:
                raise BridgeError('Сеанс изменился. Обновите данные перед командой.', 409)
            if service != 0 and service not in self.info['services']: raise BridgeError('Служба не поддерживается контроллером', 501)
            return self._exchange(service, operation, payload)
        finally: self.lock.release()

    def _exchange(self, service, operation, payload):
        self.sequence += 1
        if self.sequence > 0xffffffff:
            self.online = False; raise BridgeError('Требуется новый сеанс')
        frame = Frame(service, operation, self.sequence, self.session, payload)
        wire = frame.encode(); until = time.monotonic() + self.timeout
        try:
            # Leading delimiter resynchronises after an interrupted frame.
            pending = b'\0' + wire
            while pending:
                if time.monotonic() >= until: raise TimeoutError()
                written = self.transport.write(pending)
                if written: pending = pending[written:]
                else: time.sleep(0.001)
            while time.monotonic() < until:
                for response in self.decoder.feed(self.transport.read(280)):
                    if not response.response or (response.service, response.operation, response.sequence, response.session) != (service, operation, self.sequence, self.session): continue
                    if not response.payload: raise OSError('Пустой ответ протокола')
                    status = response.payload[0]
                    if status != OK:
                        if status == SESSION: self.online = False
                        raise BridgeError({1:'Неверный запрос', 2:'Служба или операция не поддерживается', 3:'Контроллер перезапущен: подключитесь заново', 4:'Контроллер занят', 5:'Команда запрещена настройками ПЛК', 6:'Запрос уже обработан; повтор не выполнялся'}.get(status, 'Ошибка контроллера'), {1:400,2:501,3:409,4:409,5:403,6:409}.get(status,502))
                    self.exchanges += 1
                    return response.payload[1:]
            raise TimeoutError()
        except BridgeError: raise
        except (OSError, TimeoutError) as error:
            self.online = False
            if isinstance(error, TimeoutError) and hasattr(self.transport, 'host'):
                self.last_error = 'TCP-соединение с мостом установлено, но ответа ПЛК нет. Проверьте UART, скорость и прошивку ПЛК.'
            else:
                self.last_error = 'Нет ответа от контроллера. Проверьте соединение и настройки транспорта.'
            if service == 1 and operation == 3:
                self.last_error += ' Результат команды неизвестен; повторной отправки не было.'
            raise BridgeError(self.last_error) from error

    def status(self):
        return dict(online=self.online, session=str(self.session), device=self.info,
                    error=self.last_error, exchanges=self.exchanges, badFrames=self.decoder.errors)

    def read_channels(self,numbers,expected_session=None):
        numbers=list(numbers);result={}
        if not numbers or len(numbers)>256 or len(set(numbers))!=len(numbers) or any(type(n) is not int or not 0<=n<=255 for n in numbers):
            raise ValueError('Пакет чтения: 1..256 разных номеров 0..255')
        session=self.session if expected_session is None else expected_session
        while numbers:
            part=numbers[:16];raw=self.request(1,4,bytes(part),session)
            if not raw or not 1<=raw[0]<=len(part):raise BridgeError('Неверный пакет значений',502)
            at=1
            for number in part[:raw[0]]:
                if at+2>len(raw) or raw[at]!=number:raise BridgeError('Неверный порядок пакета',502)
                length=raw[at+1];at+=2;data=raw[at:at+length]
                if not length or len(data)!=length:raise BridgeError('Оборванный пакет значений',502)
                result[number]=dict(type=data[0],value=decode_value(data));at+=length
            if at!=len(raw):raise BridgeError('Лишние данные в пакете',502)
            del numbers[:raw[0]]
        return result
