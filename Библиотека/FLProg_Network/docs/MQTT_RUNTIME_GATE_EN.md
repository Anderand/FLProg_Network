# MQTT runtime gate

## Goal

Confirm on a real ESP8266 or ESP32 that `FLProgNetworkMqttClient` works over
the standard `FLProgNetworkInterface`, without direct WiFiClient/EthernetClient
access and without blocking `loop()`.

## Example

Use `examples/MQTT_Runtime_Gate_EN` or its Russian equivalent. Enter local
Wi-Fi, broker, port and optional credential values. Do not save them in the
library.

## Minimum test bench

- An MQTT 3.1.1 broker reachable from the test board, normally TCP `1883`.
- A PC with two broker clients, or one client that can subscribe and publish.
- ESP8266/ESP32 on the same network. Run the first gate through Wi-Fi STA.

Mosquitto CLI example:

```text
mosquitto_sub -h <broker> -t flprog/network/gate/out -v
mosquitto_pub -h <broker> -t flprog/network/gate/in -m test
```

## PASS

1. `connectSuccessCount() >= 1`, `connected() == true`, `error() == 0`.
2. The example subscribes to `flprog/network/gate/in`.
3. Publishing `test` produces `MQTT RX` on Serial and `echo` on
   `flprog/network/gate/out`.
4. `alive` arrives every 15 seconds.
5. After a brief broker or Wi-Fi loss, the client enters backoff and restores
   the connection/subscription without an MCU reset.

## Actual bench result

On 2026-09-28, the gate passed on an ESP through Wi-Fi STA and a local MQTT
3.1.1 broker at `192.168.100.7:1883`. The test confirmed `WiFiReady=1`, an
MQTT connection, `connectSuccessCount()=1`, a successful subscription, and
the `self-test` loopback: `MQTT RX topic=flprog/network/gate/in
payload=self-test`. Once the queue was processed, `error()=0` and
`messages=1`. Reconnect-after-loss, TLS, W5500/RMII, and soak testing remain
outside this gate.

## Failure diagnostics

Record `state()`, `error()`, `connackCode()`, `tcpClientError()`, `dnsError()`,
`connectAttemptCount()`, `connectSuccessCount()`, `reconnectScheduleCount()`,
`protocolErrorCount()` and `oversizedPacketCount()`. Separate DNS, broker
credentials, routing and application MQTT semantics before changing the library.

## Gate boundary

This is a native service gate, not a future visual FLProg MQTT-block test.
Baseline subscription QoS is fixed at 0. TLS, W5500/RMII MQTT and a
multi-client broker soak are not declared PASS by this scenario.
