#pragma once
#include <flprogNetwork.h>

// Build-time compression only. Keep 0 for clients requiring identity encoding.
#ifndef FLPROG_WEBUI_GZIP_ASSETS
#define FLPROG_WEBUI_GZIP_ASSETS 0
#endif

inline bool flprogWebUiGzipAllowed(const String &header)
{
    // No Accept-Encoding means any coding is acceptable (HTTP semantics).
    if (!header.length()) return true;
    String value = header; value.toLowerCase();
    bool wildcard = false, found = false, gzip = false;
    unsigned start = 0;
    while (start < value.length()) {
        int end = value.indexOf(',', start); if (end < 0) end = value.length();
        String token = value.substring(start, end); token.trim();
        int semicolon = token.indexOf(';');
        String coding = semicolon < 0 ? token : token.substring(0, semicolon); coding.trim();
        bool quality = true;
        if (semicolon >= 0) {
            String parameter = token.substring(semicolon + 1); parameter.trim();
            quality = false;
            if (parameter.startsWith("q=")) {
                const char *q = parameter.c_str() + 2;
                if (*q == '0' || *q == '1') {
                    const bool one = *q++ == '1';
                    bool valid = true, nonzero = one;
                    if (*q) {
                        if (*q++ != '.') valid = false;
                        unsigned digits = 0;
                        for (; *q; ++q) {
                            if (*q < '0' || *q > '9' || ++digits > 3 || (one && *q != '0')) valid = false;
                            if (*q >= '1' && *q <= '9') nonzero = true;
                        }
                    }
                    quality = valid && nonzero;
                }
            }
        }
        if (coding == "gzip") { found = true; gzip = quality; }
        if (coding == "*") wildcard = quality;
        start = end + 1;
    }
    return found ? gzip : wildcard;
}

inline void flprogWebUiSendGzip(FLProgNetworkHttpServer *server, const char *type,
                               const unsigned char *data, size_t size)
{
    if (!flprogWebUiGzipAllowed(server->headerValueAtKey("Accept-Encoding"))) {
        server->print("HTTP/1.1 406 Not Acceptable\r\nContent-Type: text/plain\r\nContent-Length: 24\r\nVary: Accept-Encoding\r\nConnection: close\r\n\r\n");
        if (server->method() != FLPROG_WEB_SERVER_HEAD) server->print("This UI requires gzip.\r\n");
        return;
    }
#if defined(FLPROG_HTTP_SERVER_HAS_FLASH_STREAM)
    server->sendStreamProgmem(200, type, data, size, "gzip");
    return;
#endif
    server->print("HTTP/1.1 200 OK\r\nContent-Type: "); server->print(type);
    server->print("\r\nContent-Encoding: gzip\r\nVary: Accept-Encoding\r\nContent-Length: ");
    server->print((unsigned long)size); server->print("\r\nConnection: close\r\n\r\n");
    if (server->method() == FLPROG_WEB_SERVER_HEAD) return;
    for (size_t i = 0; i < size; ++i) {
#if defined(ESP8266)
        server->write((uint8_t)pgm_read_byte(data + i));
#else
        server->write((uint8_t)data[i]);
#endif
    }
}
