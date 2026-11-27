# AVR-lite test fixtures

`GeneratedTemplateSmoke` captures the generated FLProg one-device DHCP pattern: `flprog::specialSetup()`, MAC, `setSkippingEvents(0)`, `setDhcp()`, registry, and `wiz.pool()` without `begin()`. It includes `Flprog_Utilites` to measure the real generated sketch overhead.

`StaticSocketSmoke` configures a static IPv4 address through `FLProgWiznetInterface`, then exercises Arduino Ethernet TCP server/client and UDP receive/echo APIs against the same Ethernet controller. The compact profile keeps the network interface; the socket API comes from the stock Arduino Ethernet library.

`fake/src/avr_lite_fake_test.cpp` runs deterministic host-side checks for cold-start probing, explicit SPI bus 0, absent hardware retry, link flap backoff, DHCP retry, and DHCP maintain renewal/rebind status behavior. Its fake `Ethernet.init()` only selects CS; `begin()`/`linkStatus()` perform the simulated W5100 probe.

## Arduino CLI builds

Pass both the source library and F985's IDE libraries. The CLI config's sketchbook search alone does not find `ideV8/libraries/Ethernet`.

```powershell
.\build_acceptance.ps1 `
  -ArduinoCliPath 'C:\f985\FLProg\bin\Arduino_Cli\tools\arduino-cli\arduino-cli.exe' `
  -ConfigFile 'C:\f985\FLProg\bin\Arduino_Cli\config\arduino-cli.json' `
  -LibraryPath 'E:\path\to\Библиотека\FLProg_Network' `
  -IdeLibrariesPath 'C:\f985\FLProg\ideV8\libraries' `
  -BuildRoot 'E:\tmp\avr_lite_builds'
```

The script builds both fixtures for Uno, Nano ATmega328P (old bootloader), and Mega control. For the legacy acceptance sketch, build `MegaWiznetSmoke.ino` with the same CLI arguments and the matching FQBN.

## Host fake

From a Visual Studio x64 developer prompt, compile `fake/src/avr_lite_fake_test.cpp` with `/DARDUINO_ARCH_AVR /DARDUINO_AVR_UNO /D__AVR_ATmega328P__`, include `fake/include` before `src`, then run the output executable. It needs no Ethernet hardware.

