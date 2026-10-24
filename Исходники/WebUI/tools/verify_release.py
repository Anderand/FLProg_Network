#!/usr/bin/env python3
"""Repeatable static verification for the FLProg Web UI handoff."""
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "tools"))
from build_project_package import build, validate


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    catalog = json.loads((ROOT / "integration" / "flprog_network_api_catalog.json").read_text(encoding="utf-8"))
    transport_ids = {entry["id"] for entry in catalog["transports"]}
    require({"wifi-http", "w5500-http-1", "w5500-http-2"} <= transport_ids, "transport catalog incomplete")
    for project in ((ROOT / "projects" / "demo.flpui"), (ROOT / "projects" / "demo_w5500.flpui")):
        with tempfile.TemporaryDirectory() as directory:
            package = build(project, Path(directory))
            require((package / "library.properties").is_file(), f"missing metadata: {project.name}")
            require("paragraph=" in (package / "library.properties").read_text(encoding="utf-8"), f"metadata paragraph missing: {project.name}")
            ubi = next(package.glob("*.ubi"))
            raw = ubi.read_bytes()
            require(raw[:2] == b"\xff\xfe", f"UBI is not UTF-16LE: {project.name}")
            descriptor = next((package / "src").glob("*_descriptor.h")).read_text(encoding="utf-8")
            require("configure(model, theme)" in descriptor, f"theme compatibility missing: {project.name}")
    # A large layout is valid: the runtime serves every descriptor separately.
    many_widgets = {
        "schema": "flprog.webui/1.0", "project": {"id": "paged_layout"},
        "channels": [{"id": "value", "type": "float", "direction": "duplex"}],
        "pages": [{"id": "main", "widgets": [{"id": "w" + str(i), "type": "slider", "channel": "value", "label": "Value " + str(i), "x": 1, "y": i + 1, "w": 4, "h": 1} for i in range(40)]}],
    }
    validate(many_widgets)
    too_large = {
        "schema": "flprog.webui/1.0", "project": {"id": "overflow"},
        "channels": [{"id": "value", "type": "float", "direction": "duplex"}],
        "pages": [{"id": "main", "widgets": [{"id": "w", "type": "slider", "channel": "value", "label": "x" * 300, "x": 1, "y": 1, "w": 4, "h": 1}]}],
    }
    try:
        validate(too_large)
        raise AssertionError("oversized project was accepted")
    except ValueError as error:
        require("Слишком" in str(error), "wrong oversized-project error")
    blocks = ROOT / "runtime" / "FLProg_WebUI" / "user_blocks" / "FLProg_WebUI_Universal_Blocks.ubl"
    root = ET.parse(blocks).getroot()
    require(root.attrib.get("{sixx}type", "") or root.tag.endswith("object"), "UBL root invalid")
    adapter = (ROOT / "runtime" / "FLProg_WebUI" / "src" / "adapters" / "FLProgWebUiFlprogNetworkPagedHttp.h").read_text(encoding="utf-8")
    require('"/flprog-webui/app.css"' in adapter and '"/flprog-webui/item"' in adapter and '"/flprog-webui/controls.js"' in adapter, "paged device resources absent")
    require("FLPROG_NETWORK_ROUTE_WIFI_AP" in adapter and "startWifiScan" in adapter, "SoftAP or Wi-Fi scan integration absent")
    require(all(kind in adapter for kind in ("chart", "radial-gauge", "battery", "segment-display", "traffic-light")), "alternative embedded widgets absent")
    runtime = (ROOT / "runtime" / "FLProg_WebUI" / "src" / "FLProgWebUi.h").read_text(encoding="utf-8")
    require('FLPROG_WEBUI_RUNTIME_VERSION' in runtime, "runtime version absent")
    require("FLPROG_WEBUI_TEXT_BYTES 64U" in runtime, "WPA2-length text slot absent")
    require("const char *options;" in runtime and '"select"' in (ROOT / "tools" / "build_project_package.py").read_text(encoding="utf-8"), "extended widget contract absent")
    demo = json.loads((ROOT / "projects" / "demo.flpui").read_text(encoding="utf-8"))
    demo_types = {item.get("type") for page in demo["pages"] for item in page.get("widgets", [])}
    require({"chart", "radial-gauge", "battery", "segment-display", "traffic-light"} <= demo_types, "alternative widget demo absent")
    for filename in ("README_RU.md", "README_EN.md", "ROADMAP_RU.md", "ROADMAP_EN.md", "REGRESSION_RU.md", "REGRESSION_EN.md"):
        require((ROOT / filename).is_file(), f"missing handoff document: {filename}")
    print("FLProg Web UI static release verification: OK")


if __name__ == "__main__":
    main()
