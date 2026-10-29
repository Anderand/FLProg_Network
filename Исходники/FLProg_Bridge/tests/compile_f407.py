"""Compile-only gate, never flashes and never modifies IDE libraries."""
from pathlib import Path
import shutil
import sys

R=Path(__file__).resolve().parents[2]
W=Path(sys.argv[1]).resolve()
lib=W/'libraries';lib.mkdir(exist_ok=True)
shutil.copytree(R/'flprog_webui_next/runtime/FLProg_WebUI',lib/'FLProg_WebUI',dirs_exist_ok=True)
sketch=W/'bridge_gate';sketch.mkdir(exist_ok=True)
for source in (R/'flprog_bridge/firmware').glob('*.h'):shutil.copy2(source,sketch/source.name)
(sketch/'bridge_gate.ino').write_text('''// COMPILE ONLY. Not a replacement for the FLE4D application.
#include <Arduino.h>
#include "FLProgWebUiBridge.h"
Uart bridgeUart(PC7,PC6); // FLProg STM32 core 3.0.0 names the concrete serial class Uart.
FLProgWebUiChannelDescriptor channels[] = {
 {"uptime",FLPROG_WEBUI_INT32,FLPROG_WEBUI_PUBLISH,10},
 {"setpoint",FLPROG_WEBUI_FLOAT,FLPROG_WEBUI_DUPLEX,101}};
FLProgWebUiChannelSlot slots[2];
FLProgWebUiModel model(channels,slots,2);
flprog_bridge::Server bridge("{\\"projectId\\":\\"bridge-compile-only\\",\\"model\\":\\"FLE4D-30MT\\",\\"firmware\\":\\"0.1-COMPILE-ONLY\\"}");
FLProgWebUiBridge web(model); // Read-only until a project supplies a write policy.
void setup() {bridgeUart.setRx(PC7);bridgeUart.setTx(PC6);bridgeUart.begin(115200);web.attach(bridge);}
void loop() {model.publishInt(0,(int32_t)millis());bridge.pool(bridgeUart,millis(),64);}
''',encoding='utf-8')
sys.path.insert(0,str(R/'hardware_gates/STM32_OTA_PORTABILITY'))
sys.path.insert(0,str(R/'flprog_webui_next/tools'))
import build_stm32_ota as b
b.ROOT=W/'build_tools';b.ROOT.mkdir(exist_ok=True)
shutil.copy2(R/'hardware_gates/STM32_OTA_PORTABILITY/boards_catalog.json',b.ROOT/'boards_catalog.json')
b.build('FLProg_FLE4D_30MT',sketch/'bridge_gate.ino',True,libraries=lib,package=False)
