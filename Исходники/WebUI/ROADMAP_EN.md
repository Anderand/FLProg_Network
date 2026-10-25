# FLProg Web UI 1.0 roadmap

## Current status — 2026-10-25

Command notifications were implemented and tested on FLE4D firmware
1.0.9-NOTICES: dispatched, accepted, then confirmed by fresh state/result;
errors and cancellation are separate. Old result=true is not reused as
confirmation. The 26 tests include timeout/reconnect/reset behavior.
See [the report](NOTIFICATIONS_RU.md). Release r10 and Git remain unchanged.

The [Russian roadmap](ROADMAP_RU.md) now contains the complete idea/status
matrix recovered from the [original K-WEB review](specification/KWEB_REVIEW_RU.md).
It distinguishes completed work, planned remainders and deferred experiments,
including partial field/container support, Flash streaming, notifications,
navigation recovery, persistence, diagnostics, SSE and administration.
Gzip has now been tested on FLE4D; the additional editor ideas are kept separate.

Local release r8 includes project validation with widget navigation, offline
preview, channel editing, connection loss/recovery, restart, busy/result and
a one-click demo. It passes 24 automated tests. Firmware 1.0.7 was tested on
FLE4D-30MT / STM32F407VG / W5500. The historical checklist below predates it.

Optional gzip assets were implemented and tested on FLE4D on 2026-10-25:
Flash 137040→130856 bytes, static RAM 16112→16112 bytes; all 15 resources
were verified on the controller. See [the gzip report](GZIP_RU.md).
Release r9 contains gzip. Flash streaming was subsequently implemented and
tested on FLE4D: 128 KiB, slow reading, aborts and stalled peer recovery;
static RAM and HTTP context size are unchanged. See [the report](FLASH_STREAM_RU.md).
Streaming is not packaged into a new general release yet.
The original gzip checklist was to measure raw/compressed assets and final firmware Flash/RAM,
support binary Flash responses with explicit lengths and Content-Encoding,
handle Accept-Encoding and clients without gzip, preserve the 2048-byte HTTP
response budget and route budget, verify decompression and test on FLE4D.
Compress assets on the computer rather than at runtime on the MCU.

Saved simulation scenarios, multi-widget layout tools and a channel-contract
report remain unprioritized ideas. See [the current Russian roadmap](ROADMAP_RU.md).
GitHub updates require a separate user instruction; existing release r8 is unchanged.

## Architecture rules

* `FLProg_Network` contains only the developer-owned network API.
* `FLProg_WebUI` contains the shared runtime and adapters.
* A `.flpui` file belongs to one user project and stores its design contract.
* A generated project package contains only that project's descriptor and
  configurator.
* Changing layout/theme does not change the FBD diagram; changing channels
  changes the contract.

## Delivery status

1. Public API integration: complete for Wi-Fi and W5500 HTTP.
2. Design model: complete — theme, grid, X/Y/W/H, colours, icons and ranges.
3. Editor: complete — 12-column layout, properties, colour picker, drag,
   precise dimensions, text input, phone preview, overlap highlighting,
   duplication and undo.
4. Device runtime: complete — descriptors, bounded split HTTP resources,
   indicator/switch/slider/text input and command queue.
5. FLProg blocks: complete — one UBL library plus individual UBI blocks.
6. Build/install: complete — package generator and sketchbook installation.
7. Static regression: complete; hardware flashing remains in the matrix.
8. Handoff: complete — RU/EN documentation, examples and clean archive.

## Hardware matrix still requiring physical proof

* ESP8266 through Wi-Fi;
* ESP32 through Wi-Fi — deferred by user decision;
* W5500 through `FLPROG_WIZNET_INTERFACE1/2` — deferred by user decision.

Use `REGRESSION_RU.md` for the exact physical-test sequence.
