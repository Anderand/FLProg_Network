"""FLProg Bridge v1: bounded, service-neutral COBS/CRC32 frames."""
import struct
import zlib
from dataclasses import dataclass

HEADER = struct.Struct('<BBBBIQH')
MAX_PAYLOAD = 256
MAX_ENCODED = 280
CONTROL, WEBUI, MODBUS, MQTT = range(4)
WEB_RESOURCES = 4
OK, BAD_REQUEST, UNSUPPORTED, SESSION, BUSY, DENIED = range(6)


def cobs_encode(data):
    out = bytearray([0]); at = 0; code = 1
    for value in data:
        if value == 0:
            out[at] = code; at = len(out); out.append(0); code = 1
        else:
            out.append(value); code += 1
            if code == 255:
                out[at] = code; at = len(out); out.append(0); code = 1
    out[at] = code
    return bytes(out)


def cobs_decode(data):
    out = bytearray(); at = 0
    while at < len(data):
        code = data[at]; at += 1
        if not code or at + code - 1 > len(data):
            raise ValueError('invalid COBS')
        out.extend(data[at:at + code - 1]); at += code - 1
        if code != 255 and at < len(data): out.append(0)
    return bytes(out)


@dataclass(frozen=True)
class Frame:
    service: int
    operation: int
    sequence: int
    session: int
    payload: bytes = b''
    response: bool = False

    def encode(self):
        if len(self.payload) > MAX_PAYLOAD: raise ValueError('payload exceeds 256 bytes')
        raw = HEADER.pack(1, self.service, self.operation, int(self.response),
                          self.sequence, self.session, len(self.payload)) + self.payload
        return cobs_encode(raw + struct.pack('<I', zlib.crc32(raw))) + b'\0'

    @classmethod
    def decode(cls, encoded):
        raw = cobs_decode(encoded)
        if len(raw) < HEADER.size + 4: raise ValueError('short frame')
        version, service, operation, flags, seq, session, length = HEADER.unpack_from(raw)
        if version != 1 or flags not in (0, 1) or length > MAX_PAYLOAD:
            raise ValueError('unsupported frame')
        if len(raw) != HEADER.size + length + 4: raise ValueError('bad length')
        if zlib.crc32(raw[:-4]) != struct.unpack('<I', raw[-4:])[0]: raise ValueError('bad CRC')
        return cls(service, operation, seq, session, raw[HEADER.size:-4], bool(flags))


class Decoder:
    def __init__(self):
        self.buffer = bytearray(); self.overflow = False; self.errors = 0

    def feed(self, chunk):
        frames = []
        for value in chunk:
            if value == 0:
                if self.buffer and not self.overflow:
                    try: frames.append(Frame.decode(self.buffer))
                    except ValueError: self.errors += 1
                self.buffer.clear(); self.overflow = False
            elif not self.overflow:
                if len(self.buffer) == MAX_ENCODED:
                    self.buffer.clear(); self.overflow = True; self.errors += 1
                else: self.buffer.append(value)
        return frames
