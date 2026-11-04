#pragma once

// Included by the legacy umbrella after both RT_HW_BASE and FLProg_Network.
// The adapter is owned by its interface: two controllers never share CS/state.
class FLProgRtHwSpiOwner
{
protected:
    FLProgRtHwSpiOwner() : _rtHwSpi(RT_HW_Base) {}
    FLProgRtHwSpiBackend<decltype(RT_HW_Base), RT_HW_STRUCT_SPI_DEV> _rtHwSpi;
};

// Base classes are destroyed in reverse order: the SPI adapter must outlive
// FLProgNetworkInterface's DHCP/socket cleanup.
class FLProgRtHwWiznetInterface
    : private FLProgRtHwSpiOwner, public FLProgWiznetInterface
{
public:
    FLProgRtHwWiznetInterface()
    {
        setWiznetSpiBackend(&_rtHwSpi);
    }

    FLProgRtHwWiznetInterface(int pinCs, uint8_t bus = 255)
        : FLProgWiznetInterface(pinCs, bus)
    {
        setWiznetSpiBackend(&_rtHwSpi);
    }

    FLProgRtHwWiznetInterface(const FLProgRtHwWiznetInterface &) = delete;
    FLProgRtHwWiznetInterface &operator=(const FLProgRtHwWiznetInterface &) = delete;

};

// Keep this selection at the legacy sketch boundary. The compiled core keeps
// the original FLProgWiznetInterface type and does not acquire an RT_HW dependency.
#define FLProgWiznetInterface FLProgRtHwWiznetInterface
