#!/usr/bin/env python3
"""Check typed RMII lookup compiles with WI-FI_ONLY and no complete RMII class."""
from pathlib import Path
import subprocess,shutil,tempfile
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'src/flprogNetwork.h').read_text()
marker='#if FLPROG_NETWORK_HAS_RMII_INTERFACE\n// Typed RMII device lookup follows'
assert source.count(marker)==1
rmii_tail=source.split(marker,1)[1]
rmii_tail=rmii_tail.rsplit('#endif // FLPROG_NETWORK_AVR_LITE',1)[0]
code=r'''#define FLPROG_NETWORK_HAS_RMII_INTERFACE 0
#include <cstdint>
#include <cassert>
#include "device/flprogNetworkDeviceRegistry.h"
class FLProgNetworkInterface {
public:
 FLProgNetworkDeviceKind deviceKind()const{return FLPROG_NETWORK_DEVICE_KIND_BASE;}
};
'''+marker+rmii_tail+r'''
int main(){
 FLProgNetworkDeviceRegistry registry;
 FLProgNetworkInterface base;
 assert(registry.registerDevice(1,base)==FLPROG_NETWORK_DEVICE_OK);
 assert(!registry.existsRmii(1));
 assert(registry.getRmii(1)==nullptr);
 assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_TYPE_MISMATCH);
 assert(registry.getRmii(2)==nullptr);
 assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_NOT_FOUND);
 assert(registry.getRmii(255)==nullptr);
 assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_INVALID_ID);
 const FLProgNetworkDeviceRegistry& c=registry;
 assert(c.getRmii(1)==nullptr);
 assert(!c.existsRmii(1));
}
'''
with tempfile.TemporaryDirectory() as directory:
 f=Path(directory)/'test.cpp';f.write_text(code)
 for compiler in ('g++','clang++'):
  if not shutil.which(compiler):continue
  cmd=[compiler,'-std=c++11','-Wall','-Wextra','-Werror','-fno-rtti','-fno-exceptions','-I',str(ROOT/'src'),str(f),str(ROOT/'src/device/flprogNetworkDeviceRegistry.cpp'),'-o',str(Path(directory)/'test')]
  subprocess.run(cmd,check=True);subprocess.run([str(Path(directory)/'test')],check=True)
  print('WIFI_ONLY_TYPED_RMII_PASS',compiler)
