#!/usr/bin/env python3
"""Local editor for FLProg Web UI 1.0. No dependency on FLProg_Network."""
import json
import os
import re
import sys
import shutil
import importlib
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

def copy_tree(source, target, overwrite=True):
    """Merge directories on Python 3.7 without deleting user files."""
    source, target = Path(source), Path(target)
    target.mkdir(parents=True, exist_ok=True)
    for entry in source.iterdir():
        destination = target / entry.name
        if entry.is_dir():
            copy_tree(entry, destination, overwrite)
        elif overwrite or not destination.exists():
            shutil.copy2(str(entry), str(destination))

# In a source checkout resources live alongside this file.  In the portable
# EXE resources live under PyInstaller's internal directory, while documents
# and generated packages must remain next to the EXE and be writable.
if getattr(sys, "frozen", False):
    ROOT = Path(sys._MEIPASS).resolve()
    DATA_ROOT = Path(sys.executable).resolve().parent
    for folder in ("projects", "project_packages"):
        bundled = ROOT / folder
        target = DATA_ROOT / folder
        if bundled.is_dir():
            copy_tree(bundled, target, overwrite=False)
else:
    ROOT = Path(__file__).resolve().parent
    DATA_ROOT = ROOT if (ROOT / "tools").is_dir() else ROOT.parent

PROJECTS = DATA_ROOT / "projects"
DEFAULT_PACKAGES = DATA_ROOT / "project_packages"
RESOURCE_ROOT = ROOT if (ROOT / "tools").is_dir() else ROOT.parent
NETWORK_CATALOG = RESOURCE_ROOT / "integration" / "flprog_network_api_catalog.json"
FLPROG_LIBRARIES = Path(r"C:\F-981\FLProg\ideV8\portable\sketchbook\libraries")
FLPROG_LIBRARIES = Path(os.environ.get("FLPROG_LIBRARIES", str(FLPROG_LIBRARIES)))
sys.path.insert(0, str(RESOURCE_ROOT / "tools"))
import build_project_package


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Windowed portable builds have no stderr stream.
        if sys.stderr is not None:
            super().log_message(format, *args)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "public"), **kwargs)

    def reply(self, status, value):
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/api/demo":
            # Keep the editor's smoke test identical to the package currently
            # installed under the stable demo_controller identifier.  This lets
            # an existing FBD project test the transport without any block or
            # channel migration.
            # A smoke project is optional in a distribution.  The full demo is
            # the reliable fallback, so a missing development-only file must
            # never prevent the editor from opening or loading Demo.
            demo = PROJECTS / "demo_controller_smoke.flpui"
            if not demo.is_file():
                demo = PROJECTS / "demo_controller.flpui"
            if not demo.is_file():
                demo = PROJECTS / "demo.flpui"
            return self.reply(200, json.loads(demo.read_text(encoding="utf-8")))
        if self.path == "/api/network-api":
            catalog = json.loads(NETWORK_CATALOG.read_text(encoding="utf-8"))
            return self.reply(200, catalog)
        return super().do_GET()

    def do_POST(self):
        if self.path not in ("/api/save", "/api/build"): return self.reply(404, {"error":"unknown API"})
        try:
            raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            data = json.loads(raw.decode("utf-8"))
            if data.get("schema") != "flprog.webui/1.0": raise ValueError("Неверная схема проекта")
            project_id = str(data.get("project", {}).get("id", "")).strip()
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{1,63}", project_id):
                raise ValueError("ID проекта: 2–64 латинских буквы, цифры, _ или -, начиная с буквы")
            # Validate before replacing an existing user project file.
            build_project_package.validate(data)
            PROJECTS.mkdir(parents=True, exist_ok=True)
            if self.path == "/api/build":
                output = Path(str(data.get("packageOutput") or DEFAULT_PACKAGES)).resolve()
                normalized = str(output).replace("/", "\\").lower()
                if "\\libraries\\flprog_network" in normalized:
                    raise ValueError("Пакет проекта нельзя размещать в FLProg_Network")
                PROJECTS.mkdir(exist_ok=True)
                source = PROJECTS / (project_id + ".flpui")
                source.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                # Reload the project generator for every build. The editor is
                # intentionally long-running, while generator/runtime updates
                # are installed during development; retaining an old imported
                # function here silently produced obsolete project packages.
                package = importlib.reload(build_project_package).build(source, output)
                installed = None
                if FLPROG_LIBRARIES.is_dir():
                    installed = FLPROG_LIBRARIES / package.name
                    copy_tree(package, installed)
                return self.reply(200, {"ok":True, "project":str(source), "package":str(package), "installed":str(installed) if installed else None, "generator":"paged-pages", "generatorFile":str(build_project_package.__file__)})
            path = PROJECTS / (project_id + ".flpui")
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return self.reply(200, {"ok":True, "file":str(path)})
        except (ValueError, OSError, json.JSONDecodeError) as error:
            return self.reply(400, {"ok":False, "error":str(error)})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    print("FLProg Web UI Editor 1.0: http://127.0.0.1:%d" % port)
    # The portable Windows editor is launched by double click.  Open the
    # browser only after the listener has had time to bind its local port.
    if getattr(sys, "frozen", False) and '--no-browser' not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:%d/" % port)).start()
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
