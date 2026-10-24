"""Check actual embedded HTTP resources against FLProg_Network's queue budget."""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def embedded_assets(adapter):
    text = Path(adapter).read_text(encoding="utf-8")
    handlers = dict((callback, path) for path, callback in re.findall(
        r'server\.addHandler\("([^"]+)",\s*(\w+),', text))
    pattern = (r'static void FLPROG_WEBUI_HTTP_FLASH (\w+)'
               r'\(FLProgNetworkHttpServer \*value\)\s*\{\s*'
               r'static const char asset\[\] PROGMEM =\s*'
               r'((?:"(?:\\.|[^"\\])*"\s*)+);'
               r'(.*?)value->sendProgmem\(200, "([^"]+)", asset\);')
    assets = {}
    for match in re.finditer(pattern, text, re.S):
        callback, strings, guard, content_type = match.groups()
        body = "".join(ast.literal_eval(s) for s in re.findall(r'"(?:\\.|[^"\\])*"', strings))
        assets[handlers[callback]] = {"body": body, "type": content_type,
                                     "compile_guard": "static_assert" in guard}
    if not assets:
        raise AssertionError("No embedded resources found")
    return assets, handlers


def response_bytes(asset):
    size = len(asset["body"].encode("utf-8"))
    header = ("HTTP/1.1 200 OK\r\nContent-Type: " + asset["type"]
              + "\r\nContent-Length: " + str(size) + "\r\nConnection: close\r\n\r\n")
    return len(header.encode("ascii")) + size


def check():
    adapter = ROOT / "runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h"
    assets, handlers = embedded_assets(adapter)
    assert len(handlers) <= 14, "Too many HTTP handlers"
    limits = ROOT.parents[1] / "Библиотека/FLProg_Network/src/service/flprogNetworkHttpServer.h"
    limit = 2048
    if limits.is_file():
        match = re.search(r'#define FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES\s+(\d+)U?', limits.read_text(encoding="utf-8"))
        assert match, "HTTP response limit not found"
        limit = int(match.group(1))
    for path, asset in assets.items():
        assert response_bytes(asset) <= limit, (path, response_bytes(asset), limit)
        assert len(asset["body"].encode("utf-8")) + 128 <= limit, path
        assert asset["compile_guard"], "Missing compile-time bound: " + path
    order = ast.literal_eval(re.search(r"let p=(\[[^\]]+\])", assets["/"]["body"]).group(1))
    for path in order:
        assert "/flprog-webui/" + path in assets, "Loader references missing asset: " + path
    assert order[-1] == "boot.js"
    assert "setTimeout(B," not in assets["/flprog-webui/boot-init.js"]["body"]
    return {"limit": limit, "handlers": len(handlers),
            "responses": {path: response_bytes(asset) for path, asset in assets.items()}}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2, ensure_ascii=False))
