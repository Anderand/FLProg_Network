# FLProg Web UI — universal blocks

The package contains eight FLProg user blocks:

* Publish Bool / Int / Float / Text;
* Command Bool / Int / Float / Text.

`CHANNEL` is the numeric index in the generated project descriptor. The index
does not change when labels, colours, pages or widget positions change.

Publish blocks have `EN`, `CHANNEL`, `VALUE` inputs. Command blocks have `EN`,
`CHANNEL` inputs and `NEW`, `VALUE` outputs. `NEW` is true for exactly one
FLProg loop when a browser command has arrived.

Import `FLProg_WebUI_Universal_Blocks.ubl` once to add the whole set into the
single **FLProg Web UI** folder. Individual `.ubi` files are retained for
diagnostics and selective import.
