# FLProg_Network dev.16-fix33 — исторический статус

Promotion date: 2026-09-26
Decision: promoted to current main after the FIX33 Web/AP hardware regression on ESP8266.

## Confirmed on hardware

- Generated Web interface on TCP port 80 through Wi-Fi STA (192.168.100.217): PASS.
- Generated Web interface on TCP port 80 through W5500 (192.168.100.218): PASS.
- STA and W5500 responses matched before and after the runtime AP cycle: PASS.
- Generated Web interface on TCP port 80 through Wi-Fi SoftAP (192.168.4.1): PASS, confirmed from a phone connected to SSID 123333.
- Runtime SoftAP OFF/ON without ESP8266 restart, followed by Web access through SoftAP: PASS.
- After runtime AP OFF/ON, STA and W5500 Web interface remained reachable and byte-identical: PASS.

## Not included in this promotion run

- Modbus TCP Slave: intentionally not tested.
- KaScada over W5500 with Pause=1 ms: intentionally not tested.

These items are not reported as PASS and require separate verification if their behavior is changed in later work.
