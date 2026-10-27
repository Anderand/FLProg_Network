# EXP-2A-fix4 Interim Changes

- Keeps the closed A3 TransportIdentity/NET NUM/socket lifecycle architecture.
- Adds a Wi-Fi-only compile-time profile.
- Removes W5500/RMII/DHCP wired objects from FLProgNetworkInterface in Wi-Fi-only builds.
- Excludes wired DNS/UDP/socket backend paths from Wi-Fi-only linkage.
- Makes `dhcpMode()` Wi-Fi-only safe without Wiznet DHCP dependencies.
- Makes TCP Client Wi-Fi-only safe without `wiznetHardware()` dependency.
- Removes physical WIZnet/RMII backend fields from TCP/UDP Wi-Fi-only paths.
- Real TCP echo and reconnect tests are hardware-verified.
