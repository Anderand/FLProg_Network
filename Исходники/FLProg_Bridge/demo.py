"""Explicit offline simulator. Never enumerates or opens a serial port."""
import json
import time
from protocol import Frame, Decoder
from client import encode_value


class DemoPort:
    def __init__(self):
        self.decoder=Decoder();self.output=bytearray();self.session=0;self.sequence=0
        self.values={10:('text','DEMO — без контроллера'),101:('float',25.0),102:('bool',False)}

    def write(self, raw):
        for request in self.decoder.feed(raw):
            status=0;payload=b''
            if request.service==0 and request.operation==1 and request.payload==b'FLPBRIDGE1':
                if self.session!=request.session:self.sequence=request.sequence
                self.session=request.session
                payload=json.dumps(dict(protocol=1,services=[1],identity=dict(projectId='bridge-demo',model='DEMO',firmware='0.1.0')),ensure_ascii=False).encode()
            elif request.session!=self.session:status=3
            elif request.sequence<=self.sequence:status=6
            else:
                self.sequence=request.sequence
                if request.service==0 and request.operation==2:status=0 if not request.payload else 1
                elif request.service!=1:status=2
                elif request.operation==4:
                    if not request.payload or any(ch not in self.values for ch in request.payload):status=1
                    else:
                        records=[];total=1
                        for ch in request.payload:
                            kind,value=self.values[ch];typed=encode_value(kind,value)
                            if total+2+len(typed)>255:break
                            records.append(bytes([ch,len(typed)])+typed);total+=2+len(typed)
                        payload=bytes([len(records)])+b''.join(records)
                elif not request.payload or request.payload[0] not in self.values:status=1
                else:
                    ch=request.payload[0];kind,value=self.values[ch]
                    if request.operation==1:payload=encode_value(kind,value)
                    elif request.operation==2:
                        payload=bytes([ch,{'bool':0,'int32':1,'float':2,'text':3}[kind],0 if ch<=100 else 2])+('channel_'+str(ch)).encode()
                    elif request.operation==3:
                        from client import decode_value
                        if ch<=100:status=5
                        else:
                            try:
                                data=request.payload[1:]
                                if not data or data[0]!=encode_value(kind,value)[0]:raise ValueError()
                                self.values[ch]=(kind,decode_value(data))
                            except Exception:status=1
                    else:status=2
            self.output.extend(Frame(request.service,request.operation,request.sequence,request.session,bytes([status])+payload,True).encode())
        return len(raw)

    def read(self,n):
        if not self.output:time.sleep(0.005)
        data=bytes(self.output[:n]);del self.output[:n];return data

    def close(self):self.output.clear()
