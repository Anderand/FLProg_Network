#pragma once
#include "FLProgWebUiGzipHttp.h"

// Generated catalogs are constant Flash data, with no per-instance pointers
// or whole-catalog RAM buffer. Unversioned project layouts must not be cached.
#if defined(FLPROG_HTTP_SERVER_HAS_FLASH_STREAM)
inline void flprogWebUiSendWidgetCatalog(FLProgNetworkHttpServer *server,
    const void *data, size_t size, bool gzip)
{
    if (gzip && !flprogWebUiGzipAllowed(server->headerValueAtKey("Accept-Encoding"))) {
        server->send(406, "text/plain", "This catalog requires gzip.");
        return;
    }
#if defined(FLPROG_HTTP_SERVER_HAS_CACHE_POLICY)
    server->sendStreamProgmem(200, "application/json", data, size, gzip ? "gzip" : nullptr, false);
#else
    server->sendStreamProgmem(200, "application/json", data, size, gzip ? "gzip" : nullptr);
#endif
}
#endif
