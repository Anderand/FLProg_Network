#!/usr/bin/env python3
"""Build stable, universal FLProg Web UI user blocks (UBI files).

The blocks use a numeric descriptor-channel index.  They are intentionally
independent of page layout, labels and widget placement.
"""
from pathlib import Path
from uuid import uuid4, uuid5, NAMESPACE_URL
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runtime" / "FLProg_WebUI" / "user_blocks"

TYPES = (
    ("Bool", "BooleanDataType", "bool", "publishBool", "takeBool"),
    ("Int", "IntegerDataType", "int32_t", "publishInt", "takeInt"),
    ("Float", "FloatDataType", "float", "publishFloat", "takeFloat"),
    ("Text", "StringDataType", "String", "publishText", "takeText"),
)


def pin(name, typ, incoming, number):
    direction = "True" if incoming else "False"
    cache = "" if incoming else '<sixx.object sixx.name="nameCash" sixx.idref="%d"/>' % (number + 5)
    return (f'<sixx.object sixx.id="{number}" sixx.type="InputsOutputsAdaptorForUserBlock" sixx.env="Arduino">'
            f'<sixx.object sixx.id="{number+1}" sixx.type="String" sixx.env="Core" sixx.name="id">{uuid4()}</sixx.object>'
            f'<sixx.object sixx.id="{number+2}" sixx.type="UniversalBlockInputOutput" sixx.env="Arduino" sixx.name="object">'
            f'<sixx.object sixx.id="{number+3}" sixx.type="String" sixx.env="Core" sixx.name="id">{uuid4()}</sixx.object>'
            f'<sixx.object sixx.name="block" sixx.idref="1"/>'
            f'<sixx.object sixx.id="{number+4}" sixx.type="{typ}" sixx.env="Arduino" sixx.name="type"/>'
            f'<sixx.object sixx.name="isInput" sixx.type="{direction}" sixx.env="Core"/>'
            f'<sixx.object sixx.id="{number+5}" sixx.type="String" sixx.env="Core" sixx.name="name">{escape(name)}</sixx.object>'
            f'<sixx.object sixx.name="isNot" sixx.type="False" sixx.env="Core"/>{cache}</sixx.object>'
            f'<sixx.object sixx.id="{number+6}" sixx.type="String" sixx.env="Core" sixx.name="comment"/></sixx.object>')


def block(kind, datatype, cpp, publish, take, command):
    title = f"FLProg Web UI {'Command' if command else 'Publish'} {kind}"
    ident = uuid5(NAMESPACE_URL, "flprog-webui-1/" + title)
    # Object ids must be unique throughout an FLProg .ubi document.  The
    # outer block uses the small range 0..19; pins deliberately start at 100.
    inputs = [pin("EN", "BooleanDataType", True, 100),
              pin("CHANNEL", "IntegerDataType", True, 110)]
    outputs = []
    if command:
        outputs = [pin("NEW", "BooleanDataType", False, 130), pin("VALUE", datatype, False, 140)]
        loop = f"NEW = false;\nif (EN) NEW = FLProgWebUiRuntime::{take}((uint8_t)CHANNEL, VALUE);"
        info = "Читает одну новую команду Web UI. CHANNEL — индекс канала в descriptor проекта."
    else:
        inputs.append(pin("VALUE", datatype, True, 120))
        value = "VALUE.c_str()" if datatype == "StringDataType" else "VALUE"
        loop = f"if (EN) FLProgWebUiRuntime::{publish}((uint8_t)CHANNEL, {value});"
        info = "Публикует значение в Web UI. CHANNEL — индекс канала в descriptor проекта."
    decl = ('<sixx.object sixx.id="900" sixx.type="CodeUserBlockDeclareDefineBlock" sixx.env="Arduino">'
            '<sixx.object sixx.id="901" sixx.type="String" sixx.env="Core" sixx.name="define">#include</sixx.object>'
            '<sixx.object sixx.id="902" sixx.type="String" sixx.env="Core" sixx.name="name">&lt;FLProgWebUi.h&gt;</sixx.object></sixx.object>')
    return ('<?xml version="1.0" encoding="utf-16"?>\r\n'
            '<sixx.object sixx.id="0" sixx.type="BlocksLibraryElement" sixx.env="Arduino">'
            '<sixx.object sixx.id="1" sixx.type="CodeUserBlock" sixx.env="Arduino" sixx.name="typeClass">'
            f'<sixx.object sixx.id="2" sixx.type="String" sixx.env="Core" sixx.name="id">{ident}</sixx.object>'
            '<sixx.object sixx.id="3" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="blocks"/>'
            f'<sixx.object sixx.id="4" sixx.type="String" sixx.env="Core" sixx.name="label">{title}</sixx.object>'
            f'<sixx.object sixx.id="5" sixx.type="String" sixx.env="Core" sixx.name="name">{title}</sixx.object>'
            f'<sixx.object sixx.id="6" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="inputs">{"".join(inputs)}</sixx.object>'
            f'<sixx.object sixx.id="7" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="outputs">{"".join(outputs)}</sixx.object>'
            '<sixx.object sixx.id="8" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="variables"/>'
            '<sixx.object sixx.id="9" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="parametrs"/>'
            '<sixx.object sixx.id="10" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="userLibraries"/>'
            f'<sixx.object sixx.id="11" sixx.type="String" sixx.env="Core" sixx.name="info">{info}</sixx.object>'
            f'<sixx.object sixx.id="12" sixx.type="CodeUserBlockLoopCodePart" sixx.env="Arduino" sixx.name="loopCodePart"><sixx.object sixx.id="13" sixx.type="String" sixx.env="Core" sixx.name="code">{escape(loop)}</sixx.object></sixx.object>'
            '<sixx.object sixx.id="14" sixx.type="CodeUserBlockSetupCodePart" sixx.env="Arduino" sixx.name="setupCodePart"><sixx.object sixx.id="15" sixx.type="String" sixx.env="Core" sixx.name="code"/></sixx.object>'
            f'<sixx.object sixx.id="16" sixx.type="CodeUserBlockDeclareCodePart" sixx.env="Arduino" sixx.name="declareCodePart"><sixx.object sixx.id="17" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="code">{decl}</sixx.object></sixx.object>'
            '<sixx.object sixx.id="18" sixx.type="CodeUserBlockFunctuinCodePart" sixx.env="Arduino" sixx.name="functionCodePart"><sixx.object sixx.id="19" sixx.type="OrderedCollection" sixx.env="Core" sixx.name="code"/></sixx.object>'
            '<sixx.object sixx.name="notCanManyUse" sixx.type="False" sixx.env="Core"/></sixx.object></sixx.object>\r\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for kind, datatype, cpp, publish, take in TYPES:
        for command in (False, True):
            name = f"FLProg_WebUI_{'Command' if command else 'Publish'}_{kind}.ubi"
            (OUT / name).write_bytes(b"\xff\xfe" + block(kind, datatype, cpp, publish, take, command).encode("utf-16-le"))
    build_group()


def build_group():
    """Create one FLProg BlocksLibraryGroup with all generated UBI elements."""
    root = ET.Element("sixx.object", {"sixx.id": "0", "sixx.type": "BlocksLibraryGroup", "sixx.env": "Arduino"})
    elements = ET.SubElement(root, "sixx.object", {"sixx.id": "1", "sixx.name": "elements", "sixx.type": "OrderedCollection", "sixx.env": "Core"})
    next_id = 10
    for source in sorted(OUT.glob("FLProg_WebUI_*.ubi")):
        if source.name == "FLProg_WebUI_Start.ubi":
            continue  # Professional starter is imported as its own .ubi document.
        element = ET.parse(str(source)).getroot()
        mapping = {}
        for node in element.iter():
            old = node.get("sixx.id")
            if old is not None:
                mapping[old] = str(next_id)
                next_id += 1
        for node in element.iter():
            old = node.get("sixx.id")
            if old is not None:
                node.set("sixx.id", mapping[old])
            old_ref = node.get("sixx.idref")
            if old_ref in mapping:
                node.set("sixx.idref", mapping[old_ref])
        elements.append(element)
    descriptor = ET.SubElement(root, "sixx.object", {"sixx.id": str(next_id), "sixx.name": "typeClass", "sixx.type": "UserBlockFolderDescriptor", "sixx.env": "Arduino"})
    next_id += 1
    ET.SubElement(descriptor, "sixx.object", {"sixx.id": str(next_id), "sixx.name": "name", "sixx.type": "String", "sixx.env": "Core"}).text = "FLProg Web UI"
    next_id += 1
    ET.SubElement(descriptor, "sixx.object", {"sixx.id": str(next_id), "sixx.name": "id", "sixx.type": "String", "sixx.env": "Core"}).text = str(uuid5(NAMESPACE_URL, "flprog-webui-1/universal-blocks"))
    ET.SubElement(root, "sixx.object", {"sixx.name": "isReadOnly", "sixx.type": "False", "sixx.env": "Core"})
    (OUT / "FLProg_WebUI_Universal_Blocks.ubl").write_bytes(ET.tostring(root, encoding="utf-16", xml_declaration=True))


if __name__ == "__main__":
    main()
