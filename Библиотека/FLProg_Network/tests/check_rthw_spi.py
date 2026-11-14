#!/usr/bin/env python3
"""Compile actual RT_HW SPI backend template with a fake RT_HW session implementation."""
import shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='flprog_rthw_') as d:
 p=Path(d)
 (p/'Arduino.h').write_text('#pragma once\n#include <stdint.h>\n')
 (p/'SPI.h').write_text('#pragma once\nclass SPIClass{};\n')
 (p/'test.cpp').write_text(r'''
#include <cassert>
#include <cstdint>
#include <iostream>
#include "hardware/flprogSpiBackend.h"
struct Device {
    uint8_t bus=0,cs=0,custom=0,status=0,err=0,codeErr=0;
    uint32_t speed=0;bool sessionOpen=false;
};
struct RtBase {
  bool busy=false;bool failInit=false;bool failSession=false;int sessions=0;int ends=0;int inits=0;
  uint8_t getETH_bus(uint8_t){return 1;}
  int getETH_cs(uint8_t){return 12;}
  bool checkPinDOT(uint8_t pin){return pin<200;}
  bool spiCheckBus(uint8_t bus){return bus<4;}
  bool spiGetBusy(uint8_t){return busy;}
  void spiInitDevice(Device& d){++inits;d.status=failInit?0:1;d.err=failInit?1:0;}
  uint8_t spiBeginSession(Device& d){if(failSession)return 0;++sessions;d.sessionOpen=true;return 1;}
  void spiEndSession(Device& d){if(d.sessionOpen){++ends;d.sessionOpen=false;}}
  uint8_t spiLL_Transfer(Device&,uint8_t x){return uint8_t(x+1);}
};
static bool probe(uint8_t,void* p){return *static_cast<bool*>(p);}
int main(){
  RtBase rt;
  FLProgRtHwSpiBackend<RtBase,Device> b(rt);
  assert(b.cs()==-1);
  b.configure(255,-1,20000000);
  assert(b.status()==FLPROG_SPI_STATUS_OK);
  assert(b.bus()==1 && b.cs()==12 && b.device().speed==20000000);
  assert(b.begin()); assert(rt.inits==1);
  assert(b.beginTransaction());assert(b.device().sessionOpen);
  assert(b.transfer(0x10)==0x11);
  b.endTransaction();assert(rt.sessions==1 && rt.ends==1);
  bool held=true; b.setBusyProbe(probe,&held);
  assert(!b.beginTransaction());assert(b.status()==FLPROG_SPI_STATUS_BUSY);
  held=false;rt.busy=true;
  assert(!b.begin());assert(b.status()==FLPROG_SPI_STATUS_BUSY);
  rt.busy=false;
  assert(b.begin());
  rt.failSession=true;
  assert(!b.beginTransaction());assert(b.status()==FLPROG_SPI_STATUS_BUSY);
  rt.failSession=false;
  b.configure(0,256,1000000); assert(b.status()==FLPROG_SPI_STATUS_PIN_ERROR);
  assert(!b.begin());
  b.configure(0,255,1000000); // fallback to first ETH CS; rejected when switching bus on live device
  assert(b.status()==FLPROG_SPI_STATUS_UNAVAILABLE);
  std::cout<<"RTHW_SPI_PASS\n";
}
''')
 for compiler in ('g++','clang++'):
  if not shutil.which(compiler):continue
  cmd=[compiler,'-std=c++11','-Wall','-Wextra','-Werror','-fno-rtti','-fno-exceptions','-I',str(p),'-I',str(ROOT/'src'),str(p/'test.cpp'),'-o',str(p/'test')]
  print('COMPILER',compiler,flush=True)
  subprocess.run(cmd,check=True)
  subprocess.run([str(p/'test')],check=True)
print('ALL_RTHW_SPI_TESTS_PASS')
