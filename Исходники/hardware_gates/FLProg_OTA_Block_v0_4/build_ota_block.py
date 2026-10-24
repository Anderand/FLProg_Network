#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the FLProg universal OTA user-block .ubi file."""
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "FLProg_OTA_Universal.ubi"
BLOCK_UUID = uuid5(NAMESPACE_URL, "flprog-ota-universal-user-block/v0.4")


def pin(name, datatype, incoming, n):
    direction = "True" if incoming else "False"
    cache = "" if incoming else f'<sixx.object sixx.name="nameCash" sixx.idref="{n + 5}"/>'
    return (
        f'<sixx.object sixx.id="{n}" sixx.type="InputsOutputsAdaptorForUserBlock" sixx.env="Arduino">'
        f'<sixx.object sixx.id="{n+1}" sixx.type="String" sixx.env="Core" sixx.name="id">{uuid5(BLOCK_UUID, "adaptor/" + name)}</sixx.object>'
        f'<sixx.object sixx.id="{n+2}" sixx.type="UniversalBlockInputOutput" sixx.env="Arduino" sixx.name="object">'
        f'<sixx.object sixx.id="{n+3}" sixx.type="String" sixx.env="Core" sixx.name="id">{uuid5(BLOCK_UUID, "pin/" + name)}</sixx.object>'
        '<sixx.object sixx.name="block" sixx.idref="1"/>'
        f'<sixx.object sixx.id="{n+4}" sixx.type="{datatype}" sixx.env="Arduino" sixx.name="type"/>'
        f'<sixx.object sixx.name="isInput" sixx.type="{direction}" sixx.env="Core"/>'
        f'<sixx.object sixx.id="{n+5}" sixx.type="String" sixx.env="Core" sixx.name="name">{escape(name)}</sixx.object>'
        f'<sixx.object sixx.name="isNot" sixx.type="False" sixx.env="Core"/>{cache}</sixx.object>'
        f'<sixx.object sixx.id="{n+6}" sixx.type="String" sixx.env="Core" sixx.name="comment"/></sixx.object>'
    )


def build():
    inputs = [
        pin("EN", "BooleanDataType", True, 100),
        pin("NET_NUM", "IntegerDataType", True, 110),
        pin("PASSWORD", "StringDataType", True, 120),
        pin("VERSION", "StringDataType", True, 200),
    ]
    outputs = [
        pin("SUPPORTED", "BooleanDataType", False, 130),
        pin("READY", "BooleanDataType", False, 140),
        pin("BUSY", "BooleanDataType", False, 150),
        pin("FAULT", "BooleanDataType", False, 160),
        pin("STATE", "LongDataType", False, 170),
        pin("ERR", "LongDataType", False, 180),
        pin("RX_BYTES", "LongDataType", False, 190),
    ]
    loop = (
        "flprogOtaUniversal.control(EN, (int32_t)NET_NUM, PASSWORD, VERSION);\n"
        "SUPPORTED = flprogOtaUniversal.supported();\n"
        "READY = flprogOtaUniversal.ready();\n"
        "BUSY = flprogOtaUniversal.busy();\n"
        "STATE = flprogOtaUniversal.state();\n"
        "ERR = flprogOtaUniversal.error();\n"
        "RX_BYTES = flprogOtaUniversal.receivedBytes();\n"
        "FAULT = (ERR != 0) || !SUPPORTED;"
    )
    root = ET.Element("sixx.object", {"sixx.id": "0", "sixx.type": "BlocksLibraryElement", "sixx.env": "Arduino"})
    block = ET.SubElement(root, "sixx.object", {"sixx.id": "1", "sixx.type": "CodeUserBlock", "sixx.env": "Arduino", "sixx.name": "typeClass"})

    def obj(parent, ident, typ, name, text=None, env="Core"):
        node = ET.SubElement(parent, "sixx.object", {"sixx.id": str(ident), "sixx.type": typ, "sixx.env": env, "sixx.name": name})
        if text is not None:
            node.text = text
        return node

    obj(block, 2, "String", "id", str(BLOCK_UUID))
    obj(block, 3, "OrderedCollection", "blocks")
    obj(block, 4, "String", "label", "FLProg OTA")
    obj(block, 5, "String", "name", "FLProg OTA")
    input_collection = obj(block, 6, "OrderedCollection", "inputs")
    for xml_pin in inputs:
        input_collection.append(ET.fromstring(xml_pin))
    output_collection = obj(block, 7, "OrderedCollection", "outputs")
    for xml_pin in outputs:
        output_collection.append(ET.fromstring(xml_pin))
    obj(block, 8, "OrderedCollection", "variables")
    obj(block, 9, "OrderedCollection", "parametrs")
    obj(block, 10, "OrderedCollection", "userLibraries")
    obj(block, 11, "String", "info", "Один блок на проект. EN=true, NET_NUM=номер сети FLProg, PASSWORD может быть пустым. VERSION — версия прошивки до 31 байта UTF-8. Модель берётся из выбранной платы менеджера. SPI и Ethernet настраиваются в FLProg. STM32: F407 512/1024 КиБ и F103 256/512 КиБ с W5500, только с соответствующим OTA-профилем и загрузчиком. После успешной передачи автоматический перезапуск. Новые платформы требуют проверки на оборудовании. Неверный адрес сборки запрещён. Блок не защищает от внешнего полного стирания Flash. ESP8266/ESP32: прежний ArduinoOTA по Wi-Fi.")
    loop_part = ET.SubElement(block, "sixx.object", {"sixx.id": "12", "sixx.type": "CodeUserBlockLoopCodePart", "sixx.env": "Arduino", "sixx.name": "loopCodePart"})
    obj(loop_part, 13, "String", "code", loop)
    setup = ET.SubElement(block, "sixx.object", {"sixx.id": "14", "sixx.type": "CodeUserBlockSetupCodePart", "sixx.env": "Arduino", "sixx.name": "setupCodePart"})
    declare = ET.SubElement(block, "sixx.object", {"sixx.id": "16", "sixx.type": "CodeUserBlockDeclareCodePart", "sixx.env": "Arduino", "sixx.name": "declareCodePart"})
    decl_collection = obj(declare, 17, "OrderedCollection", "code")
    define = ET.SubElement(decl_collection, "sixx.object", {"sixx.id": "900", "sixx.type": "CodeUserBlockDeclareDefineBlock", "sixx.env": "Arduino"})
    obj(define, 901, "String", "define", "#include")
    obj(define, 902, "String", "name", "<flprogOtaUniversalBlock.h>")
    standard = ET.SubElement(decl_collection, "sixx.object", {"sixx.id": "910", "sixx.type": "CodeUserBlockDeclareStandartBlock", "sixx.env": "Arduino"})
    obj(standard, 911, "String", "name", "flprogOtaUniversal")
    obj(standard, 912, "String", "lastPart", ";")
    obj(standard, 913, "String", "firstPart", "FLProgOtaUniversalBlock")
    function = ET.SubElement(block, "sixx.object", {"sixx.id": "18", "sixx.type": "CodeUserBlockFunctuinCodePart", "sixx.env": "Arduino", "sixx.name": "functionCodePart"})
    obj(function, 19, "OrderedCollection", "code")
    ET.SubElement(block, "sixx.object", {"sixx.name": "notCanManyUse", "sixx.type": "True", "sixx.env": "Core"})

    setup_code = [
        "#if defined(ARDUINO_ARCH_STM32)"
    ]
    for index in range(1, 9):
        setup_code.extend([
            "#if defined(FLPROG_WIZNET_INTERFACE{})".format(index),
            "flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId){}, &FLPROG_WIZNET_INTERFACE{});".format(index, index),
            "#endif",
        ])
    setup_code.extend([
        "#elif defined(ESP8266) || defined(ESP32)"
    ])
    for index in range(1, 9):
        setup_code.extend([
            "#if defined(FLPROG_WIFI_INTERFACE{})".format(index),
            "flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId){}, &FLPROG_WIFI_INTERFACE{});".format(index, index),
            "#endif",
        ])
    setup_code.append("#endif")
    obj(setup, 15, "String", "code", "\n".join(setup_code))

    xml = '<?xml version="1.0" encoding="utf-16"?>\r\n' + ET.tostring(root, encoding="unicode", short_empty_elements=True)
    OUT.write_bytes(xml.encode("utf-16"))
    verify(OUT)
    return OUT


def verify(path):
    root = ET.parse(str(path)).getroot()
    if root.get("sixx.type") != "BlocksLibraryElement":
        raise ValueError("expected BlocksLibraryElement root")
    ids = [node.get("sixx.id") for node in root.iter() if node.get("sixx.id") is not None]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate sixx.id values")
    id_set = set(ids)
    for node in root.iter():
        ref = node.get("sixx.idref")
        if ref is not None and ref not in id_set:
            raise ValueError("unresolved sixx.idref: " + ref)
    block = next((node for node in root.iter() if node.get("sixx.type") == "CodeUserBlock"), None)
    if block is None:
        raise ValueError("no CodeUserBlock found")
    labels = [node.text or "" for node in block if node.get("sixx.name") == "label"]
    if labels != ["FLProg OTA"]:
        raise ValueError("unexpected block label: " + repr(labels))
    input_names = [node.text for node in block.iter() if node.get("sixx.name") == "name" and node.get("sixx.type") == "String" and node.text in {"EN", "NET_NUM", "PASSWORD", "VERSION"}]
    output_names = [node.text for node in block.iter() if node.get("sixx.name") == "name" and node.get("sixx.type") == "String" and node.text in {"SUPPORTED", "READY", "BUSY", "FAULT", "STATE", "ERR", "RX_BYTES"}]
    if set(input_names) != {"EN", "NET_NUM", "PASSWORD", "VERSION"}:
        raise ValueError("FBD inputs are missing or malformed")
    if set(output_names) != {"SUPPORTED", "READY", "BUSY", "FAULT", "STATE", "ERR", "RX_BYTES"}:
        raise ValueError("FBD outputs are missing or malformed")


if __name__ == "__main__":
    print(build())
