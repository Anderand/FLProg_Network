# FLProg Web UI 1.0 regression record

Date: 2026-10-10.

Static verification passed for the Python generator/editor, editor JavaScript,
demo package generation, invalid slider-to-bool contract rejection, universal
blocks XML, sketchbook installation, and bounded device resources. The device
JavaScript response is 1575 bytes, below the 2048-byte HTTP response
limit; HTML, CSS and JavaScript are served separately.

The generator also rejects a project whose configuration or worst-case state
response cannot fit the bounded device buffer, before it can be flashed.

## Live ESP8266 Wi-Fi read-only check

On 2026-10-10, device `192.168.100.217` returned HTTP 200 for `/` (246 bytes),
`app.css` (477), `app.js` (1313), `config` (560; theme and three widgets) and
`state` (97; three channels). Command endpoints were deliberately not invoked,
because that could change a physical relay state.

Hardware verification remains required for ESP8266 Wi-Fi, ESP32 Wi-Fi and
W5500 Ethernet. W5500 generation uses the published
`FLPROG_WIZNET_INTERFACE1/2` identifiers and the runtime adapter uses the
public `FLProgNetworkInterface` abstraction.

ESP32 and W5500 physical checks are deferred by user decision. ESP8266 Wi-Fi
has been physically verified; W5500 packages and adapter remain statically
verified and ready for a later hardware run.

## Current ESP8266 firmware check

On 2026-10-11 after recompilation and flashing, `192.168.100.217` returned
HTTP 200 for all Web UI endpoints. Response sizes were 246 bytes for HTML,
559 CSS, 1484 JavaScript, 56 meta, 560 config and 94 state. It reported
runtime `1.0.0-20261011`, project theme `#111827`, three widgets and channels
`temperature`, `light`, `brightness`; all static resources remained under
2048 bytes.
