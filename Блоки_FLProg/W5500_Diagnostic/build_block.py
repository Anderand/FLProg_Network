#!/usr/bin/env python3
"""Generate the FLProg W5500 diagnostic user-block library."""
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "FLProg_W5500_Diagnostic.ubi"
BLOCK_UUID = uuid5(NAMESPACE_URL, "flprog-w5500-diagnostic-user-block/v0.1")

INPUTS = [
    ("EN", "BooleanDataType"),
    ("NET_NUM", "IntegerDataType"),
]
OUTPUTS = [
    ("FOUND", "BooleanDataType"),
    ("MODE", "LongDataType"),
    ("WIZNET", "BooleanDataType"),
    ("RMII", "BooleanDataType"),
    ("SPI_BUS", "LongDataType"),
    ("SPI_EFF_BUS", "LongDataType"),
    ("CS_PIN", "LongDataType"),
    ("CHIP", "StringDataType"),
    ("CHIP_CODE", "LongDataType"),
    ("HW_STATUS", "LongDataType"),
    ("SPI_STATUS", "LongDataType"),
    ("SPI_TX", "LongDataType"),
    ("LINK", "LongDataType"),
    ("ETH_READY", "BooleanDataType"),
    ("IP", "StringDataType"),
    ("IP_ASSIGNED", "BooleanDataType"),
    ("DHCP_STATE", "LongDataType"),
    ("DHCP_ERROR", "LongDataType"),
    ("DHCP_SERVER", "StringDataType"),
    ("NET_STATUS", "LongDataType"),
    ("NET_ERROR", "LongDataType"),
    ("RESULT", "BooleanDataType"),
    ("SEQ", "LongDataType"),
    ("MS", "LongDataType"),
    ("LINE", "StringDataType"),
]


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


LOOP_CODE = r'''{
  static uint32_t flprogW5500DiagLastAt = 0;
  static uint32_t flprogW5500DiagSequence = 0;
  static bool flprogW5500DiagWasEnabled = false;
  const uint32_t flprogW5500DiagNow = millis();

  if (!EN) {
    flprogW5500DiagWasEnabled = false;
    FOUND = false; MODE = 0; WIZNET = false; RMII = false;
    SPI_BUS = 0; SPI_EFF_BUS = 0; CS_PIN = 0; CHIP = "";
    CHIP_CODE = 0; HW_STATUS = 0; SPI_STATUS = 0; SPI_TX = 0;
    LINK = 0; ETH_READY = false; IP = "0.0.0.0"; IP_ASSIGNED = false;
    DHCP_STATE = 0; DHCP_ERROR = 0; DHCP_SERVER = "0.0.0.0";
    NET_STATUS = 0; NET_ERROR = 0; RESULT = false; SEQ = 0; MS = 0;
    LINE = "";
  } else if (!flprogW5500DiagWasEnabled ||
             (uint32_t)(flprogW5500DiagNow - flprogW5500DiagLastAt) >= 1000UL) {
    flprogW5500DiagWasEnabled = true;
    flprogW5500DiagLastAt = flprogW5500DiagNow;
    SEQ = (int32_t)flprogW5500DiagSequence++;
    MS = (int32_t)flprogW5500DiagNow;
    FOUND = false; MODE = 0; WIZNET = false; RMII = false;
    SPI_BUS = 0; SPI_EFF_BUS = 0; CS_PIN = 0; CHIP = "";
    CHIP_CODE = 0; HW_STATUS = 0; SPI_STATUS = 0; SPI_TX = 0;
    LINK = 0; ETH_READY = false; IP = "0.0.0.0"; IP_ASSIGNED = false;
    DHCP_STATE = 0; DHCP_ERROR = 0; DHCP_SERVER = "0.0.0.0";
    NET_STATUS = 0; NET_ERROR = 0; RESULT = false;

    FLProgNetworkInterface *flprogW5500DiagNetwork = nullptr;
    if ((int32_t)NET_NUM >= 0 &&
        (int32_t)NET_NUM < (int32_t)FLPROG_NETWORK_DEVICE_INVALID) {
      flprogW5500DiagNetwork = flprogNetworkDevices.getDevice(
          (FLProgNetworkDeviceId)NET_NUM);
    }

    if (flprogW5500DiagNetwork != nullptr) {
      FOUND = true;
      MODE = (int32_t)flprogW5500DiagNetwork->networkMode();
      WIZNET = flprogW5500DiagNetwork->wiznetMode();
      RMII = flprogW5500DiagNetwork->rmiiMode();
      SPI_BUS = (int32_t)flprogW5500DiagNetwork->spiBus();
      SPI_EFF_BUS = (int32_t)flprogW5500DiagNetwork->effectiveWiznetSpiBus();
      CS_PIN = (int32_t)flprogW5500DiagNetwork->pinCs();
      CHIP = flprogW5500DiagNetwork->chipName();
      CHIP_CODE = (int32_t)flprogW5500DiagNetwork->chipCode();
      HW_STATUS = (int32_t)flprogW5500DiagNetwork->hardwareStatus();
      SPI_STATUS = (int32_t)flprogW5500DiagNetwork->spiStatus();
      SPI_TX = (int32_t)flprogW5500DiagNetwork->spiTransactionCount();
      LINK = (int32_t)flprogW5500DiagNetwork->linkStatus();
      ETH_READY = flprogW5500DiagNetwork->wiznetIsReady();
      IP = flprogW5500DiagNetwork->wiznetIPString();
      IP_ASSIGNED = (IP != "0.0.0.0");
      DHCP_STATE = (int32_t)flprogW5500DiagNetwork->dhcpState();
      DHCP_ERROR = (int32_t)flprogW5500DiagNetwork->dhcpError();
      DHCP_SERVER = flprogW5500DiagNetwork->dhcpServer().toString();
      NET_STATUS = (int32_t)flprogW5500DiagNetwork->getStatus();
      NET_ERROR = (int32_t)flprogW5500DiagNetwork->getError();
      RESULT = (CHIP_CODE == 55) && ETH_READY && IP_ASSIGNED;
    }

    // RT_HW Console truncates a String after 100 ASCII characters. Keep the
    // summary focused on Ethernet bring-up; detailed values stay on the pins.
    String flprogW5500DiagLine(F("found="));
    flprogW5500DiagLine += FOUND ? 1 : 0;
    flprogW5500DiagLine += F(" chip=");
    flprogW5500DiagLine += CHIP;
    flprogW5500DiagLine += '/';
    flprogW5500DiagLine += CHIP_CODE;
    flprogW5500DiagLine += F(" spi=");
    flprogW5500DiagLine += SPI_STATUS;
    flprogW5500DiagLine += F(" tx=");
    flprogW5500DiagLine += SPI_TX;
    flprogW5500DiagLine += F(" link=");
    flprogW5500DiagLine += LINK;
    flprogW5500DiagLine += F(" ready=");
    flprogW5500DiagLine += ETH_READY ? 1 : 0;
    flprogW5500DiagLine += F(" ip=");
    flprogW5500DiagLine += IP;
    flprogW5500DiagLine += F(" dhcp=");
    flprogW5500DiagLine += DHCP_STATE;
    flprogW5500DiagLine += '/';
    flprogW5500DiagLine += DHCP_ERROR;
    flprogW5500DiagLine += F(" net=");
    flprogW5500DiagLine += NET_STATUS;
    flprogW5500DiagLine += '/';
    flprogW5500DiagLine += NET_ERROR;
    LINE = flprogW5500DiagLine;
  }
}'''


def build():
    root = ET.Element("sixx.object", {"sixx.id": "0", "sixx.type": "BlocksLibraryElement", "sixx.env": "Arduino"})
    block = ET.SubElement(root, "sixx.object", {"sixx.id": "1", "sixx.type": "CodeUserBlock", "sixx.env": "Arduino", "sixx.name": "typeClass"})

    def obj(parent, ident, typ, name, text=None, env="Core"):
        node = ET.SubElement(parent, "sixx.object", {"sixx.id": str(ident), "sixx.type": typ, "sixx.env": env, "sixx.name": name})
        if text is not None:
            node.text = text
        return node

    obj(block, 2, "String", "id", str(BLOCK_UUID))
    obj(block, 3, "OrderedCollection", "blocks")
    obj(block, 4, "String", "label", "FLProg W5500 Тест")
    obj(block, 5, "String", "name", "FLProg W5500 Тест")
    input_collection = obj(block, 6, "OrderedCollection", "inputs")
    pin_id = 100
    for name, datatype in INPUTS:
        input_collection.append(ET.fromstring(pin(name, datatype, True, pin_id)))
        pin_id += 10
    output_collection = obj(block, 7, "OrderedCollection", "outputs")
    pin_id = 200
    for name, datatype in OUTPUTS:
        output_collection.append(ET.fromstring(pin(name, datatype, False, pin_id)))
        pin_id += 10
    obj(block, 8, "OrderedCollection", "variables")
    obj(block, 9, "OrderedCollection", "parametrs")
    obj(block, 10, "OrderedCollection", "userLibraries")
    obj(block, 11, "String", "info", "Диагностические выходы уже настроенного FLProg W5500/Ethernet интерфейса и компактная строка LINE. Подключите LINE либо отдельные выходы к RT_HW Console. Блок не меняет настройки и не вызывает Ethernet pool/connect.")
    loop_part = ET.SubElement(block, "sixx.object", {"sixx.id": "12", "sixx.type": "CodeUserBlockLoopCodePart", "sixx.env": "Arduino", "sixx.name": "loopCodePart"})
    obj(loop_part, 13, "String", "code", LOOP_CODE)
    setup = ET.SubElement(block, "sixx.object", {"sixx.id": "14", "sixx.type": "CodeUserBlockSetupCodePart", "sixx.env": "Arduino", "sixx.name": "setupCodePart"})
    registration = []
    for index in range(1, 9):
        registration.extend([
            f"#if defined(FLPROG_WIZNET_INTERFACE{index})",
            f"flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId){index}, &FLPROG_WIZNET_INTERFACE{index});",
            "#endif",
        ])
    obj(setup, 15, "String", "code", "\n".join(registration))
    declare = ET.SubElement(block, "sixx.object", {"sixx.id": "16", "sixx.type": "CodeUserBlockDeclareCodePart", "sixx.env": "Arduino", "sixx.name": "declareCodePart"})
    decl_collection = obj(declare, 17, "OrderedCollection", "code")
    for ident, include_name in ((900, "<flprogNetwork.h>"),
                               (910, "<device/flprogNetworkDeviceRegistry.h>")):
        define = ET.SubElement(decl_collection, "sixx.object", {"sixx.id": str(ident), "sixx.type": "CodeUserBlockDeclareDefineBlock", "sixx.env": "Arduino"})
        obj(define, ident + 1, "String", "define", "#include")
        obj(define, ident + 2, "String", "name", include_name)
    function = ET.SubElement(block, "sixx.object", {"sixx.id": "18", "sixx.type": "CodeUserBlockFunctuinCodePart", "sixx.env": "Arduino", "sixx.name": "functionCodePart"})
    obj(function, 19, "OrderedCollection", "code")
    ET.SubElement(block, "sixx.object", {"sixx.name": "notCanManyUse", "sixx.type": "True", "sixx.env": "Core"})

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
    if labels != ["FLProg W5500 Тест"]:
        raise ValueError("unexpected block label: " + repr(labels))
    pins = {}
    for direction in ("inputs", "outputs"):
        names = []
        collection = block.find(f"sixx.object[@sixx.name='{direction}']")
        for adaptor in collection:
            name_node = adaptor.find("sixx.object/sixx.object[@sixx.name='name']")
            names.append(name_node.text if name_node is not None else "")
        pins[direction] = names
    if set(pins["inputs"]) != {name for name, _ in INPUTS}:
        raise ValueError("FBD inputs are missing or malformed")
    if set(pins["outputs"]) != {name for name, _ in OUTPUTS}:
        raise ValueError("FBD outputs are missing or malformed")
    code = "\n".join(node.text or "" for node in block.iter() if node.get("sixx.name") == "code")
    if "LINE = flprogW5500DiagLine;" not in code:
        raise ValueError("combined diagnostic output missing")
    if "RT_HW_console.outPrint" in code:
        raise ValueError("block must expose values, not print directly")
    for define in block.iter("sixx.object"):
        if define.get("sixx.type") == "CodeUserBlockDeclareDefineBlock":
            fields = {child.get("sixx.name") for child in define}
            if not {"define", "name"}.issubset(fields):
                raise ValueError("malformed include declaration")


if __name__ == "__main__":
    print(build())
