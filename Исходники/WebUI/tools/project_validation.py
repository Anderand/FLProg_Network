"""Structured, non-mutating project diagnostics shared by the editor and builder."""
import copy
import math
import re
from field_pattern import parse_pattern
from group_style import validate_group_styles

STATIC = {"heading", "static-text", "divider", "link"}
COMMAND = {"switch", "checkbox", "button", "slider", "number-input", "text-input",
           "password-input", "color-input", "date-input", "time-input", "select", "weekdays", "wifi-scan"}
EXPECTED = {}
for kinds, types in [
    ({"switch", "checkbox", "button", "wifi-scan", "traffic-light"}, {"bool"}),
    ({"slider", "number-input", "gauge", "progress", "chart", "radial-gauge", "sector-gauge", "bar-meter", "battery"}, {"float", "int32"}),
    ({"text-input", "password-input", "color-input", "date-input", "time-input", "select"}, {"text"}),
    ({"weekdays"}, {"int32"}),
]:
    for kind in kinds:
        EXPECTED[kind] = types
ROLES = {"value", "setpoint", "busy", "result", "enabled", "alarm", "series1", "series2"}


def _validate_project(document):
    import build_project_package as generator
    issues = []

    def add(code, message, pi=None, wi=None, tab="data", severity="error", related=None, channel=None):
        issue = dict(code=code, message=message, severity=severity, tab=tab)
        if pi is not None:
            issue["pageIndex"] = pi
            issue["pageTitle"] = str(pages[pi].get("title") or pages[pi].get("id") or pi + 1)
        if wi is not None:
            issue["widgetIndex"] = wi
            widget = pages[pi]["widgets"][wi]
            issue["widgetTitle"] = str(widget.get("label") or widget.get("id") or wi + 1)
        if related is not None:
            issue["relatedWidgetIndex"] = related
        if channel is not None:
            issue["channelId"] = channel
        issues.append(issue)

    def result():
        errors = sum(i["severity"] == "error" for i in issues)
        return dict(ok=True, valid=not errors, issues=issues,
                    summary=dict(errors=errors, warnings=len(issues) - errors))

    pages = []
    if not isinstance(document, dict):
        add("document", "Проект должен быть объектом JSON", tab="project")
        return result()
    channels = document.get("channels", [])
    pages = document.get("pages", [])
    if not isinstance(channels, list) or any(not isinstance(c, dict) for c in channels):
        add("channels", "Список каналов повреждён", tab="channels")
        return result()
    if not isinstance(pages, list) or any(not isinstance(p, dict) or not isinstance(p.get("widgets", []), list) or any(not isinstance(w, dict) for w in p.get("widgets", [])) for p in pages):
        add("pages", "Список страниц или виджетов повреждён", tab="project")
        return result()

    def channel_location(id):
        for pi, page in enumerate(pages):
            for wi, w in enumerate(page.get("widgets", [])):
                bindings = w.get("bindings", [])
                if w.get("channel") == id or (isinstance(bindings, list) and any(isinstance(b, dict) and b.get("channel") == id for b in bindings)):
                    return pi, wi
        return None, None

    by_id, indexes = {}, set()
    for c in channels:
        id = str(c.get("id", ""))
        pi, wi = channel_location(id)
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,63}", id):
            add("channel-id", "Некорректный ID канала: " + id, pi, wi, channel=id)
        if id in by_id:
            add("duplicate-channel", "Повторяется канал: " + id, pi, wi, channel=id)
        by_id[id] = c
        if c.get("type") not in generator.TYPES:
            add("channel-type", "Неизвестный тип канала «%s»: %s" % (id, c.get("type")), pi, wi, channel=id)
        if c.get("direction") not in generator.DIRECTIONS:
            add("channel-direction", "Некорректное направление канала «%s»" % id, pi, wi, channel=id)
        number = c.get("index")
        if number is not None:
            first, last = (0, 100) if c.get("source") and c.get("source") != "user" else (101, 255)
            if type(number) is not int or not first <= number <= last or number in indexes:
                add("channel-index", "Некорректный или повторный номер FBD канала «%s»" % id, pi, wi, channel=id)
            if type(number) is int:
                indexes.add(number)
    widget_ids, page_ids = set(), set()
    for pi, page in enumerate(pages):
        try:
            validate_group_styles(page)
        except ValueError as error:
            add("group-style",str(error),pi,tab="general")
        page_id = str(page.get("id", ""))
        if not page_id or page_id in page_ids:
            add("page-id", "ID страницы пустой или повторяется: " + page_id, pi, tab="project")
        page_ids.add(page_id)
        widgets = page.get("widgets", [])
        rectangles = []
        for wi, w in enumerate(widgets):
            def problem(code, text, tab="data"):
                add(code, text, pi, wi, tab)
            id, kind = str(w.get("id", "")), w.get("type")
            if not id or id in widget_ids:
                problem("widget-id", "ID виджета пустой или повторяется: " + id, "general")
            widget_ids.add(id)
            if kind not in generator.WIDGET_TYPES:
                problem("widget-type", "Неизвестный тип виджета: " + str(kind), "general")
            try:
                parse_pattern(w.get("pattern", ""))
                if w.get("pattern") and kind not in ("text-input", "password-input"): raise ValueError("Шаблон доступен только текстовому полю и паролю")
                message=w.get("validationMessage", "")
                if not isinstance(message,str) or len(message.encode("utf-8"))>96 or any(ord(c)<32 for c in message): raise ValueError("Текст ошибки: до 96 байт UTF-8")
            except ValueError as error:
                problem("field-pattern", str(error), "behavior")
            primary = by_id.get(str(w.get("channel", "")))
            if kind not in STATIC and primary is None:
                problem("missing-channel", "Не выбран основной канал или он отсутствует: " + str(w.get("channel") or "—"))
            if primary and kind in EXPECTED and primary.get("type") not in EXPECTED[kind]:
                problem("widget-channel-type", "Для «%s» нужен канал %s; выбран %s" % (kind, "/".join(sorted(EXPECTED[kind])), primary.get("type")))
            bindings = w.get("bindings", [])
            if not isinstance(bindings, list) or any(not isinstance(b, dict) for b in bindings):
                problem("bindings", "Список дополнительных связей повреждён")
                bindings = []
            if kind in STATIC and bindings:
                problem("static-binding", "Статический элемент не принимает связи каналов")
            roles = set()
            for b in bindings:
                role = b.get("role")
                if role not in ROLES or role in roles:
                    problem("binding-role", "Неизвестная или повторная роль связи: " + str(role))
                roles.add(str(role))
                target = by_id.get(str(b.get("channel", "")))
                if not target:
                    problem("missing-binding-channel", "Связь «%s» ссылается на отсутствующий канал: %s" % (role, b.get("channel") or "—"))
                    continue
                direction = b.get("direction", "duplex")
                if direction not in generator.DIRECTIONS or (role == "setpoint" and (direction == "publish" or target.get("direction") == "publish")) or (role != "setpoint" and (direction == "command" or target.get("direction") == "command")):
                    problem("binding-direction", "Неподходящее направление связи «%s» и её канала" % role)
                if role in ("busy", "alarm", "enabled") and target.get("type") != "bool":
                    problem("binding-type", "Связь «%s» требует bool-канал" % role)
                if role == "enabled" and kind not in COMMAND:
                    problem("enabled-widget", "Связь enabled доступна только элементу управления")
                if role == "setpoint":
                    if kind not in COMMAND:
                        problem("setpoint-widget", "Связь setpoint доступна только элементу управления")
                    if primary and target.get("type") != primary.get("type"):
                        problem("setpoint-type", "Тип setpoint должен совпадать с типом основного канала")
                if role in ("series1", "series2") and (kind != "chart" or target.get("type") not in ("int32", "float")):
                    problem("series-type", "Серия графика требует chart и числовой канал")
                if role == "value" and kind in EXPECTED and target.get("type") not in EXPECTED[kind]:
                    problem("value-type", "Тип канала value не подходит виджету «%s»" % kind)
            if kind in COMMAND:
                setpoint = next((b for b in bindings if b.get("role") == "setpoint"), None)
                target = by_id.get(str(setpoint.get("channel", ""))) if setpoint else primary
                if target and target.get("direction") == "publish":
                    problem("readonly-command", "Командный канал доступен только для чтения; выберите command/duplex или связь setpoint")
            elif kind not in STATIC and primary and primary.get("direction") == "command":
                problem("command-display", "Для показания нужен publish/duplex-канал, а не command")
            try:
                x,y,width,height = [float(w.get(k, default)) for k,default in (("x",1),("y",1),("w",4),("h",2))]
                if not all(math.isfinite(v) and v == int(v) for v in (x,y,width,height)) or not (1<=x<=12 and 1<=y<=99 and 1<=width<=12 and 1<=height<=12 and x+width<=13):
                    raise ValueError()
                rectangles.append((wi,str(w.get("group") or "").strip(),x,y,width,height))
            except (ValueError, TypeError, OverflowError):
                problem("grid", "Некорректные X/Y/W/H: целая сетка 12 колонок, Y 1…99, размеры 1…12", "layout")
        for i, a in enumerate(rectangles):
            for b in rectangles[i+1:]:
                if a[1] == b[1] and a[2] < b[2]+b[4] and a[2]+a[4] > b[2] and a[3] < b[3]+b[5] and a[3]+a[5] > b[3]:
                    title = str(widgets[b[0]].get("label") or widgets[b[0]].get("id") or b[0]+1)
                    add("overlap", "Пересечение с виджетом «%s» в группе «%s»" % (title,a[1] or "Без группы"), pi,a[0],"layout","warning",b[0])
    # Preserve all pre-existing generator limits (UTF-8 envelopes, channel
    # counts, ranges, options, etc.) without mutating the user's model.
    if not any(i["severity"] == "error" for i in issues):
        try:
            generator._validate_legacy(copy.deepcopy(document))
        except (ValueError, TypeError, AttributeError, KeyError, OverflowError) as e:
            add("generator", str(e), tab="project")
    return result()


def validate_project(document):
    try:
        return _validate_project(document)
    except (ValueError, TypeError, AttributeError, KeyError, OverflowError) as error:
        return dict(ok=True, valid=False, summary=dict(errors=1, warnings=0), issues=[
            dict(code="structure", severity="error", tab="project",
                 message="Некорректная структура проекта: " + str(error))])
