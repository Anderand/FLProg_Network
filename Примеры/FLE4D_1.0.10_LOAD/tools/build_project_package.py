#!/usr/bin/env python3
"""Build an isolated Arduino library package from a FLProg Web UI 1.0 project.

The caller must explicitly supply the destination directory.  This tool never
writes into FLProg_Network and never modifies the original .flpui document.
"""
import argparse
import json
import re
import math
from pathlib import Path
from typing import Dict, List, Tuple

TYPES = {"bool": "FLPROG_WEBUI_BOOL", "int32": "FLPROG_WEBUI_INT32",
         "float": "FLPROG_WEBUI_FLOAT", "text": "FLPROG_WEBUI_TEXT"}
DIRECTIONS = {"publish": "FLPROG_WEBUI_PUBLISH", "command": "FLPROG_WEBUI_COMMAND",
              "duplex": "FLPROG_WEBUI_DUPLEX"}
WIDGET_TYPES = {
    "indicator", "switch", "checkbox", "slider", "number-input",
    "gauge", "progress", "chart", "radial-gauge", "sector-gauge", "bar-meter", "battery", "segment-display",
    "traffic-light", "heading", "static-text", "divider", "link", "status-row", "text", "text-input", "password-input",
    "color-input", "date-input", "time-input", "select", "weekdays",
    "button", "wifi-scan",
}
# Per-response envelope used by the paged Web UI transport.  There is no
# aggregate dashboard limit: metadata, every widget and every live channel
# are returned as separate bounded HTTP responses.
HTTP_ITEM_BYTES = 900


def safe_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not result or result[0].isdigit():
        result = "project_" + result
    return result


def c_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _widget_config(item: Dict, labels: Dict[str, str]) -> Dict:
    channel = str(item.get("channel", ""))
    return {
        "id": str(item.get("id", "")),
        "group": str(item.get("group", "")),
        "placeholder": str(item.get("placeholder", "")),
        "unit": str(item.get("unit", "")),
        "maxLength": int(item.get("maxLength", 63)),
        "confirmation": str(item.get("confirmation", "Отправить команду?" if item.get("type") == "button" else "")),
        "type": str(item.get("type", "")),
        "label": str(item.get("label") or labels.get(channel, channel)),
        "channel": channel,
        "icon": str(item.get("icon", "")),
        "color": str(item.get("color", "")),
        "options": str(item.get("options", "")),
        "code": str(item.get("code", "")),
        "bindings": item.get("bindings", []),
        "min": float(item.get("min", 0)),
        "max": float(item.get("max", 100)),
        "step": float(item.get("step", 1)),
        "x": max(1, min(12, int(item.get("x", 1)))),
        "y": max(1, min(99, int(item.get("y", 1)))),
        "w": max(1, min(12, int(item.get("w", 4)))),
        "h": max(1, min(12, int(item.get("h", 2)))),
    }


def estimate_http_buffers(document: Dict, channels: List[Dict]) -> Tuple[int, int]:
    """Conservative byte estimates for bounded device JSON responses."""
    labels = {str(item["id"]): str(item.get("label") or item["id"]) for item in channels}
    widgets = [_widget_config(item, labels) for page in document.get("pages", []) for item in page.get("widgets", [])]
    theme = {key: str(document.get("theme", {}).get(key, "")) for key in ("background", "card", "text", "accent")}
    # The C++ runtime prints three decimal places, which can be up to six bytes
    # longer than Python's compact float representation across one widget.
    config = json.dumps({"theme": theme, "widgets": widgets}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    config_bytes = len(config) + len(widgets) * 6 + 32
    state_bytes = len('{"schema":"flprog.webui/1.0","channels":{}}'.encode("utf-8"))
    for item in channels:
        state_bytes += len(json.dumps(str(item["id"]), ensure_ascii=False).encode("utf-8")) + 1
        # Text occupies up to 63 bytes internally (for WPA2 credentials) and
        # can expand to six JSON bytes per source byte in a JSON response.
        value_bytes = 378 if item["type"] == "text" else 48
        state_bytes += value_bytes + 1
    return config_bytes, state_bytes


def _validate_legacy(document: Dict) -> Tuple[str, List[Dict]]:
    if document.get("schema") != "flprog.webui/1.0":
        raise ValueError("Ожидается schema: flprog.webui/1.0")
    project_id = str(document.get("project", {}).get("id", "")).strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{1,63}", project_id):
        raise ValueError("project.id: латинские буквы/цифры/_/-, 2…64 символов")
    channels = document.get("channels")
    if not isinstance(channels, list) or not channels:
        raise ValueError("Нужен непустой список channels")
    if len(channels) > 255:
        raise ValueError("Максимум 255 каналов в одном проекте Web UI")
    # Physical descriptor order is compact, but FBD keeps a stable logical
    # address space: public FLProg_Network API at 0…100, user channels at
    # 101+.  This avoids wasting 101 RAM slots on ESP8266 just to reserve the
    # visible range in the editor.
    api_channels = [item for item in channels if item.get("source") and item.get("source") != "user"]
    user_channels = [item for item in channels if item not in api_channels]
    if len(api_channels) > 101:
        raise ValueError("В диапазоне API FLProg_Network доступно максимум 101 канал (№0…100)")
    if len(user_channels) > 155:
        raise ValueError("В диапазоне пользовательских каналов доступно максимум 155 каналов (№101…255)")
    for group, first, last in ((api_channels, 0, 100), (user_channels, 101, 255)):
        used = set()
        for item in group:
            number = item.get("index")
            if number is None:
                continue
            if type(number) is not int or not first <= number <= last or number in used:
                raise ValueError("Некорректный или повторный номер FBD: %r (%s)" % (number, item.get("id")))
            used.add(number)
        for item in group:
            if item.get("index") is None:
                number = next(i for i in range(first, last + 1) if i not in used)
                item["index"] = number
                used.add(number)
    for item in user_channels:
        item.setdefault("source", "user")
    channels[:] = api_channels + user_channels
    ids = set()
    for item in channels:
        channel_id = str(item.get("id", "")).strip()
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,63}", channel_id):
            raise ValueError(f"Некорректный id канала: {channel_id!r}")
        if channel_id in ids:
            raise ValueError(f"Повтор канала: {channel_id}")
        ids.add(channel_id)
        index = item.get("index")
        if not isinstance(index, int) or not 0 <= index <= 255:
            raise ValueError(f"Некорректный номер FBD у {channel_id}: {index!r}")
        if item.get("type") not in TYPES:
            raise ValueError(f"Некорректный type у {channel_id}")
        if item.get("direction") not in DIRECTIONS:
            raise ValueError(f"Некорректный direction у {channel_id}")
    pages = document.get("pages", [])
    if not isinstance(pages, list) or not pages:
        raise ValueError("Нужна хотя бы одна страница")
    if len(pages) > 255:
        raise ValueError("Максимум 255 страниц в одном проекте Web UI")
    widget_count = 0
    for page in pages:
        if not isinstance(page.get("widgets", []), list):
            raise ValueError("widgets должен быть списком")
        for widget in page["widgets"]:
            bindings = widget.get("bindings", [])
            if not isinstance(bindings, list) or len(bindings) > 8:
                raise ValueError("bindings должен быть списком максимум из 8 связей")
            roles = set()
            for binding in bindings:
                role = str(binding.get("role", ""))
                target = str(binding.get("channel", ""))
                direction = str(binding.get("direction", "duplex"))
                if role not in ("value", "setpoint", "alarm", "busy", "result", "series1", "series2"):
                    raise ValueError("Неизвестная роль связи: " + role)
                if role in roles:
                    raise ValueError("Повтор роли bindings: " + role)
                if target not in ids or direction not in DIRECTIONS:
                    raise ValueError("Связь %s должна ссылаться на существующий канал и направление publish/command/duplex" % role)
                target_channel = next(channel for channel in channels if channel["id"] == target)
                if role == "setpoint" and direction == "publish":
                    raise ValueError("Связь setpoint должна иметь направление command или duplex")
                if role != "setpoint" and direction == "command":
                    raise ValueError("Связи состояния должны иметь направление publish или duplex: " + role)
                if role in ("series1", "series2") and str(widget.get("type", "")) != "chart":
                    raise ValueError("Роли series1/series2 доступны только для графика")
                if role in ("series1", "series2") and target_channel["type"] not in ("int32", "float"):
                    raise ValueError("Канал серии графика должен быть числовым: " + target)
                roles.add(role)
            widget_count += 1
            kind = str(widget.get("type", ""))
            if kind not in WIDGET_TYPES:
                raise ValueError(f"Неизвестный тип виджета: {kind}")
            channel_id = str(widget.get("channel", ""))
            static_element = kind in ("heading", "static-text", "divider", "link")
            if static_element and bindings:
                raise ValueError("Статические элементы не принимают связи каналов: " + kind)
            if any(binding["role"] == "setpoint" for binding in bindings) and kind not in {
                "slider", "switch", "checkbox", "button", "text-input", "password-input",
                "number-input", "color-input", "date-input", "time-input", "select", "weekdays"
            }:
                raise ValueError("Роль setpoint доступна только для элементов управления")
            if not static_element and channel_id not in ids:
                raise ValueError(f"Виджет ссылается на неизвестный канал: {channel_id}")
            if static_element:
                channel_id = ""
                widget["channel"] = ""
                if kind in ("static-text", "link") and not str(widget.get("options", "")).strip():
                    raise ValueError(f"{kind} требует непустой текст или URL: {widget.get('id', '?')}")
                channel = None
            else:
                channel = next(item for item in channels if item["id"] == channel_id)
            for binding in bindings:
                if binding["role"] == "setpoint" and binding["channel"] != channel_id:
                    target = next(item for item in channels if item["id"] == binding["channel"])
                    if channel is not None and target["type"] != channel["type"]:
                        raise ValueError("Канал setpoint должен иметь тот же тип, что и основной канал виджета")
            if kind in ("switch", "checkbox", "button", "wifi-scan", "traffic-light") and channel["type"] != "bool":
                raise ValueError(f"{kind} требует bool-канал: {channel_id}")
            if kind in ("slider", "number-input", "gauge", "progress", "chart", "radial-gauge", "battery") and channel["type"] not in ("int32", "float"):
                raise ValueError(f"{kind} требует числовой канал: {channel_id}")
            if kind in ("text-input", "password-input", "color-input", "date-input", "time-input", "select") and channel["type"] != "text":
                raise ValueError(f"{kind} требует text-канал: {channel_id}")
            if kind == "weekdays" and channel["type"] != "int32":
                raise ValueError(f"weekdays требует int32-канал: {channel_id}")
            if kind == "select" and not str(widget.get("options", "")).strip():
                raise ValueError(f"select требует options (варианты через ;): {channel_id}")
            if not 1 <= int(widget.get("maxLength", 63)) <= 63:
                raise ValueError("Длина поля: от 1 до 63 байт UTF-8")
            numbers = [float(widget.get(k, d)) for k, d in (("min", 0), ("max", 100), ("step", 1))]
            if not all(math.isfinite(v) for v in numbers) or numbers[0] > numbers[1] or numbers[2] <= 0:
                raise ValueError("Диапазон: конечные min <= max и step > 0")
            if kind == "number-input" and channel["type"] == "int32" and any(v != int(v) for v in numbers):
                raise ValueError("Целочисленное поле требует целые min, max и step")
            x, y = int(widget.get("x", 1)), int(widget.get("y", 1))
            w, h = int(widget.get("w", 4)), int(widget.get("h", 2))
            if not (1 <= x <= 12 and y >= 1 and 1 <= w <= 12 and 1 <= h <= 12 and x + w <= 13):
                raise ValueError(f"Некорректная сетка виджета {widget.get('id', channel_id)}")
    widget_ids = [str(w.get("id", "")) for pg in pages for w in pg.get("widgets", [])]
    if any(not wid for wid in widget_ids) or len(set(widget_ids)) != len(widget_ids):
        raise ValueError("ID элементов должны быть непустыми и уникальными в проекте")
    if widget_count == 0:
        raise ValueError("Нужен хотя бы один виджет")
    if widget_count > 255:
        raise ValueError("Максимум 255 виджетов в одном проекте Web UI")
    # A project has no total layout/config ceiling.  Only one descriptor is
    # transported at a time.  Keep individual user strings bounded so one
    # malformed label cannot overflow the small deterministic response slot.
    for page in pages:
        if len(str(page.get("id", "")).encode("utf-8")) > 120 or len(str(page.get("title") or page.get("id", "")).encode("utf-8")) > 180:
            raise ValueError("Слишком длинное имя страницы; id максимум 120, название максимум 180 байт")
        for widget in page.get("widgets", []):
            fields = ("id", "type", "label", "channel", "icon", "color", "size", "options", "code", "group", "placeholder", "unit", "confirmation")
            if any(len(str(widget.get(key, "")).encode("utf-8")) > 180 for key in fields):
                raise ValueError(f"Слишком длинное свойство виджета {widget.get('id', '?')}; максимум 180 байт")
    # Every descriptor is served separately by /item. Validate the complete
    # JSON record, not just individual fields, against its deterministic slot.
    labels = {str(item["id"]): str(item.get("label") or item["id"]) for item in channels}
    for page in pages:
        page_payload = json.dumps({"id": str(page.get("id", "main")), "title": str(page.get("title") or page.get("id", "main"))}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(page_payload) > HTTP_ITEM_BYTES:
            raise ValueError("Слишком длинный дескриптор страницы для безопасного HTTP-ответа")
        for item in page.get("widgets", []):
            value = _widget_config(item, labels)
            value["page"] = str(page.get("id", "main"))
            response = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            if len(response) > HTTP_ITEM_BYTES:
                raise ValueError(f"Слишком большой дескриптор виджета {item.get('id', '?')}; сократите подпись или свойства")
    theme = {key: str(document.get("theme", {}).get(key, "")) for key in ("background", "card", "text", "accent")}
    meta = json.dumps({"widgets": widget_count, "pages": len(pages), "theme": theme}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(meta) > HTTP_ITEM_BYTES:
        raise ValueError("Слишком большая тема для безопасного HTTP-ответа")
    return project_id, channels


def validate(document: Dict) -> Tuple[str, List[Dict]]:
    from project_validation import validate_project
    report = validate_project(document)
    errors = [issue for issue in report["issues"] if issue["severity"] == "error"]
    if errors:
        raise ValueError(errors[0]["message"])
    return _validate_legacy(document)


def descriptor(project_id: str, channels: List[Dict], pages: List[Dict], theme: Dict) -> str:
    namespace = safe_identifier(project_id)
    channel_labels = {str(item["id"]): str(item.get("label") or item["id"]) for item in channels}
    rows = [
        "// Generated by FLProg Web UI Designer 1.0. Do not edit.",
        "#pragma once",
        "#include <FLProgWebUi.h>",
        "",
        f"namespace flprog_webui_{namespace} {{",
        "static const FLProgWebUiChannelDescriptor channels[] = {",
    ]
    for item in channels:
        rows.append(f"    {{{c_string(item['id'])}, {TYPES[item['type']]}, {DIRECTIONS[item['direction']]}, {int(item['index'])}}},")
    rows += [
        "};",
    ]
    binding_index = 0
    for page in pages:
        for item in page.get("widgets", []):
            bindings = item.get("bindings", [])
            if not bindings:
                binding_index += 1
                continue
            rows.append(f"static const FLProgWebUiBindingDescriptor bindings_{binding_index}[] = {{")
            for binding in bindings:
                rows.append("    {%s, %s, %s}," % (c_string(str(binding["role"])), c_string(str(binding["channel"])), c_string(str(binding.get("direction", "duplex")))))
            rows.append("};")
            binding_index += 1
    rows += [
        "static const FLProgWebUiWidgetDescriptor widgets[] = {",
    ]
    binding_index = 0
    for page in pages:
        for item in page.get("widgets", []):
            channel = str(item.get("channel", ""))
            values = (str(item.get("id", "")), str(item.get("type", "")), str(item.get("label") or channel_labels.get(channel, channel)), channel,
                      str(item.get("icon", "")), str(item.get("color", "")), str(item.get("size", "normal")))
            numbers = (float(item.get("min", 0)), float(item.get("max", 100)), float(item.get("step", 1)))
            layout = (max(1, min(12, int(item.get("x", 1)))), max(1, min(99, int(item.get("y", 1)))), max(1, min(12, int(item.get("w", 4)))), max(1, min(12, int(item.get("h", 2)))))
            bindings = item.get("bindings", [])
            binding_ref = "bindings_%d" % binding_index if bindings else "0"
            rows.append("    {" + ", ".join(c_string(value) for value in values) + ", " + ", ".join(str(value) + "f" for value in numbers) + ", " + ", ".join(str(value) for value in layout) + ", " + c_string(str(page.get("id", "main"))) + ", " + c_string(str(item.get("options", ""))) + ", " + c_string(str(item.get("code", ""))) + ", " + binding_ref + ", " + str(len(bindings)) + ", " + ", ".join(c_string(str(item.get(k, ""))) for k in ("group", "placeholder", "unit")) + ", " + str(int(item.get("maxLength", 63))) + ", " + c_string(str(item.get("confirmation", "Отправить команду?" if item.get("type") == "button" else ""))) + "},")
            binding_index += 1
    rows += [
        "};",
        "static const FLProgWebUiPageDescriptor pages[] = {",
    ]
    for page in pages:
        rows.append("    {" + c_string(str(page.get("id", "main"))) + ", " + c_string(str(page.get("title") or page.get("id", "main"))) + "},")
    rows += [
        "};",
        "static const FLProgWebUiThemeDescriptor theme = {" + ", ".join(c_string(str(theme.get(key, ""))) for key in ("background", "card", "text", "accent")) + "};",
        "static const uint8_t widgetCount = sizeof(widgets) / sizeof(widgets[0]);",
        "static const uint8_t pageCount = sizeof(pages) / sizeof(pages[0]);",
        "static FLProgWebUiChannelSlot slots[sizeof(channels) / sizeof(channels[0])];",
        "static FLProgWebUiModel model(channels, slots, sizeof(channels) / sizeof(channels[0]));",
        "inline bool configure() { return FLProgWebUiRuntime::configure(model, theme); }",
        "}",
        "",
    ]
    return "\n".join(rows)


def config_ubi(project_id: str, transport_id: str = "wifi-http") -> str:
    """One-time FLProg configuration block for a stable project package."""
    safe = safe_identifier(project_id)
    uid = "webui-config-" + safe
    interface_macros = {
        "wifi-http": "FLPROG_WIFI_INTERFACE1",
        "w5500-http-1": "FLPROG_WIZNET_INTERFACE1",
        "w5500-http-2": "FLPROG_WIZNET_INTERFACE2",
    }
    interface_macro = interface_macros[transport_id]
    setup = (f'flprog_webui_{safe}::configure();\n'
             f'static FLProgWebUiFlprogNetworkPagedHttp webUi(flprog_webui_{safe}::model, flprog_webui_{safe}::widgets, flprog_webui_{safe}::widgetCount, flprog_webui_{safe}::pages, flprog_webui_{safe}::pageCount, flprog_webui_{safe}::theme);\n'
             f'#if defined({interface_macro})\n'
             f'webUi.begin({interface_macro});\n'
             f'#else\n#error "FLProg Web UI: add the selected {transport_id} interface"\n#endif')
    # XML uses only ASCII in structural fields; UTF-16LE is written below.
    return (f'<?xml version="1.0" encoding="utf-16"?>\r\n'
            f'<sixx.object sixx.id="0" sixx.type="BlocksLibraryElement" sixx.env="Arduino"><sixx.object sixx.id="1" sixx.type="CodeUserBlock" sixx.env="Arduino" sixx.name="typeClass">'
            f'<sixx.object sixx.id="2" sixx.type="String" sixx.env="Core" sixx.name="id">{uid}</sixx.object><sixx.object sixx.id="3" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="blocks"/>'
            f'<sixx.object sixx.id="4" sixx.type="String" sixx.env="Core" sixx.name="label">FLProg Web UI Configure: {project_id}</sixx.object><sixx.object sixx.id="5" sixx.type="String" sixx.env="Core" sixx.name="name">FLProg Web UI Configure</sixx.object>'
            f'<sixx.object sixx.id="6" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="inputs"/><sixx.object sixx.id="7" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="outputs"/><sixx.object sixx.id="8" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="variables"/><sixx.object sixx.id="9" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="parametrs"/><sixx.object sixx.id="10" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="userLibraries"/>'
            f'<sixx.object sixx.id="11" sixx.type="String" sixx.env="Core" sixx.name="info">Однократный конфигуратор проекта Web UI.</sixx.object><sixx.object sixx.id="12" sixx.type="CodeUserBlockLoopCodePart" sixx.env="Arduino" sixx.name="loopCodePart"><sixx.object sixx.id="13" sixx.type="String" sixx.env="Core" sixx.name="code"/></sixx.object>'
            f'<sixx.object sixx.id="14" sixx.type="CodeUserBlockSetupCodePart" sixx.env="Arduino" sixx.name="setupCodePart"><sixx.object sixx.id="15" sixx.type="String" sixx.env="Core" sixx.name="code">{setup}</sixx.object></sixx.object>'
            f'<sixx.object sixx.id="16" sixx.type="CodeUserBlockDeclareCodePart" sixx.env="Arduino" sixx.name="declareCodePart"><sixx.object sixx.id="17" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="code"><sixx.object sixx.id="18" sixx.type="CodeUserBlockDeclareDefineBlock" sixx.env="Arduino"><sixx.object sixx.id="19" sixx.type="String" sixx.env="Core" sixx.name="define">#include</sixx.object><sixx.object sixx.id="20" sixx.type="String" sixx.env="Core" sixx.name="name">&lt;{safe}_descriptor.h&gt;</sixx.object></sixx.object><sixx.object sixx.id="21" sixx.type="CodeUserBlockDeclareDefineBlock" sixx.env="Arduino"><sixx.object sixx.id="22" sixx.type="String" sixx.env="Core" sixx.name="define">#include</sixx.object><sixx.object sixx.id="23" sixx.type="String" sixx.env="Core" sixx.name="name">&lt;adapters/FLProgWebUiFlprogNetworkPagedHttp.h&gt;</sixx.object></sixx.object></sixx.object></sixx.object><sixx.object sixx.id="24" sixx.type="CodeUserBlockFunctuinCodePart" sixx.env="Arduino" sixx.name="functionCodePart"><sixx.object sixx.id="25" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="code"/></sixx.object><sixx.object sixx.name="notCanManyUse" sixx.type="True" sixx.env="Core"/></sixx.object></sixx.object>\r\n')


def build(source: Path, destination: Path) -> Path:
    document = json.loads(source.read_text(encoding="utf-8"))
    project_id, channels = validate(document)
    transport_id = str(document.get("transport", {}).get("id", "wifi-http"))
    if transport_id not in ("wifi-http", "w5500-http-1", "w5500-http-2"):
        raise ValueError("Неподдерживаемый transport.id")
    library_name = "FLProg_WebUI_Project_" + safe_identifier(project_id)
    target = destination / library_name
    source_dir = target / "src"
    source_dir.mkdir(parents=True, exist_ok=True)
    (target / "library.properties").write_text(
        f"name={library_name}\nversion=1.0.0\nauthor=FLProg Web UI Designer\n"
        "maintainer=FLProg Web UI Designer\nurl=https://github.com/flprog/FLProg_Network\n"
        "sentence=Generated FLProg Web UI project package.\n"
        "paragraph=Project descriptor and FLProg configurator generated by FLProg Web UI Editor.\n"
        "category=Other\narchitectures=*\ndepends=FLProg_WebUI\n", encoding="utf-8")
    (source_dir / f"{safe_identifier(project_id)}_descriptor.h").write_text(
        descriptor(project_id, channels, document.get("pages", []), document.get("theme", {})), encoding="utf-8")
    (target / f"FLProg_WebUI_Configure_{safe_identifier(project_id)}.ubi").write_bytes(
        b"\xff\xfe" + config_ubi(project_id, transport_id).encode("utf-16-le"))
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Собрать отдельный пакет FLProg Web UI")
    parser.add_argument("project", type=Path, help="Файл .flpui")
    parser.add_argument("--output", required=True, type=Path, help="Папка libraries sketchbook")
    args = parser.parse_args()
    print(build(args.project, args.output))
