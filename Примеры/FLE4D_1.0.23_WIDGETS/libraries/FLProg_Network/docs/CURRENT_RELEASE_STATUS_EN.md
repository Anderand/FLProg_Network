# Current release status - dev.17-pr28

Date: 2026-09-28. This file is the current English release status.

## Identity

- Library: `FLProg_Network`.
- Version: `1.0.0-rc.6a.dev.17-pr28`.
- High-level API: `10006`, unchanged.
- Scope: one transport/network-manager layer for generated FLProg projects
  using Wi-Fi STA/AP, W5500 and RMII.

## Verified results

| Gate | Result |
|---|---|
| ESP8266 PR26 HTTP | PASS: HTTP `200`, 4170 bytes through Wi-Fi `.217` and W5500 `.218`/`.219`. |
| ESP8266 PR26 W5500 | PASS: paced TCP regression 10/10 on each W5500. |
| ESP8266 PR26 OTA | PASS: discovery, OTA upload and post-upload HTTP/W5500 regression. |
| ESP8266 memory | 4008 bytes free heap with OTA enabled; SoftAP was excluded only from this measurement configuration. |
| ESP MQTT runtime gate | PASS on 2026-09-28: Wi-Fi STA, local broker, subscribe and `self-test` loopback; `connectSuccess=1`, `messages=1`, final `error=0`. |
| ESP32 PR28 | Compile PASS: Flash 87%, RAM 24%. |
| RP2040 PR28 | Compile PASS: Flash 19%, RAM 36%. |

## Architecture decision

Legacy `FLProgOTA` preserves the generated API without manual `.ino` edits,
but delegates to `FLProgNetworkOta`. ArduinoOTA calls remain in the service
layer. The facade waits for a ready Wi-Fi STA and binds lazily to the matching
`FLProgNetworkInterface`, which also supports projects that construct W5500
objects before the Wi-Fi object.

Services remain in one library for generated-project compatibility. They do
not form a separate FLProg_Network_Services package.

## Release boundaries

- OTA is available only through Wi-Fi STA. W5500/RMII OTA is not implemented.
- The default legacy shared HTTP context handles one client sequentially. A
  burst request can be rejected during the W5500 LISTEN reopen interval.
- Generated `FLPROG_WEB_INTERFACE_SERVER` redefinition and deprecated
  `BluetoothSerial` warnings belong to the generator/Flprog_Utilites, not to
  FLProg_Network.

## Bilingual comment coverage

On 2026-09-28, all 64 `src/**/*.h` and `src/**/*.cpp` files and both executable
examples received extended Russian and English maintenance comments. The clean
RU and EN distribution archives retain their respective language only.
