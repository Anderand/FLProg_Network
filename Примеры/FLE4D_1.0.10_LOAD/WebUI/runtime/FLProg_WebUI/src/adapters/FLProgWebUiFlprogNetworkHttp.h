/*
 * Compatibility include for configurator blocks generated before runtime 1.4.
 *
 * The old adapter assembled the whole configuration and state in one HTTP
 * response. That approach is not reliable on ESP8266 or the compact
 * FLProg_Network HTTP queue. Existing projects keep their include and class
 * name, but now use the bounded paged transport.
 */
#pragma once

#include "FLProgWebUiFlprogNetworkPagedHttp.h"

using FLProgWebUiFlprogNetworkHttp = FLProgWebUiFlprogNetworkPagedHttp;
