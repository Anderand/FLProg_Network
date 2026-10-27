PASS chunks=1
PASS chunks=510
PASS chunks=511
PASS chunks=4096
PASS chunk extensions and trailers
PASS oversized trailers rejected
PASS oversized chunk-size line rejected
PASS invalid data terminator rejected
PASS overflowing chunk length rejected
PASS HTTP write grace window
PASS HTTP stalled write closes at deadline
PASS HTTP timeout reported once
PASS HTTP write progress renews timeout
PASS HTTP explicit disabled timeout preserved
PASS HTTP timeout survives millis rollover
PASS 408 response gets fresh send window
PASS completed response closes normally even after a delayed pool
PASS MQTT pending ACK before deadline
PASS MQTT PUBLISH cannot extend ACK deadline
PASS MQTT pending ACK before deadline
PASS MQTT PUBLISH cannot extend ACK deadline
PASS MQTT pending ACK before deadline
PASS MQTT PUBLISH cannot extend ACK deadline
PASS valid PINGRESP completes wait
PASS MQTT ACK timeout survives millis rollover
PASS MQTT explicit disabled timeout preserved
26 checks, 0 failures
