# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description='Native regression checks for legacy RESET and SPI setters')
parser.add_argument('--library', type=Path, default=Path(__file__).resolve().parents[2]/'Библиотека/FLProg_Network')
parser.add_argument('--zig', default=shutil.which('zig'))
parser.add_argument('--output', type=Path)
args = parser.parse_args()
if not args.zig:
    parser.error('Zig must be on PATH or supplied with --zig')
library = args.library.resolve()/'src'
temporary = tempfile.TemporaryDirectory(prefix='flprog-network-setters-')
work = args.output.resolve() if args.output else Path(temporary.name)
work.mkdir(parents=True, exist_ok=True)
stubs = work / 'stubs'
stubs.mkdir(exist_ok=True)
(stubs / 'Arduino.h').write_text('''#pragma once
#include <cstdint>
#include <cstddef>
#define NUM_DIGITAL_PINS 40
#define OUTPUT 1
uint32_t millis(); uint32_t micros();
void digitalWrite(uint8_t, uint8_t); void pinMode(uint8_t, uint8_t);
''', encoding='utf-8')
(stubs / 'SPI.h').write_text('#pragma once\nclass SPIClass {};\n', encoding='utf-8')
(stubs / 'IPAddress.h').write_text('#pragma once\nclass IPAddress {};\n', encoding='utf-8')

def method(source, signature):
    start = source.index(signature)
    brace = source.index('{', start)
    depth, end = 1, brace+1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

network = (library / 'flprogNetwork.cpp').read_text(encoding='utf-8-sig')
hardware = (library / 'hardware/flprogWiznetHardware.cpp').read_text(encoding='utf-8-sig')
backend = (library / 'hardware/flprogSpiBackend.cpp').read_text(encoding='utf-8-sig')
assert network.index('_poolEntered = 1;', network.index('uint8_t FLProgNetworkInterface::pool()')) < network.index('syncBlockInputs();', network.index('uint8_t FLProgNetworkInterface::pool()'))
hw_methods = [method(hardware, sig) for sig in [
    'FLProgWiznetHardware::FLProgWiznetHardware()', 'void FLProgWiznetHardware::syncSpiBackendConfiguration()',
    'uint8_t FLProgWiznetHardware::spiBackendKind() const', 'uint8_t FLProgWiznetHardware::effectiveSpiBus() const',
    'uint8_t FLProgWiznetHardware::normalizedBus() const', 'uint8_t FLProgWiznetHardware::setSpiSpeedRuntime(',
    'uint8_t FLProgWiznetHardware::setStartupDelayMs(', 'uint8_t FLProgWiznetHardware::setResetMode(',
    'uint8_t FLProgWiznetHardware::serviceStartup()']]
hw_methods = [('#if FLPROG_NETWORK_COMPILE_WIRED\n' + item + '\n#endif')
              if 'FLProgWiznetHardware::setSpiSpeedRuntime(' in item else item
              for item in hw_methods]
net_methods = [method(network, sig) for sig in [
    'uint8_t FLProgNetworkInterface::setWiznetPoolFactory(',
    'uint8_t FLProgNetworkInterface::setPinRST(', 'uint8_t FLProgNetworkInterface::setSpeedSPI(',
    'uint8_t FLProgNetworkInterface::prepareWiznetPool()']]
writer = method(network, 'static uint8_t flprogLegacyArduinoResetWrite(')
prefix = r'''
#include <cassert>
#include <cstdio>
#include <vector>
#include <utility>
#include "flprogNetworkProfile.h"
#define private public
#include "hardware/flprogWiznetHardware.h"
#undef private
static uint32_t clockMs = 0, clockUs = 0;
static int spiCalls = 0, pinModes = 0;
static std::vector<std::pair<int,int>> writes;
uint32_t millis() { return clockMs; }
uint32_t micros() { return clockUs; }
void digitalWrite(uint8_t pin, uint8_t level) { writes.emplace_back(pin, level); }
void pinMode(uint8_t, uint8_t) { ++pinModes; }
struct TestRtDevice {
    uint8_t bus=0,cs=255,custom=0,status=0,err=0,codeErr=0;
    uint32_t speed=0; bool sessionOpen=false;
};
struct TestRtHw {
    uint8_t getETH_bus(uint8_t) { return 1; }
    int getETH_cs(uint8_t) { return 10; }
    bool checkPinDOT(uint8_t pin) { return pin<40; }
    bool spiCheckBus(uint8_t bus) { return bus<4; }
    bool spiGetBusy(uint8_t) { return false; }
    void spiInitDevice(TestRtDevice &d) { ++spiCalls; d.status=1; }
    uint8_t spiBeginSession(TestRtDevice &d) { ++spiCalls; d.sessionOpen=true; return 1; }
    void spiEndSession(TestRtDevice &d) { ++spiCalls; d.sessionOpen=false; }
    uint8_t spiLL_Transfer(TestRtDevice &, uint8_t value) { ++spiCalls; return value; }
};
FLProgArduinoSpiBackend::FLProgArduinoSpiBackend() {}
bool FLProgArduinoSpiBackend::begin() { ++spiCalls; return true; }
bool FLProgArduinoSpiBackend::beginTransaction() { ++spiCalls; return true; }
void FLProgArduinoSpiBackend::endTransaction() { ++spiCalls; }
uint8_t FLProgArduinoSpiBackend::transfer(uint8_t value) { ++spiCalls; return value; }
bool FLProgArduinoSpiBackend::busAvailable() const { return true; }
bool FLProgArduinoSpiBackend::pinsSupported() const { return true; }
#define FLPROG_NETWORK_MODE_ETHERNET 2
class FLProgNetworkInterface {
public:
    FLProgWiznetHardware hw;
    uint8_t mode=FLPROG_NETWORK_MODE_ETHERNET;
    bool wiz=true, rmii=false;
    uint8_t networkMode() const { return mode; }
    bool wiznetMode() const { return wiz; }
    bool rmiiMode() const { return rmii; }
    FLProgWiznetHardware &wiznetRef() { return hw; }
    uint8_t setPinRST(uint8_t pin=255), setSpeedSPI(uint32_t hz), prepareWiznetPool();
    uint8_t _poolPreparation=0, _poolEntered=0, _poolPinRST=255, _poolPinRSTRequested=0;
    uint32_t _poolSpeedSPI=0;
    uint8_t _poolSpeedSPIRequested=0, _wiznetBackendExplicit=0;
    static FLProgSpiBackend *(*_wiznetPoolFactory)();
    static FLProgEthernetResetWriter _wiznetPoolResetWriter;
    static uint8_t setWiznetPoolFactory(FLProgSpiBackend *(*)(), FLProgEthernetResetWriter);
    void setWiznetSpiBackend(FLProgSpiBackend *backend) {
        _wiznetBackendExplicit=1; hw._spiBackend=backend; hw.syncSpiBackendConfiguration();
    }
};
FLProgSpiBackend *(*FLProgNetworkInterface::_wiznetPoolFactory)()=nullptr;
FLProgEthernetResetWriter FLProgNetworkInterface::_wiznetPoolResetWriter=nullptr;
static TestRtHw factoryBase;
static FLProgRtHwSpiBackend<TestRtHw, TestRtDevice> factoryBackend(factoryBase);
static int factoryCalls=0, rtWrites=0;
static FLProgSpiBackend *testFactory() { ++factoryCalls; return &factoryBackend; }
static FLProgSpiBackend *failedFactory() { return nullptr; }
static uint8_t testRtWriter(uint8_t pin,uint8_t level) {
    if(pin>=40) return 0; ++rtWrites; digitalWrite(pin,level); return 1;
}
'''
tests = r'''
int main() {
    FLProgWiznetHardware legacy;
    assert(legacy.serviceStartup() == FLPROG_WIZNET_HW_READY); // no added wait unless opted in
    assert(!legacy.setResetMode(FLPROG_ETH_RESET_NONE)); // startup configuration closes even on legacy path
    assert(!legacy.setStartupDelayMs(500));
    assert(writes.empty() && spiCalls==0);
#if FLPROG_NETWORK_COMPILE_WIRED && !FLPROG_NETWORK_PROFILE_WIFI_ONLY
    FLProgNetworkInterface net;
    assert(net.setPinRST(255)==1 && net.setSpeedSPI(20000000UL)==1);
    assert(net.hw.spiSpeed()==14000000UL && !net.hw._startupConfigured);
    assert(writes.empty() && spiCalls==0);
    net._poolEntered=1;
    assert(net.prepareWiznetPool()==1);
    assert(net.hw.spiSpeed()==20000000UL && net.hw.resetMode()==FLPROG_ETH_RESET_NONE);
    assert(net.setPinRST(7)==0);
    assert(net.hw.serviceStartup()==FLPROG_WIZNET_HW_WAIT);
    clockMs=499; assert(net.hw.serviceStartup()==FLPROG_WIZNET_HW_WAIT);
    clockMs=500; assert(net.hw.serviceStartup()==FLPROG_WIZNET_HW_READY);
    assert(writes.empty() && spiCalls==0);
    net.hw._initState=2;
    assert(net.setSpeedSPI(10000000UL)==1 && net.hw._initState==2);
    assert(FLProgSpiArbiter::tryLock(0, &net.hw));
    assert(net.setSpeedSPI(8000000UL)==0 && net.hw.spiSpeed()==10000000UL);
    FLProgSpiArbiter::unlock(0, &net.hw);
    assert(net.setSpeedSPI(8000000UL)==1 && net.hw._initState==2);
    assert(net.setSpeedSPI(0)==0 && net.hw.spiSpeed()==8000000UL);
    puts("PASS: exact pr1 calls, deferred application, pin 255 without GPIO; runtime SPI without reset and busy rejection");

    FLProgNetworkInterface invalid;
    assert(invalid.setSpeedSPI(0)==0);
    invalid._poolEntered=1;
    assert(invalid.prepareWiznetPool()==0 && invalid._poolPreparation==2);
    FLProgNetworkInterface wifi; wifi.mode=1;
    assert(!wifi.setPinRST(5) && !wifi.setSpeedSPI(1000));
    FLProgNetworkInterface rmii; rmii.rmii=true;
    assert(!rmii.setPinRST(5) && !rmii.setSpeedSPI(1000));
    assert(writes.empty() && spiCalls==0);
    puts("PASS: invalid frequency and WiFi/RMII transport isolation");

    TestRtHw rtBase;
    FLProgRtHwSpiBackend<TestRtHw, TestRtDevice> rtBackend(rtBase);
    FLProgNetworkInterface rtNet;
    rtNet.hw._spiBackend=&rtBackend;
    rtNet.hw.syncSpiBackendConfiguration();
    assert(rtNet.setPinRST(255) && !rtNet.setPinRST(5));
    assert(rtNet.setSpeedSPI(20000000UL));
    rtNet._poolEntered=1;
    assert(rtNet.prepareWiznetPool());
    assert(rtBackend._device.speed==20000000UL && rtBackend.bus()==1);
    rtNet.hw._initState=2;
    assert(rtNet.setSpeedSPI(10000000UL));
    assert(rtBackend._device.speed==10000000UL && rtNet.hw._initState==2);
    assert(writes.empty() && spiCalls==0);
    puts("PASS: real RT_HW backend configuration remains passive; pin 255 accepted, implicit GPIO writer rejected");

    FLProgNetworkInterface reset;
    reset.hw._pinCs=10;
    assert(reset.setPinRST(5)==1 && writes.empty());
    reset._poolEntered=1;
    assert(reset.prepareWiznetPool()==1 && writes.empty());
    clockMs=0xffffff00u; clockUs=0xfffffc00u;
    assert(reset.hw.serviceStartup()==FLPROG_WIZNET_HW_WAIT);
    assert(writes.size()==1 && writes[0]==std::make_pair(5,0));
    clockUs += 1999; assert(reset.hw.serviceStartup()==FLPROG_WIZNET_HW_WAIT && writes.size()==1);
    ++clockUs; assert(reset.hw.serviceStartup()==FLPROG_WIZNET_HW_WAIT);
    assert(writes.size()==2 && writes[1]==std::make_pair(5,1));
    clockMs += 499; assert(reset.hw.serviceStartup()==FLPROG_WIZNET_HW_WAIT);
    ++clockMs; assert(reset.hw.serviceStartup()==FLPROG_WIZNET_HW_READY);
    assert(reset.hw.serviceStartup()==FLPROG_WIZNET_HW_READY && writes.size()==2 && spiCalls==0);
    assert(!reset.hw.setResetMode(FLPROG_ETH_RESET_NONE));
    FLProgNetworkInterface collision; collision.hw._pinCs=7;
    assert(collision.setPinRST(7));
    assert(!collision.prepareWiznetPool());
    FLProgNetworkInterface badpin;
    assert(badpin.setPinRST(NUM_DIGITAL_PINS));
    assert(badpin.prepareWiznetPool());
    assert(badpin.hw.serviceStartup()==FLPROG_WIZNET_HW_ERROR && writes.size()==2);
    puts("PASS: managed reset once, 2 ms pulse + 500 ms recovery, micros/millis wrap, CS collision and invalid-pin refusal");
    writes.clear(); clockMs=0; clockUs=0;
    assert(!FLProgNetworkInterface::setWiznetPoolFactory(nullptr,testRtWriter));
    assert(FLProgNetworkInterface::setWiznetPoolFactory(testFactory,testRtWriter));
    assert(FLProgNetworkInterface::setWiznetPoolFactory(testFactory,testRtWriter));
    assert(!FLProgNetworkInterface::setWiznetPoolFactory(failedFactory,testRtWriter));
    FLProgNetworkInterface automatic;
    assert(automatic.setPinRST(6) && automatic.setSpeedSPI(20000000UL));
    assert(factoryCalls==0 && rtWrites==0 && writes.empty() && spiCalls==0);
    automatic._poolEntered=1;
    assert(automatic.prepareWiznetPool() && factoryCalls==1);
    assert(automatic.hw.spiBackendKind()==FLPROG_SPI_BACKEND_RT_HW);
    assert(automatic.prepareWiznetPool() && factoryCalls==1);
    assert(automatic.hw.serviceStartup()==FLPROG_WIZNET_HW_WAIT && rtWrites==1);
    clockUs=2000; assert(automatic.hw.serviceStartup()==FLPROG_WIZNET_HW_WAIT && rtWrites==2);
    clockMs=500; assert(automatic.hw.serviceStartup()==FLPROG_WIZNET_HW_READY);
    assert(writes.size()==2 && spiCalls==0);
    FLProgNetworkInterface explicitArduino;
    explicitArduino._wiznetBackendExplicit=1;
    assert(explicitArduino.setPinRST(8)); explicitArduino._poolEntered=1;
    assert(explicitArduino.prepareWiznetPool() && factoryCalls==1);
    assert(explicitArduino.hw.spiBackendKind()==FLPROG_SPI_BACKEND_ARDUINO);
    assert(explicitArduino.hw.serviceStartup()==FLPROG_WIZNET_HW_WAIT && rtWrites==2);
    FLProgNetworkInterface::_wiznetPoolFactory=failedFactory;
    FLProgNetworkInterface exhausted; exhausted._poolEntered=1;
    assert(!exhausted.prepareWiznetPool() && exhausted._poolPreparation==2);
    FLProgNetworkInterface::_wiznetPoolFactory=nullptr;
    FLProgNetworkInterface::_wiznetPoolResetWriter=nullptr;
    puts("PASS: deferred RT_HW factory, managed RT_HW reset, explicit Arduino selection, factory failure");
#else
    FLProgNetworkInterface wifiOnly;
    assert(!wifiOnly.setPinRST(255) && !wifiOnly.setSpeedSPI(20000000UL));
    assert(wifiOnly.prepareWiznetPool() && writes.empty() && spiCalls==0);
    puts("PASS: WiFi-only API compiles and rejects Ethernet settings without hardware access");
#endif
    puts("ALL HOST SETTER CHECKS PASSED");
}
'''
source = prefix + '\n' + method(backend, 'void FLProgArduinoSpiBackend::configure(') + '\n' + '\n'.join(hw_methods) + '\n#if FLPROG_NETWORK_COMPILE_WIRED && !FLPROG_NETWORK_PROFILE_WIFI_ONLY\n' + writer + '\n#endif\n' + '\n'.join(net_methods) + '\n' + tests
cpp = work / 'setters_test.cpp'
cpp.write_text(source, encoding='utf-8')
zig = Path(args.zig)
results = []
for profile in (0, 1, 2):
    exe = work / ('profile_%d.exe' % profile)
    command = [str(zig), 'c++', '-std=c++11', '-O0', '-Wall', '-Wextra', '-I'+str(stubs), '-I'+str(library),
               '-DFLPROG_NETWORK_BUILD_PROFILE='+str(profile),
               str(cpp), str(library/'hardware/flprogSpiArbiter.cpp'), '-o', str(exe)]
    subprocess.run(command, check=True)
    result = subprocess.run([str(exe)], capture_output=True, text=True)
    print(result.stdout, end='', flush=True)
    print(result.stderr, end='', flush=True)
    assert result.returncode==0, result.returncode
    results.append(result.stdout + result.stderr)
(work/'results.txt').write_text('\n'.join(results), encoding='utf-8')
