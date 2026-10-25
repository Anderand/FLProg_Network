# FLProg Web UI 1.0

FLProg Web UI is a separate built-in Web UI constructor for FLProg.
`FLProg_Network` stays a clean transport library: a project stores its design
in a `.flpui` document and receives its own
`FLProg_WebUI_Project_<id>` package.

## Contents

* `runtime/FLProg_WebUI` — shared runtime, installed once.
* `editor/` — local editor. Run `python server.py` and open
  `http://127.0.0.1:8766`.
* `projects/` — per-project designs.
* `project_packages/` — generated packages, outside `FLProg_Network`.
* `user_blocks/FLProg_WebUI_Universal_Blocks.ubl` — one importable Publish /
  Command set for Bool, Int32, Float and Text.

## Workflow

1. Create channels and widgets in the editor.
2. Save the `.flpui` design.
3. Use **Build and install** to install a separate project package.
4. Import the package configurator `.ubi` into the FLProg diagram together
   with the ordinary FLProg Wi-Fi interface. On the first migration to runtime
   1.2, replace the previous configurator with this block; it enables paged
   HTTP transport.
5. Import the universal `.ubl`, connect the channels, compile and flash.

Changing layout, theme, position and labels does not alter the FBD contract.
Changing the channel list does.

Move a card by its `⠿` handle, resize it with the `W/H` buttons or exact
`X/Y/W/H` fields. The editor marks overlapping cards with an amber border and
lists their numbers, and provides Duplicate plus Undo (the latest 40 changes).
These operations modify only the `.flpui` design.

The editor displays `№N` / `INDEX = N` for every channel. This is the exact
zero-based `CHANNEL` parameter used by the universal FLProg blocks and is also
shown in the widget channel selector.

## Paged HTTP

`FLProg_Network` deliberately bounds a single HTTP response. Runtime 1.2 does
not raise that limit or allocate heap memory. The browser fetches metadata
once, each widget descriptor separately, and reads channels only for the open
page while polling. Therefore aggregate layout/config size no longer limits
the number of widgets and pages.

The Web UI work buffer is 1024 bytes; one widget property is limited to 180
bytes. `GET /flprog-webui/meta` reports runtime `1.2.0-20261011`.
