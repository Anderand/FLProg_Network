# coding: utf-8
"""Export the existing controller renderer as a standalone Bridge website."""
import ast
import copy
import hashlib
import gzip
import html
import json
import re
import shutil
from pathlib import Path
from check_http_assets import embedded_assets,page_styles
from project_validation import validate_project


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')


def attach_bridge_header(library,result):
    library=Path(library)
    manifest_path=library/'WEBUI_COMPATIBILITY.json'
    passport=json.loads(manifest_path.read_text(encoding='utf-8'))
    header=library/'src'/(passport['projectId']+'_bridge.h')
    shutil.copy2(result['identityHeader'],header)
    passport['bridgeApi']=1
    passport['bridgeHash']=re.search(r'FLPROG_BRIDGE_WEB_HASH "([0-9a-f]{64})"',header.read_text(encoding='utf-8')).group(1)
    if 'FLPROG_BRIDGE_WEB_PACKAGE_SIZE' in header.read_text(encoding='utf-8'):
        passport['bridgeResourceApi']=1
    passport['files'][header.relative_to(library).as_posix()]=hashlib.sha256(header.read_bytes()).hexdigest()
    project_id=passport['projectId']
    safe=re.sub(r'[^A-Za-z0-9_]','_',project_id)
    entry=library/'src'/(project_id+'_bridge_entry.h')
    entry.write_text('''// Generated automatic Bridge project binding.\n#pragma once
#ifdef FLPROG_BRIDGE_SELECTED_PROJECT
#error "Bridge: only one project may be selected"
#endif
#define FLPROG_BRIDGE_SELECTED_PROJECT '''+json.dumps(project_id)+'''
#define FLPROG_BRIDGE_AUTO_PROJECT 1
#ifndef FLPROG_WEBUI_NO_HTTP_CATALOG
#define FLPROG_WEBUI_NO_HTTP_CATALOG 1
#define FLPROG_BRIDGE_RESTORE_HTTP_CATALOG 1
#endif
#include "'''+safe+'''_descriptor.h"
#ifdef FLPROG_BRIDGE_RESTORE_HTTP_CATALOG
#undef FLPROG_WEBUI_NO_HTTP_CATALOG
#undef FLPROG_BRIDGE_RESTORE_HTTP_CATALOG
#endif
#include "'''+project_id+'''_bridge.h"
#include <FLProgBridgeProjectBinding.h>
namespace flprog_bridge_'''+safe+''' {
inline flprog_bridge::ProjectBinding& binding(){
    static flprog_bridge::ProjectBinding instance(flprog_webui_'''+safe+'''::model,
        flprog_webui_'''+safe+'''::theme,FLPROG_BRIDGE_SELECTED_PROJECT,FLPROG_BRIDGE_WEB_HASH,
        FLPROG_BRIDGE_WEB_PACKAGE,FLPROG_BRIDGE_WEB_PACKAGE_SIZE,
        FLPROG_BRIDGE_WEB_PACKAGE_PLAIN_SIZE,FLPROG_BRIDGE_WEB_PACKAGE_SHA256);
    return instance;
}
}
namespace flprog_bridge_selected = flprog_bridge_'''+safe+''';
''',encoding='utf-8')
    wrapper=library/'src'/(project_id+'_webui.h')
    include='#include "'+entry.name+'"'
    text=wrapper.read_text(encoding='utf-8')
    if include not in text:wrapper.write_text(text+'\n// Bridge resources exported for this exact project.\n'+include+'\n',encoding='utf-8')
    for path in (entry,wrapper):passport['files'][path.relative_to(library).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    passport['bridgeBlockApi']=1
    block_dir=Path(result.get('blockDirectory',''))
    if result.get('blockDirectory') and block_dir.is_dir():
        shutil.copytree(block_dir,library/'Bridge_UART',dirs_exist_ok=True)
    manifest_path.write_text(json.dumps(passport,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return dict(result,siteIdentityHeader=result['identityHeader'],identityHeader=str(header),include='#include <'+passport['projectId']+'_bridge.h>')


def export_bridge(document,root,output):
    report=validate_project(document)
    if not report['valid']:raise ValueError('Исправьте ошибки проекта перед экспортом')
    root=Path(root);output=Path(output);doc=copy.deepcopy(document)
    existing=output/'bridge.json'
    if existing.is_file() and json.loads(existing.read_text(encoding='utf-8')).get('projectId')!=doc['project']['id']:
        raise ValueError('Папка экспорта занята другим проектом')
    # Paths and IDE settings are local editor preferences, not the UI contract.
    doc={key:doc[key] for key in ('schema','project','channels','pages','theme','polling') if key in doc}
    assets,_=embedded_assets(root/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
    order=ast.literal_eval(re.search(r'let p=(\[[^\]]+\])',assets['/flprog-webui/controls.js?part=loader']['body']).group(1))
    bootstrap='''const bridgeFetch=window.fetch.bind(window);let bridgeCommandSession='',bridgePageHash=new URL(location.href).searchParams.get('web');
function bridgeSessionChanged(d){if(bridgePageHash&&d.webHash&&bridgePageHash!==d.webHash){location.reload();throw Error('Обновлён веб-проект ПЛК')}const changed=!!bridgeCommandSession&&bridgeCommandSession!==d.session;bridgeCommandSession=d.session;return changed}
window.fetch=function(input,options={}){const u=new URL(String(input),location.href);if(u.origin!==location.origin)throw Error('Внешний адрес не поддерживается');if(u.pathname==='/flprog-webui/write'){if(!bridgeCommandSession)throw Error('Сначала дождитесь синхронизации с ПЛК');options={...options,headers:{...options.headers,'X-FLProg-Bridge':'1','X-FLProg-Session':bridgeCommandSession,'Content-Type':'application/json'},body:'{}'}}return bridgeFetch(input,options)};
'''
    def script(body):return '<script>'+body.replace('</script','<\\/script')+'</script>'
    page='<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    page+='<title>'+html.escape(doc['project'].get('title',doc['project']['id']))+' — COM</title>'
    page+='<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src data: \'self\'; connect-src \'self\'; form-action \'none\'; base-uri \'none\'">'
    page+='<style>'+page_styles(assets)+'</style>'
    page+='<main><nav id="n"></nav><div id="s">Подключение к ПЛК через COM…</div></main><div id="m" hidden></div>'
    page+=script(bootstrap)
    for name in order:
        body=assets['/flprog-webui/'+name]['body']
        if name=='boot.js':
            needle='let reset=d.revision<rv||'
            if needle not in body:raise ValueError('Изменён контракт renderer boot.js: обновите экспорт моста')
            body=body.replace(needle,"let reset=bridgeSessionChanged(d)||d.revision<rv||",1)
        page+=script(body)
    page+='</html>'
    files={'index.html':page.encode('utf-8'),'project.json':canonical(doc)}
    digests={name:hashlib.sha256(data).hexdigest() for name,data in files.items()}
    project_hash=hashlib.sha256(canonical(dict(api='flprog.bridge.web/1',files=digests))).hexdigest()
    manifest=dict(api='flprog.bridge/1',webApi=1,projectId=doc['project']['id'],projectHash=project_hash,
                  renderer='flprog.webui/1',entry='index.html',project='project.json',files=digests)
    output.mkdir(parents=True,exist_ok=True)
    for name,data in files.items():(output/name).write_bytes(data)
    (output/'bridge.json').write_bytes(canonical(manifest))
    firmware=output/'firmware';firmware.mkdir(exist_ok=True)
    header=firmware/'FLProgBridgeProject.h'
    package=canonical(dict(manifest=manifest,files={key:value.decode('utf-8') for key,value in files.items()}))
    compressed=gzip.compress(package,compresslevel=9,mtime=0)
    digest=hashlib.sha256(compressed).digest()
    def array(name,value):
        return 'static const uint8_t '+name+'[] FLPROG_BRIDGE_FLASH_DATA = {\n'+''.join('  '+','.join('0x%02x'%v for v in value[i:i+24])+',\n' for i in range(0,len(value),24))+'};\n'
    source='// Generated from the exact Bridge website. Rebuild PLC after layout changes.\n#pragma once\n#include <stdint.h>\n'
    source+='#define FLPROG_BRIDGE_WEB_API 1\n#define FLPROG_BRIDGE_WEB_HASH "'+project_hash+'"\n'
    source+='#ifdef PROGMEM\n#define FLPROG_BRIDGE_FLASH_DATA PROGMEM\n#else\n#define FLPROG_BRIDGE_FLASH_DATA\n#endif\n'
    source+=array('FLPROG_BRIDGE_WEB_PACKAGE',compressed)+array('FLPROG_BRIDGE_WEB_PACKAGE_SHA256',digest)
    source+='static const uint32_t FLPROG_BRIDGE_WEB_PACKAGE_SIZE='+str(len(compressed))+'U;\nstatic const uint32_t FLPROG_BRIDGE_WEB_PACKAGE_PLAIN_SIZE='+str(len(package))+'U;\n#undef FLPROG_BRIDGE_FLASH_DATA\n'
    header.write_text(source,encoding='utf-8')
    (output/'README_RU.md').write_text('# Веб-проект для COM-моста\n\nДля прежней прошивки откройте эту папку в FLProg Bridge0.2.0 или новее.\nДля загрузки веба изFlash используйте Bridge0.3.0 и FLProgBridgeResources: сжатый пакет находится в firmware/FLProgBridgeProject.h.\nВ проектной библиотеке это <ID>_bridge.h. Объявите webHash/webApi в HELLO и зарегистрируйте службу ресурсов4.\nПосле изменения макета/каналов пересоберите прошивку. Заголовок не размещается в IDE автоматически.\n',encoding='utf-8')
    return dict(site=str(output),manifest=str(output/'bridge.json'),identityHeader=str(header),projectHash=project_hash,compressedBytes=len(compressed),plainBytes=len(package),firmwareRebuildRequired=True,blockDirectory=str(root/'runtime/FLProg_WebUI/user_blocks/Bridge_UART'))
