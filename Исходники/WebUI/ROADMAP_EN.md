# FLProg Web UI 1.0 roadmap

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
