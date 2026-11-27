#pragma once

// Compact AVR facade for Arduino Ethernet (W5100/W5200/W5500). The full
// FLProg network stack is intentionally not pulled into ATmega328P sketches.
#if defined(ARDUINO_ARCH_AVR) && defined(__AVR_ATmega328P__)

#include <Arduino.h>
#ifndef FLPROG_NETWORK_SUCCESS
#define FLPROG_NETWORK_SUCCESS 0
#endif
#ifndef FLPROG_NETWORK_WAIT
#define FLPROG_NETWORK_WAIT 1
#endif
#ifndef FLPROG_NETWORK_ERROR
#define FLPROG_NETWORK_ERROR 2
#endif
#include <Ethernet.h>
#include <string.h>

class FLProgWiznetInterface
{
public:
    enum : uint8_t { STATUS_DISABLED=0, STATUS_IDLE=1, STATUS_CONNECTING=2, STATUS_READY=3, STATUS_RECONNECT=4, STATUS_ERROR=5 };
    enum : uint8_t { ERROR_NONE=0, ERROR_HARDWARE=3, ERROR_LINK=4, ERROR_DHCP=5, ERROR_SPI_BUS=6 };
    FLProgWiznetInterface() : _cs(10) { initDefaults(); }
    FLProgWiznetInterface(int pinCs, uint8_t bus=255) : _cs(pinCs), _bus(bus) { initDefaults(); }

    // The stock Ethernet library owns SPI; bus is retained for source compatibility only.
    uint8_t begin() { _attempted=false; _ready=false; _nextAttempt=0; return pool(); }
    uint8_t begin(IPAddress ip) { resetDhcp(); localIP(ip); return begin(); }
    uint8_t begin(IPAddress ip, IPAddress dnsIp) { resetDhcp(); localIP(ip); dns(dnsIp); return begin(); }
    uint8_t begin(IPAddress ip, IPAddress dnsIp, IPAddress gatewayIp)
    { resetDhcp(); localIP(ip); dns(dnsIp); gateway(gatewayIp); return begin(); }
    uint8_t begin(IPAddress ip, IPAddress dnsIp, IPAddress gatewayIp, IPAddress subnetIp)
    { resetDhcp(); localIP(ip); dns(dnsIp); gateway(gatewayIp); subnet(subnetIp); return begin(); }

    // pool() is the generated sketch entry point and starts the interface lazily.
    uint8_t pool()
    {
        poolStatus();
        if (_status == STATUS_READY) return FLPROG_NETWORK_SUCCESS;
        if (_status == STATUS_ERROR) return FLPROG_NETWORK_ERROR;
        return FLPROG_NETWORK_WAIT;
    }

private:
    uint8_t poolStatus()
    {
        const uint32_t now=millis();
        if (_attempted && _ready) {
            if (static_cast<uint32_t>(now-_lastLinkCheck)<LINK_POLL_MS) return _status;
            _lastLinkCheck=now;
            if (!linkAvailable()) {
                _ready = false;
                _status = STATUS_RECONNECT;
                _error = ERROR_LINK;
                _nextAttempt = now + RETRY_MS;
                _nextLinkCheck = now + LINK_POLL_MS;
                return _status;
            }
            if (_dhcp && static_cast<uint32_t>(now-_lastMaintain)>=MAINTAIN_MS) {
                _lastMaintain=now;
                int rc=Ethernet.maintain();
                if (rc==2 || rc==4) { _ip=Ethernet.localIP(); _error=ERROR_NONE; }
                else if (rc==1 || rc==3) _error=ERROR_DHCP;
                if (rc==3) {
                    Ethernet.setLocalIP(IPAddress(0,0,0,0));
                    _ip = IPAddress(0,0,0,0);
                    _ready = false;
                    _status = STATUS_RECONNECT;
                    _nextAttempt = now + RETRY_MS;
                    _nextLinkCheck = now + LINK_POLL_MS;
                    return _status;
                }
                // Ethernet.maintain reports renewal failure but may retain the
                // active lease; only clear readiness when its address is zero.
                if (_zero(Ethernet.localIP())) {
                    _ip = Ethernet.localIP();
                    _ready=false;
                    _status=STATUS_RECONNECT;
                    _error=ERROR_DHCP;
                    _nextAttempt=now+RETRY_MS;
                    _nextLinkCheck=now+LINK_POLL_MS;
                }
            }
            return _status;
        }
        if (_attempted && !_ready) {
            if (_hardwarePresent) {
                if (static_cast<int32_t>(now-_nextLinkCheck)<0) return _status;
                _lastLinkCheck=now;
                _nextLinkCheck=now+LINK_POLL_MS;
                if (!linkAvailable()) {
                    _status=STATUS_RECONNECT;
                    _error=ERROR_LINK;
                    return _status;
                }
            }
            if (static_cast<int32_t>(now-_nextAttempt)<0) return _status;
        }
        return startAddressing(now);
    }

public:
    void dhcpMode(bool v) { if (_dhcp!=v) { _dhcp=v; resetRuntime(); } }
    bool isDhcp() const { return _dhcp; }
    void setDhcp() { dhcpMode(true); }
    void setDhcp(bool v) { dhcpMode(v); }
    void resetDhcp() { dhcpMode(false); }
    void localIP(IPAddress v) { _ip=v; _configured=true; }
    void localIP(uint32_t v) { localIP(IPAddress(v)); }
    void localIP(uint8_t a,uint8_t b,uint8_t c,uint8_t d) { localIP(IPAddress(a,b,c,d)); }
    IPAddress localIP() const
    {
        if (_ready) return Ethernet.localIP();
        return _dhcp ? IPAddress(0, 0, 0, 0) : _ip;
    }
    void dns(IPAddress v) { _dns=v; }
    void dns(uint32_t v) { dns(IPAddress(v)); }
    void dns(uint8_t a,uint8_t b,uint8_t c,uint8_t d) { dns(IPAddress(a,b,c,d)); }
    IPAddress dns() const { return _ready ? Ethernet.dnsServerIP() : _dns; }
    void gateway(IPAddress v) { _gateway=v; }
    void gateway(uint32_t v) { gateway(IPAddress(v)); }
    void gateway(uint8_t a,uint8_t b,uint8_t c,uint8_t d) { gateway(IPAddress(a,b,c,d)); }
    IPAddress gateway() const { return _ready ? Ethernet.gatewayIP() : _gateway; }
    void subnet(IPAddress v) { _subnet=v; }
    void subnet(uint32_t v) { subnet(IPAddress(v)); }
    void subnet(uint8_t a,uint8_t b,uint8_t c,uint8_t d) { subnet(IPAddress(a,b,c,d)); }
    IPAddress subnet() const { return _ready ? Ethernet.subnetMask() : _subnet; }
    void mac(const uint8_t *v) { if(v) memcpy(_mac,v,6); }
    void mac(uint8_t a,uint8_t b,uint8_t c,uint8_t d,uint8_t e,uint8_t f)
    { _mac[0]=a;_mac[1]=b;_mac[2]=c;_mac[3]=d;_mac[4]=e;_mac[5]=f; }
    uint8_t *mac() { return _mac; }
    const uint8_t *mac() const { return _mac; }
    void macAddress(const uint8_t *v) { mac(v); }
    const uint8_t *macAddress() const { return _mac; }
    void setSkippingEvents(uint16_t v) { _skippingEvents=v; }
    uint16_t getSkippingEvents() const { return _skippingEvents; }

    bool isReady() const { return _ready; }
    bool isReadyForDNS() const { return _ready; }
    bool ethernetIsReady() const { return _ready; }
    bool wiznetIsReady() const { return _ready; }
    uint8_t getStatus() const { return _status; }
    uint8_t getError() const { return _error; }
    uint8_t status() const { return _status; }
    uint8_t error() const { return _error; }
    bool hasError() const { return _error!=ERROR_NONE; }
    bool isConnecting() const { return _status==STATUS_CONNECTING||_status==STATUS_RECONNECT; }
    bool isInit() const { return _attempted; }
    bool isImitation() const { return false; }
    uint8_t hardwareStatus() const
    {
        return _hardwarePresent
            ? static_cast<uint8_t>(Ethernet.hardwareStatus())
            : static_cast<uint8_t>(EthernetNoHardware);
    }
    uint8_t linkStatus() const
    { return _hardwarePresent ? static_cast<uint8_t>(Ethernet.linkStatus()) : static_cast<uint8_t>(Unknown); }
    uint8_t maxSoketNum() const { return 4; }
    uint8_t maxSocketNum() const { return 4; }

private:
    static const uint32_t RETRY_MS = 15000UL;
    static const uint32_t MAINTAIN_MS = 1000UL;
    static const uint32_t LINK_POLL_MS = 1000UL;
    int _cs;
    uint8_t _bus=255, _mac[6];
    IPAddress _ip,_dns,_gateway,_subnet;
    uint32_t _nextAttempt=0,_lastMaintain=0;
    uint8_t _status=STATUS_IDLE,_error=ERROR_NONE;
    uint16_t _skippingEvents=0;
    bool _dhcp=true,_configured=false,_attempted=false,_ready=false,_hardwarePresent=false;
    uint32_t _lastLinkCheck=0,_nextLinkCheck=0;
    void initDefaults()
    { memset(_mac,0,sizeof(_mac)); _ip=IPAddress(0,0,0,0);_dns=IPAddress(0,0,0,0);_gateway=IPAddress(0,0,0,0);_subnet=IPAddress(255,255,255,0); }
    static bool _zero(const IPAddress &v) { return !v[0]&&!v[1]&&!v[2]&&!v[3]; }
    bool linkAvailable() const { return Ethernet.linkStatus()!=LinkOFF; }
    void resetRuntime() { _attempted=false;_ready=false;_hardwarePresent=false;_status=STATUS_IDLE;_error=ERROR_NONE; }
    uint8_t startAddressing(uint32_t now)
    {
        _status = STATUS_CONNECTING;
        _error = ERROR_NONE;
        if ((_bus!=0 && _bus!=255) || _cs<0 || _cs>=20) {
            _attempted = true;
            _ready = false;
            _status = STATUS_ERROR;
            _error = ERROR_SPI_BUS;
            _nextAttempt = now + RETRY_MS;
            return _status;
        }
        ensureDefaultMac();
        _ready = false;
        _hardwarePresent = false;
        Ethernet.init(static_cast<uint8_t>(_cs));
        int ok = 1;
        if (_dhcp) ok = Ethernet.begin(_mac, 1000UL, 250UL);
        else {
            if (!_configured || _zero(_ip)) {
                _attempted = true;
                _status = STATUS_ERROR;
                _error = ERROR_DHCP;
                _nextAttempt = now + RETRY_MS;
                return _status;
            }
            IPAddress gw = _gateway;
            IPAddress dnsIp = _dns;
            if (_zero(gw)) { gw = _ip; gw[3] = 1; }
            if (_zero(dnsIp)) dnsIp = gw;
            _gateway = gw;
            _dns = dnsIp;
            Ethernet.begin(_mac, _ip, dnsIp, gw, _subnet);
        }
        // Probe only after the stock library has initialized W5100 and set CS.
        _hardwarePresent=Ethernet.hardwareStatus()!=EthernetNoHardware;
        _attempted = true;
        _lastMaintain = millis();
        _lastLinkCheck = _lastMaintain;
        _nextLinkCheck = _lastMaintain + LINK_POLL_MS;
        if (!_hardwarePresent) {
            _ready = false;
            _status = STATUS_ERROR;
            _error = ERROR_HARDWARE;
            _nextAttempt = millis() + RETRY_MS;
            return _status;
        }
        // Link status is reliable only after the hardware probe above. On a
        // cold start DHCP itself is the initial carrier/device probe.
        if (!linkAvailable()) {
            _ready = false;
            _status = STATUS_RECONNECT;
            _error = ERROR_LINK;
            _nextAttempt = millis() + RETRY_MS;
            return _status;
        }
        if (!ok || _zero(Ethernet.localIP())) {
            _ready = false;
            _status = STATUS_ERROR;
            _error = ERROR_DHCP;
            _nextAttempt = millis() + RETRY_MS;
            return _status;
        }
        _ip = Ethernet.localIP();
        _ready = true;
        _status = STATUS_READY;
        _error = ERROR_NONE;
        return _status;
    }
    void ensureDefaultMac()
    {
        if(!_zeroMac()) return;
        const uint32_t seed=micros();
        _mac[0]=0x02; _mac[1]=0x46; _mac[2]=0x4C;
        _mac[3]=static_cast<uint8_t>(seed>>16); _mac[4]=static_cast<uint8_t>(seed>>8); _mac[5]=static_cast<uint8_t>(seed)^0x01;
    }
    bool _zeroMac() const { return !(_mac[0]|_mac[1]|_mac[2]|_mac[3]|_mac[4]|_mac[5]); }
};

#endif // AVR ATmega328P
