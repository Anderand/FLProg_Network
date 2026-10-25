"""Offline preview using the actual controller's embedded browser resources."""
import ast
import copy
import json
import re
from check_http_assets import embedded_assets
from project_validation import validate_project


def preview_html(document, root):
    report = validate_project(document)
    if not report['valid']:
        raise ValueError('Исправьте ошибки проекта перед предпросмотром')
    document = copy.deepcopy(document)
    assets, _ = embedded_assets(root/'runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h')
    order = ast.literal_eval(re.search(r'let p=(\[[^\]]+\])', assets['/']['body']).group(1))
    def script(text):
        return '<script>'+text.replace('</script', '<\\/script')+'</script>'
    boot = 'const previewDocument='+json.dumps(document, ensure_ascii=False)+';\n'
    public = root/'public' if (root/'public').is_dir() else root/'editor/public'
    boot += (public/'preview-simulator.js').read_text(encoding='utf-8')
    html = '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    html += '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src data:; connect-src \'none\'; form-action \'none\'">'
    html += '<style>'+assets['/flprog-webui/app.css']['body']+'</style>'
    html += '<main><nav id="n"></nav><div id="s">Загрузка предпросмотра…</div></main><div id="m" hidden></div>'
    html += script(boot)
    for path in order:
        html += script(assets['/flprog-webui/'+path]['body'])
    return html
