#pragma once
using FLProgNetworkDeviceId=unsigned char;
struct Registry{FLProgNetworkInterface*getDevice(FLProgNetworkDeviceId){return nullptr;}};
static Registry flprogNetworkDevices;
