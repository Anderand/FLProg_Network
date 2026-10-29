# coding: utf-8
"""Loopback-only HTTP facade. Static pages use the documented public API."""
import json
import hashlib
import mimetypes
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qs
from client import BridgeError, encode_value, decode_value
from web_project import WebProject
VERSION='0.4.1-preview.1'


class State:
    def __init__(self, site=None, allow_writes=False):
        self.client=None;self.allow_writes=allow_writes;self.demo=False;self.auto_reconnect=True
        self.site=Path(site).resolve() if site else None;self.manifest=None;self.project=None;self.resources={}
        self.webSource='local' if site else 'generic';self.resourceReport=None
        self.resourceLoading=False;self.resourceProgress=None
        self.fallbackSite=self.site
        if self.site:
            self.manifest=json.loads((self.site/'bridge.json').read_text(encoding='utf-8'))
            if self.manifest.get('api')!='flprog.bridge/1' or not self.manifest.get('projectId'):
                raise ValueError('bridge.json: требуются api=flprog.bridge/1 и projectId')
            self.file(self.manifest.get('entry','index.html'))
            if self.manifest.get('renderer')=='flprog.webui/1':
                files=self.manifest.get('files',{})
                if not files or self.manifest.get('webApi')!=1:raise ValueError('Неполный паспорт веб-проекта')
                if len(files)>64:raise ValueError('В паспорте больше 64 ресурсов')
                for name,digest in files.items():
                    data=self.file(name).read_bytes()
                    if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Ресурс проекта изменён: '+name)
                    self.resources[name]=data
                raw=json.dumps(dict(api='flprog.bridge.web/1',files=files),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
                if hashlib.sha256(raw).hexdigest()!=self.manifest.get('projectHash'):raise ValueError('Неверный хеш веб-проекта')
                self.project=WebProject(json.loads(self.resources[self.manifest['project']].decode('utf-8')))
                if self.project.document['project']['id']!=self.manifest['projectId']:raise ValueError('ID проекта не совпал с паспортом')

    def file(self,path):
        target=(self.site/path).resolve()
        try:target.relative_to(self.site)
        except ValueError:raise BridgeError('Путь вне папки сайта',403)
        if not target.is_file() or target.name=='bridge.json':raise BridgeError('Файл не найден',404)
        if self.manifest and self.manifest.get('files') and target.relative_to(self.site).as_posix() not in self.manifest['files']:
            raise BridgeError('Ресурс не включён в паспорт сайта',404)
        if target.stat().st_size>4*1024*1024:raise BridgeError('Ресурс больше 4 МиБ',413)
        return target

    def active(self):
        if self.resourceLoading:raise BridgeError('Загружаются ресурсы веба из Flash ПЛК',503)
        c=self.client
        if c is None or not c.online:raise BridgeError('Контроллер не подключён')
        if self.manifest and c.info.get('identity',{}).get('projectId')!=self.manifest['projectId']:
            raise BridgeError('ID сайта не совпадает с проектом контроллера',409)
        if self.manifest and self.manifest.get('projectHash'):
            identity=c.info.get('identity',{})
            if identity.get('webApi')!=self.manifest.get('webApi') or identity.get('webHash')!=self.manifest['projectHash']:
                raise BridgeError('Версия API или хеш веб-интерфейса не совпали с прошивкой. Пересоберите проект и ПЛК.',409)
        return c


def make_server(state,port=0):
    class Handler(BaseHTTPRequestHandler):
        protocol_version='HTTP/1.0'
        def log_message(self,*args):pass
        def setup(self):
            super().setup();self.connection.settimeout(3)
        def reply(self,code,value,mime='application/json; charset=utf-8'):
            if not isinstance(value,bytes):value=json.dumps(value,ensure_ascii=False,allow_nan=False).encode('utf-8')
            self.send_response(code);self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(value)));self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff');self.send_header('X-Frame-Options','DENY')
            self.end_headers();self.wfile.write(value)
        def check_host(self):
            expected='127.0.0.1:'+str(self.server.server_port)
            if self.headers.get('Host')!=expected:raise BridgeError('Неверный адрес локального моста',403)
            origin=self.headers.get('Origin')
            if origin and origin!='http://'+expected:raise BridgeError('Другой источник страницы',403)
        def do_GET(self):
            try:
                self.check_host();path=urlsplit(self.path).path
                if path=='/api/v1/status':
                    result=state.client.status() if state.client else dict(online=False,session='0',device=None)
                    result.update(api='flprog.bridge/1',version=VERSION,demo=state.demo,writesEnabled=state.allow_writes,webSource=state.webSource,resources=state.resourceReport,resourceLoading=state.resourceLoading,resourceProgress=state.resourceProgress)
                    return self.reply(200,result)
                if path.startswith('/flprog-webui/') and state.resourceLoading:
                    raise BridgeError('Загружаются ресурсы веба из Flash ПЛК',503)
                if path.startswith('/flprog-webui/') and state.project:
                    c=state.active();params={k:v[0] for k,v in parse_qs(urlsplit(self.path).query,keep_blank_values=True).items()}
                    if path=='/flprog-webui/item':return self.reply(200,state.project.item(params))
                    if path=='/flprog-webui/state':
                        data=state.project.snapshot(c,params);data['webHash']=state.manifest['projectHash'];return self.reply(200,data)
                    raise BridgeError('Этот API пока не поддерживается COM-мостом',501)
                match=re.fullmatch('/api/v1/channels/([0-9]{1,3})(/meta)?',path)
                if match:
                    number=int(match[1])
                    if number>255:raise ValueError('Номер канала: 0..255')
                    c=state.active();data=c.request(1,2 if match[2] else 1,bytes([number]))
                    if match[2]:
                        if len(data)<3 or data[1]>3 or data[2]>2:raise BridgeError('Неверное описание канала',502)
                        return self.reply(200,dict(number=data[0],type=['bool','int32','float','text'][data[1]],direction=['publish','command','duplex'][data[2]],id=data[3:].decode('utf-8'),session=str(c.session)))
                    return self.reply(200,dict(number=number,value=decode_value(data),session=str(c.session)))
                if path.startswith('/api/'):return self.reply(404,dict(error='Неизвестный API'))
                if path=='/' and state.resourceLoading:
                    return self.reply(200,'''<!doctype html><meta charset="utf-8"><title>FLProg Bridge</title><h2 id="s">Загрузка веба из Flash ПЛК…</h2><script>async function p(){try{let d=await(await fetch('/api/v1/status')).json();let r=d.resourceProgress;document.querySelector('#s').textContent=r?'Веб из Flash ПЛК: '+Math.floor(r.received*100/r.total)+'%':'Подключение…';if(d.online&&!d.resourceLoading&&d.webSource!=='generic'){location.reload();return}}catch(e){}setTimeout(p,250)}p()</script>'''.encode('utf-8'),'text/html; charset=utf-8')
                if path=='/bridge' or (path=='/' and not state.site):
                    page=Path(__file__).resolve().parent/'public/index.html'
                    return self.reply(200,page.read_bytes(),'text/html; charset=utf-8')
                if state.site:
                    state.active()
                    if path=='/' and state.webSource=='device' and parse_qs(urlsplit(self.path).query).get('web',[''])[0]!=state.manifest['projectHash']:
                        self.send_response(302);self.send_header('Location','/?web='+state.manifest['projectHash']);self.send_header('Content-Length','0');self.send_header('Cache-Control','no-store');self.end_headers();return
                    name=state.manifest.get('entry','index.html') if path=='/' else unquote(path).lstrip('/')
                    if state.project:
                        if name not in state.resources:raise BridgeError('Ресурс не включён в паспорт сайта',404)
                        return self.reply(200,state.resources[name],mimetypes.guess_type(name)[0] or 'application/octet-stream')
                    target=state.file(name)
                    return self.reply(200,target.read_bytes(),mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
                return self.reply(404,dict(error='Файл не найден'))
            except BridgeError as e:self.reply(e.status,dict(error=str(e)))
            except (ValueError,UnicodeError,OSError) as e:self.reply(400,dict(error=str(e)))
        def do_POST(self):
            try:
                self.check_host()
                if self.headers.get('X-FLProg-Bridge')!='1':raise BridgeError('Требуется заголовок X-FLProg-Bridge: 1',403)
                if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise BridgeError('Требуется application/json',415)
                length=int(self.headers.get('Content-Length','0'))
                if not 1<=length<=1024:raise BridgeError('Запрос должен занимать 1..1024 байт',413)
                if urlsplit(self.path).path=='/flprog-webui/write' and state.project:
                    if not state.allow_writes:raise BridgeError('Запись отключена в программе моста',403)
                    session=self.headers.get('X-FLProg-Session','')
                    if not session.isdigit():raise BridgeError('Сначала прочитайте свежие данные ПЛК',409)
                    self.rfile.read(length)
                    params={k:v[0] for k,v in parse_qs(urlsplit(self.path).query,keep_blank_values=True).items()}
                    return self.reply(202,state.project.write(state.active(),params,int(session)))
                match=re.fullmatch('/api/v1/channels/([0-9]{1,3})',self.path)
                if not match:raise BridgeError('Неизвестный API',404)
                if not state.allow_writes:raise BridgeError('Запись отключена в программе моста',403)
                number=int(match[1])
                if not 101<=number<=255:raise BridgeError('Системные каналы защищены от записи',403)
                body=json.loads(self.rfile.read(length).decode('utf-8'))
                if not isinstance(body,dict):raise ValueError('Требуется JSON-объект')
                session=body.get('session')
                if not isinstance(session,str) or not session.isdigit():raise ValueError('Требуется сеанс из свежего чтения')
                payload=encode_value(body.get('type'),body.get('value'));c=state.active()
                c.request(1,3,bytes([number])+payload,expected_session=int(session))
                return self.reply(200,dict(accepted=True,confirmed=False,session=str(c.session),message='Принято в очередь ПЛК. Выполнение проверяйте по данным и busy/result.'))
            except BridgeError as e:self.reply(e.status,dict(error=str(e)))
            except (ValueError,UnicodeError,OSError) as e:self.reply(400,dict(error=str(e)))
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)
