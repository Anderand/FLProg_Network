# COMPAT FIX1 SKIPPING EVENTS

FLProg_Network RC6-A dev.14-fix1 — legacy setSkippingEvents compatibility

Change:
- FLProgNetworkInterface now exposes:
    void setSkippingEvents(uint16_t value)
    uint16_t getSkippingEvents() const
- Restores the public method inherited by old FLProgOnBoardWifiInterface and
  FLProgWiznetInterface from FLProgAbstractTcpInterface.
- The value is stored for source/observable-state compatibility.
- No scheduler/pool throttling behavior is added in this fix.

Why this is correct for the reported old WiFi example:
- Old FLProgOnBoardWifiInterface inherited the property, but its pool() did not
  use _skippingEvents.
- The generated example calls setSkippingEvents(0), so runtime behavior is unchanged.

Important:
- Old FLProgWiznetInterface DID use skippingEvents to throttle pool(). That
  semantic behavior remains a separate compatibility item and should be tested.
