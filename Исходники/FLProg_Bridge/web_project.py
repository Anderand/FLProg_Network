# coding: utf-8
"""Existing WebUI HTTP contract over a bounded serial channel service."""
import math
import threading
from client import BridgeError,encode_value
from field_pattern import pattern_matches

TYPE={'bool':0,'int32':1,'float':2,'text':3}


class WebProject:
    def __init__(self,document):
        self.document=document
        self.channels={c['id']:c for c in document['channels']}
        self.pages=document['pages'];self.widgets=[]
        self.operation=threading.Lock();self.session=None;self.revision=1;self.values={}
        for page in self.pages:
            for widget in page['widgets']:
                self.widgets.append(dict(widget,page=page['id'],groupStyle={'border':True,'padding':12,'gap':10,**page.get('groupStyles',{}).get(widget.get('group','').strip(),{})},
                    min=widget.get('min',0),max=widget.get('max',100),step=widget.get('step',1),
                    confirmation=widget.get('confirmation','Отправить команду?' if widget['type']=='button' else '')))

    def secret(self,cid):
        return self.channels[cid].get('secret') is True or self.channels[cid]['direction']=='command' or any(w['type']=='password-input' and self.target(w)==cid for w in self.widgets)

    @staticmethod
    def target(widget):
        return next((b['channel'] for b in widget.get('bindings',[]) if b['role']=='setpoint'),widget.get('channel'))

    def item(self,params):
        if 'widgets' in params:
            page=params['widgets'];items=[[i,w] for i,w in enumerate(self.widgets) if w['page']==page]
            if not any(p['id']==page for p in self.pages):raise BridgeError('Страница не найдена',404)
            return dict(page=page,items=items)
        if 'page' in params:
            number=int(params['page'])
            if not 0<=number<len(self.pages):raise BridgeError('Страница не найдена',404)
            page=self.pages[number]
            return dict(id=page['id'],title=page['title'],indices=[i for i,w in enumerate(self.widgets) if w['page']==page['id']],pages=len(self.pages),
                        theme=self.document.get('theme',{}),polling=self.document.get('polling',dict(intervalMs=1300,pauseWhenHidden=True)),widgetCatalog=True)
        number=int(params.get('index','-1'))
        if not 0<=number<len(self.widgets):raise BridgeError('Виджет не найден',404)
        return self.widgets[number]

    def read(self,client,ids,session):
        ids=list(dict.fromkeys(ids))
        for cid in ids:
            if cid not in self.channels or self.secret(cid):raise BridgeError('Канал недоступен для чтения',403)
        if not ids:return {}
        raw=client.read_channels([self.channels[cid]['index'] for cid in ids],session)
        values={}
        for cid in ids:
            item=raw[self.channels[cid]['index']]
            if item['type']!=TYPE[self.channels[cid]['type']]:raise BridgeError('Тип канала не совпал с проектом',409)
            values[cid]=item['value']
        return values

    def snapshot(self,client,params):
        if not self.operation.acquire(timeout=.1):raise BridgeError('Чтение страницы уже выполняется',409)
        try:
            session=client.session
            if 'channel' in params:
                cid=params['channel'];return dict(channel=cid,value=self.read(client,[cid],session)[cid],session=str(session))
            page=params.get('page')
            if not any(p['id']==page for p in self.pages):raise BridgeError('Страница не найдена',404)
            ids=[]
            for w in self.widgets:
                if w['page']!=page:continue
                candidates=[w.get('channel')]+[b['channel'] for b in w.get('bindings',[])]
                ids.extend(cid for cid in candidates if cid in self.channels and not self.secret(cid))
            if 'system_uptime' in self.channels:ids.append('system_uptime')
            data=self.read(client,ids,session)
            if self.session!=session:self.values={};self.revision=1;self.session=session
            if any(self.values.get(k)!=v for k,v in data.items()):self.revision+=1
            self.values.update(data)
            return dict(values=data,revision=self.revision,uptime=int(data.get('system_uptime',0))*1000,session=str(session))
        finally:self.operation.release()

    def write(self,client,params,session):
        if not self.operation.acquire(timeout=.1):raise BridgeError('Мост занят чтением страницы',409)
        try:
            cid=params.get('channel');text=params.get('value')
            if cid not in self.channels or text is None:raise BridgeError('Не указан канал или значение',400)
            channel=self.channels[cid]
            if channel['index']<=100 or channel['direction']=='publish':raise BridgeError('Канал только для чтения',403)
            widget=next((w for w in self.widgets if w['id']==params.get('widget')),None)
            if widget is None or self.target(widget)!=cid:raise BridgeError('Виджет не соответствует команде',400)
            affected=[w for w in self.widgets if self.target(w)==cid]
            gates=[b for w in affected for b in w.get('bindings',[]) if b['role'] in ('enabled','busy')]
            gate_values=self.read(client,[b['channel'] for b in gates],session)
            for gate in gates:
                other=self.channels[gate['channel']]
                if other['type']!='bool' or (gate['role']=='busy' and gate_values[gate['channel']] is True) or (gate['role']=='enabled' and gate_values[gate['channel']] is not True):
                    raise BridgeError('Управление заблокировано: busy/enabled',409)
            if len(text.encode('utf-8'))>widget.get('maxLength',63) or '\0' in text:raise BridgeError('Слишком длинное значение',422)
            if not pattern_matches(widget.get('pattern',''),text):raise BridgeError(widget.get('validationMessage') or 'Значение не соответствует шаблону',422)
            if channel['type']=='bool':
                if text not in ('true','false','1','0'):raise BridgeError('Требуется bool',422)
                value=text in ('true','1')
            elif channel['type']=='int32':
                try:value=int(text)
                except ValueError:raise BridgeError('Требуется целое число',422)
            elif channel['type']=='float':
                try:value=float(text)
                except ValueError:raise BridgeError('Требуется число',422)
            else:value=text
            if widget['type'] in ('number-input','slider'):
                if not isinstance(value,(int,float)) or not math.isfinite(value) or not widget['min']<=value<=widget['max']:raise BridgeError('Значение вне диапазона',422)
                step=widget['step']
                if step and abs((value-widget['min'])/step-round((value-widget['min'])/step))>.001:raise BridgeError('Значение не соответствует шагу',422)
            client.request(1,3,bytes([channel['index']])+encode_value(channel['type'],value),session)
            return dict(queued=True,session=str(session),confirmed=False)
        finally:self.operation.release()
