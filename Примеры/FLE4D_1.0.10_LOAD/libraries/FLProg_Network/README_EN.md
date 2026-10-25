# FLProg_Network dev.17-pr28

Release snapshot date: 2026-09-27.

The library provides a common transport/network-manager layer for generated
FLProg projects with Wi-Fi STA/AP, W5500 and RMII. API level: `10006`.

## Hardware-verified on ESP8266

- NET NUM / Device Registry — PASS.
- TransportIdentity — PASS.
- A1 + A2 Wi-Fi DHCP — PASS.
- TCP Client over Wi-Fi — PASS.
- TCP echo TX/RX — PASS.
- TCP echo-server loss and reconnect — PASS.
- Shared HTTP works concurrently through Wi-Fi STA and two W5500 interfaces.
- Wi-Fi OTA uses a compatibility facade over `FLProgNetworkOta`.

## Important limitation

OTA is implemented only through Wi-Fi STA. With the one-context legacy shared
HTTP server, a burst request during the W5500 LISTEN reopen window may be
rejected; this is the documented sequential-processing limit.

## Verified result

ESP8266: HTTP `200` on Wi-Fi `.217` and W5500 `.218`/`.219`; OTA upload and
the subsequent regression passed. ESP32 and RP2040 PR28 compile successfully.
Details are in `docs/CURRENT_RELEASE_STATUS_RU.md`.

## Source comments

Every `.h/.cpp` file in `src` and each executable example carries extended
Russian and English comments. The maintenance rule is documented in
`docs/COMMENTING_STANDARD_RU_EN.md`.
