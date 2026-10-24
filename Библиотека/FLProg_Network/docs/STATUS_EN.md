# Status — superseded

The current release status is `CURRENT_RELEASE_STATUS_RU.md` (dev.17-pr28).

# Historical RC6-A EXP-2A-fix4 Status

## Baseline
- A3 FINAL is fully closed.
- Current experimental branch: EXP-2A-fix4.
- Current hardware test platform: ESP8266, core 3.1.2.

## Passed
- A1 / NET NUM / registry: PASS.
- A2 Wi-Fi DHCP: PASS.
- TCP begin/connect: PASS.
- Echo TX/RX: PASS.
- TCP server stop -> disconnect: PASS.
- TCP server return -> reconnect: PASS.
- Wi-Fi transport identity: kind=1, instance=0.
- Generation during the live TCP connection: G=2.

## Latest reconnect test
Before server stop: C=1, S=4, TX/RX increase, OC=1.
After server stop: C=0, S=0, Wi-Fi remains W=1, TX/RX stop.
After server restart: C=1, S=4, TX/RX resume, OC=2.

## Current limitations
- W5500/RMII are compile-time disabled.
- Full wired regression has not yet been repeated after optimization.
- Services are now intentionally kept in the single FLProg_Network library.
- Wi-Fi AP loss/recovery gate is still pending.
