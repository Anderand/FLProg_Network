"""Syntax and command tests from actual embedded assets; requires Node.js."""
import json
import subprocess
import tempfile
from pathlib import Path
from check_http_assets import ROOT, embedded_assets

assets, _ = embedded_assets(ROOT / "runtime/FLProg_WebUI/src/adapters/FLProgWebUiFlprogNetworkPagedHttp.h")
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "assets.json"
    path.write_text(json.dumps(assets), encoding="utf-8")
    subprocess.run(["node", str(Path(__file__).with_suffix(".js")), str(path)], check=True)
