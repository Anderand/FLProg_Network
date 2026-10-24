# SUPERSEDED BY dev.16-fix33 on 2026-09-26

# FLProg_Network dev.16-fix32 — исторический статус

Promotion date: 2026-09-24
Decision: promoted to current main by user after the completed Web/AP hardware regression on ESP8266.

## Confirmed on hardware

- Generated Web interface on TCP port 80 through Wi-Fi STA (192.168.100.217): PASS.
- Generated Web interface on TCP port 80 through W5500 (192.168.100.218): PASS.
- The STA and W5500 HTTP responses were byte-identical (4052 bytes; SHA-256 556CAF9925192C49C7EE859BD5EE528870822A91B0A96A88D37D8BF60BE88EA0): PASS.
- Generated Web interface on TCP port 80 through Wi-Fi SoftAP (192.168.4.1): PASS, confirmed from a phone connected to SSID 123333.
- Runtime SoftAP OFF/ON without ESP8266 restart, followed by Web access through SoftAP: PASS.
- After runtime AP OFF/ON, STA and W5500 Web interface remained reachable and byte-identical: PASS.

## Not included in this promotion run

- Modbus TCP Slave: intentionally not tested.
- KaScada over W5500 with Pause=1 ms: intentionally not tested.

These items are not reported as PASS and require separate verification if their behavior is changed in later work.
