#!/usr/bin/env python3
"""No Arduino SDK: compile the actual registry + typed accessor implementation with minimal class stubs."""
import re, subprocess, shutil, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
real=(ROOT/'src/flprogNetwork.h').read_text()
anchor='// Safe typed NET NUM lookups:'
assert real.count(anchor)==1, 'typed getter implementation missing'
actual=real.split(anchor,1)[1]
with tempfile.TemporaryDirectory(prefix='flprog_typed_') as tmp:
 p=Path(tmp)
 src='''#include <cassert>\n#include <cstdint>\n#include <iostream>\n#include "device/flprogNetworkDeviceRegistry.h"\n
class FLProgNetworkInterface {
public:
    FLProgNetworkDeviceKind deviceKind() const { return kind_; }
    void networkMode(uint8_t x){mode_=x;}
    uint8_t networkMode() const{return mode_;}
protected:
    void setDeviceKind(FLProgNetworkDeviceKind k){kind_=k;}
private:
    FLProgNetworkDeviceKind kind_=FLPROG_NETWORK_DEVICE_KIND_BASE;
    uint8_t mode_=0;
};
class FLProgWiznetInterface:public FLProgNetworkInterface {
public:FLProgWiznetInterface(){setDeviceKind(FLPROG_NETWORK_DEVICE_KIND_WIZNET);networkMode(1);}
};
class FLProgOnBoardWifiInterface:public FLProgNetworkInterface {
public:FLProgOnBoardWifiInterface(){setDeviceKind(FLPROG_NETWORK_DEVICE_KIND_WIFI);networkMode(0);}
};
// The following definitions are copied verbatim from the actual shipped header.
'''+ '// Safe typed NET NUM lookups:'+actual + r'''
int main(){
    FLProgWiznetInterface wz;
    FLProgOnBoardWifiInterface wf;
    FLProgNetworkInterface base;
    auto &registry=flprogNetworkDevices;
    registry.clear();
    assert(!registry.existsWiznet(1));
    assert(!registry.existsWifi(1));
    assert(!registry.existsWiznet(255));
    assert(!registry.existsWifi(255));
    assert(registry.getDevice(1)==nullptr);
    assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_NOT_FOUND);
    assert(registry.getWiznet(1)==nullptr);
    assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_NOT_FOUND);
    assert(registry.getWifi(255)==nullptr);
    assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_INVALID_ID);
    assert(registry.idFor(&wf)==255);
    assert(registry.registerDevice(1,wz)==FLPROG_NETWORK_DEVICE_OK);
    assert(registry.registerDevice(2,wf)==FLPROG_NETWORK_DEVICE_OK);
    assert(registry.registerDevice(3,base)==FLPROG_NETWORK_DEVICE_OK);
    assert(registry.exists(1) && registry.exists(2) && registry.exists(3));
    assert(registry.existsWiznet(1));
    assert(!registry.existsWifi(1));
    assert(registry.existsWifi(2));
    assert(!registry.existsWiznet(2));
    assert(!registry.existsWiznet(3));
    assert(!registry.existsWifi(3));
    assert(!registry.existsWiznet(254) && !registry.existsWifi(254));
    const auto before=registry.lastResult();
    const auto idBefore=registry.lastId();
    assert(!registry.existsWifi(1) && !registry.existsWiznet(2));
    assert(registry.lastResult()==before && registry.lastId()==idBefore);
    assert(registry.getWiznet(1)==&wz);
    assert(registry.getWifi(2)==&wf);
    assert(registry.getWiznet(2)==nullptr);
    assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_TYPE_MISMATCH);
    assert(registry.getWifi(1)==nullptr);
    assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_TYPE_MISMATCH);
    assert(registry.getWiznet(3)==nullptr);
    assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_TYPE_MISMATCH);
    // Changing routing mode must not forge the C++ dynamic wrapper type.
    wz.networkMode(0); wf.networkMode(1);
    assert(registry.existsWiznet(1) && registry.existsWifi(2));
    assert(!registry.existsWifi(1) && !registry.existsWiznet(2));
    assert(registry.getWiznet(1)==&wz);
    assert(registry.getWifi(2)==&wf);
    const auto &c=registry;
    assert(c.existsWiznet(1) && c.existsWifi(2));
    assert(!c.existsWifi(1) && !c.existsWiznet(2));
    assert(c.getWiznet(1)==&wz);
    assert(c.getWifi(2)==&wf);
    assert(c.getWiznet(2)==nullptr);
    assert(c.lastResult()==FLPROG_NETWORK_DEVICE_TYPE_MISMATCH);
    assert(c.getDevice(100)==nullptr);
    assert(registry.registerDevice(1,wf)==FLPROG_NETWORK_DEVICE_DUPLICATE_ID);
    assert(registry.unregisterDevice(1,&wf)==FLPROG_NETWORK_DEVICE_OWNER_MISMATCH);
    assert(registry.unregisterDevice(1,&wz)==FLPROG_NETWORK_DEVICE_OK);
    assert(!registry.existsWiznet(1));
    assert(!registry.existsWifi(1));
    assert(registry.existsWifi(2));
    assert(registry.getWiznet(1)==nullptr);
    assert(registry.lastResult()==FLPROG_NETWORK_DEVICE_NOT_FOUND);
    assert(registry.unregisterDevice(2,&wf)==FLPROG_NETWORK_DEVICE_OK);
    registry.clear();
    assert(!registry.existsWiznet(1) && !registry.existsWifi(2));
    std::cout << "TYPED_REGISTRY_AND_EXISTS_PASS" << std::endl;
}
'''
 (p/'registry_test.cpp').write_text(src)
 for compiler in ('g++','clang++'):
  if not shutil.which(compiler):continue
  cmd=[compiler,'-std=c++11','-Wall','-Wextra','-Werror','-pedantic','-fno-rtti','-fno-exceptions','-I',str(ROOT/'src'),str(p/'registry_test.cpp'),str(ROOT/'src/device/flprogNetworkDeviceRegistry.cpp'),'-o',str(p/'a.out')]
  print('COMPILER',compiler,flush=True)
  subprocess.run(cmd,check=True)
  subprocess.run([str(p/'a.out')],check=True)
  sanitizer=cmd.copy();sanitizer[-2:-2]=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
  sanitizer[-1]=str(p/'asan.out')
  # LLVM sanitizer and GCC ASan may be unavailable on individual hosts; mandatory when present.
  subprocess.run(sanitizer,check=True)
  subprocess.run([str(p/'asan.out')],check=True)
print('ALL_TYPED_REGISTRY_TESTS_PASS')
