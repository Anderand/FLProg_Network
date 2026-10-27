# MQTT user blocks v0.1

Import the three .ubi files into FLProg. Copy flprogMqttUserBlocks.h into
the installed FLProg_Network/src directory (already installed on this PC).
Requires the existing Network Core defining flpNetwork and calling its pool(),
plus configured WiFi A2. Exactly one MQTT Core; multiple Publish/Subscribe blocks.

Core EN starts automatically. CON/DIS use rising edges; DIS takes priority.
Broker, Port, ClientID, User and Password are applied on enable or CON.
Port 0 defaults to 1883. Empty User selects anonymous access.
After Connected, trigger Subscribe; later trigger Send to publish.
Accepted means local acceptance, not confirmed broker delivery. Retry a command
with a new edge if ERR=1 (BUSY). Received pulses once; Message/RxTopic retain data.
Supports +/# filters, four subscriptions by default, MQTT 3.1.1 QoS0, no TLS.
The receive buffer holds only the latest text message per network scan; bursts
may overwrite earlier messages. WQTT plain TCP exposes credentials in transit.

Validated XML, unique IDs and reference resolution. FLProg import/code generation,
compilation and hardware operation of these blocks are not yet verified.
The earlier hardware test covered a separate native MQTT sketch. This v0.1
package is ready for import and generation testing.
