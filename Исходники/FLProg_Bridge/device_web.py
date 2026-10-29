# coding: utf-8
"""Read a bounded gzip resource package from PLC Flash; cache only verified data."""
import hashlib,json,os,struct,tempfile,zlib
from pathlib import Path
from client import BridgeError
from protocol import WEB_RESOURCES

RESOURCE_SERVICE=WEB_RESOURCES
MAX_COMPRESSED=2*1024*1024
MAX_PLAIN=8*1024*1024

def cache_root():
    return Path(os.environ.get('LOCALAPPDATA',tempfile.gettempdir()))/'FLProgNetwork/Bridge/cache'

def device_site(client,progress=lambda done,total:None,cache=None):
    # Lazy import keeps State independent of this optional transport helper.
    from http_api import State
    if RESOURCE_SERVICE not in client.info['services']:raise BridgeError('В прошивке нет службы веб-ресурсов',501)
    session=client.session;identity=dict(client.info.get('identity',{}))
    meta=client.request(RESOURCE_SERVICE,1,b'',session)
    if len(meta)!=44:raise BridgeError('Неверный паспорт ресурсов',502)
    version,encoding,chunk,size,plain=struct.unpack('<BBHII',meta[:12]);digest=meta[12:]
    if version!=1 or encoding!=1 or not 1<=chunk<=224 or not 1<=size<=MAX_COMPRESSED or not 1<=plain<=MAX_PLAIN:
        raise BridgeError('Неподдерживаемый формат или размер ресурсов',502)
    root=Path(cache) if cache else cache_root();root.mkdir(parents=True,exist_ok=True)
    target=root/digest.hex()
    def verify(folder):
        value=State(folder);value.client=client;value.active()
        if value.manifest.get('projectHash')!=identity.get('webHash'):raise BridgeError('Ресурсы принадлежат другой прошивке',409)
        return value
    if target.is_dir():
        try:
            verify(target);progress(size,size);return target,dict(cacheHit=True,bytes=size,sha256=digest.hex())
        except (OSError,ValueError,BridgeError):pass
    received=bytearray();progress(0,size)
    while len(received)<size:
        offset=len(received);count=min(chunk,size-offset)
        response=client.request(RESOURCE_SERVICE,2,struct.pack('<IH',offset,count),session)
        if len(response)!=count+4 or struct.unpack('<I',response[:4])[0]!=offset:
            raise BridgeError('Неверное смещение или длина порции ресурсов',502)
        received.extend(response[4:]);progress(len(received),size)
    if hashlib.sha256(received).digest()!=digest:raise BridgeError('SHA-256 ресурсов не совпал',502)
    try:
        decoder=zlib.decompressobj(31);data=decoder.decompress(bytes(received),plain+1)
        if len(data)!=plain or not decoder.eof or decoder.unconsumed_tail or decoder.unused_data:raise ValueError('Размер распаковки')
        package=json.loads(data.decode('utf-8'))
        if not isinstance(package,dict):raise ValueError('Тип пакета')
        manifest=package['manifest'];files=package['files']
        if not isinstance(manifest,dict) or not isinstance(files,dict):raise ValueError('Структура пакета')
        if set(files)!={'index.html','project.json'} or set(manifest['files'])!=set(files):raise ValueError('Состав ресурсов')
        if any(not isinstance(content,str) for content in files.values()):raise ValueError('Тип ресурса')
        if manifest.get('projectId')!=identity.get('projectId') or manifest.get('projectHash')!=identity.get('webHash'):
            raise ValueError('Проект ресурсов не совпал с HELLO')
    except (ValueError,KeyError,TypeError,UnicodeError,zlib.error) as error:raise BridgeError('Повреждён пакет веб-ресурсов: '+str(error),502) from error
    # No ZIP extraction or paths supplied by the device. Never overwrite an old cache.
    folder=Path(tempfile.mkdtemp(prefix='verified-',dir=str(root)))
    for name,content in files.items():(folder/name).write_bytes(content.encode('utf-8'))
    (folder/'bridge.json').write_text(json.dumps(manifest,ensure_ascii=False),encoding='utf-8')
    try:verify(folder)
    except (OSError,ValueError,BridgeError) as error:raise BridgeError('Проверка веб-пакета не пройдена: '+str(error),502) from error
    if not target.exists():
        try:folder.rename(target);folder=target
        except FileExistsError:pass
    return folder,dict(cacheHit=False,bytes=size,sha256=digest.hex())

def synchronize(state,client,progress=lambda done,total:None,cache=None):
    if RESOURCE_SERVICE not in client.info['services']:
        if state.webSource=='device':
            from http_api import State
            fallback=State(state.fallbackSite,state.allow_writes)
            state.resources=fallback.resources;state.project=fallback.project;state.site=fallback.site
            state.webSource=fallback.webSource;state.resourceReport=None;state.manifest=fallback.manifest
        return None
    state.resourceLoading=True
    def notify(done,total):state.resourceProgress=dict(received=done,total=total);progress(done,total)
    try:
        folder,report=device_site(client,notify,cache)
        from http_api import State
        verified=State(folder,state.allow_writes);verified.client=client;verified.active()
        # The new manifest activates the new project last. Old hashes fail active().
        state.resources=verified.resources;state.project=verified.project;state.site=folder
        state.webSource='device';state.resourceReport=report;state.manifest=verified.manifest
        return report
    finally:state.resourceLoading=False
