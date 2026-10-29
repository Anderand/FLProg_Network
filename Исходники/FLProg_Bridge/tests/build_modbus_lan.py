from pathlib import Path
import subprocess,json,hashlib,shutil
r=Path(r'E:\FLP\Flprog_network');w=Path(r'E:\SAI\FLProg_Network\_work\modbus_lan_bridge_20261029');ide=Path(r'C:\F-981\FLProg\ideV8');out=w/'build';out.mkdir(exist_ok=True,parents=True)
sketch=w/'BridgeModbusLanPrototype'
shutil.copy2(r/'flprog_bridge/esp32/BridgeModbusLanPrototype/BridgeModbusLanPrototype.ino',sketch/'BridgeModbusLanPrototype.ino')
for name in ['BridgeNetworkEndpoint.h','BridgeNetworkConfig.h','BridgeReadClient.h','BridgeWire.h','BridgeModbusTcp.h','BoundedRelay.h']:
 shutil.copy2(r/'flprog_bridge/esp32/FLProgBridgeEsp32'/name,sketch/name)
cmd=[str(ide/'arduino-builder.exe'),'-compile','-jobs=4','-logger=human']
for p in [ide/'hardware',ide/'portable/packages']:cmd+=['-hardware',str(p)]
for p in [ide/'tools-builder',ide/'hardware/tools/avr',ide/'portable/packages']:cmd+=['-tools',str(p)]
cmd+=['-built-in-libraries',str(ide/'libraries'),'-libraries',str(w/'libraries'),'-fqbn','esp32:esp32:esp32','-build-path',str(out),str(w/'BridgeModbusLanPrototype/BridgeModbusLanPrototype.ino')]
with (w/'BUILD.log').open('wb') as f:result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
assert result.returncode==0,'ESP32 build failed: '+str(w/'BUILD.log')
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.bin')}
(w/'BUILD.json').write_text(json.dumps(dict(board='classic ESP32',fqbn='esp32:esp32:esp32',core='3.3.11',files=files,flashed=False,credentials_configured=False,universal_plc_bridge=True,runtime_setup=False,runtime_configuration=True,config_namespace="flpbridge-lan",service_modes=["raw3234","modbus502"],prototype_only=True,network_backends=["WiFi","Wiznet","RMII"],web_settings_integrated=False),indent=2),encoding='utf-8');print('ESP32 compiled; not flashed')
