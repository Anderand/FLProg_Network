/* ESP8266 transport for FLProg_WebUI.
 * Optional: include only in an ESP8266 sketch that already owns Wi-Fi. */
#pragma once

#if defined(ESP8266)
#include <ESP8266WebServer.h>
#include "../FLProgWebUiHttpProtocol.h"

#ifndef FLPROG_WEBUI_HTTP_BUFFER_SIZE
#define FLPROG_WEBUI_HTTP_BUFFER_SIZE 768
#endif

class FLProgWebUiEsp8266Http {
public:
    explicit FLProgWebUiEsp8266Http(FLProgWebUiModel &model) : _api(model), _server(nullptr) {}

    // Does not start Wi-Fi. The caller owns Wi-Fi credentials and lifecycle.
    void begin(ESP8266WebServer &server) {
        _server = &server;
        _server->on("/", HTTP_GET, [this]() { index(); });
        _server->on("/flprog-webui/state", HTTP_GET, [this]() { state(); });
        _server->on("/flprog-webui/write", HTTP_POST, [this]() { write(); });
        _server->onNotFound([this]() { _server->send(404, "application/json", "{\"error\":\"not found\"}"); });
        _server->begin();
    }

    // Call from the networking task/loop. No allocations are performed by
    // FLProg_WebUI between requests; ESP8266WebServer may allocate internally
    // while parsing an actual incoming request.
    void poll() { if (_server) _server->handleClient(); }

private:
    void index() {
        static const char page[] PROGMEM =
            "<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>FLProg Web UI</title><style>body{font:16px sans-serif;margin:20px}pre{white-space:pre-wrap}</style>"
            "<h1>FLProg Web UI</h1><pre id=s>Loading...</pre><script>"
            "async function q(){let r=await fetch('/flprog-webui/state');s.textContent=await r.text()}q();setInterval(q,1000)"
            "</script>";
        _server->send_P(200, PSTR("text/html; charset=utf-8"), page);
    }
    void state() {
        if (!_api.state(_buffer, sizeof(_buffer))) { _server->send(507, "application/json", "{\"error\":\"response too large\"}"); return; }
        _server->send(200, "application/json", _buffer);
    }
    void write() {
        if (!_server->hasArg("channel") || !_server->hasArg("value")) { _server->send(400, "application/json", "{\"error\":\"channel and value required\"}"); return; }
        // These String objects belong to ESP8266WebServer request handling and
        // exist only for a real HTTP request, never during normal FBD cycles.
        String channel = _server->arg("channel"), value = _server->arg("value");
        if (!_api.write(channel.c_str(), value.c_str())) { _server->send(404, "application/json", "{\"error\":\"unknown channel\"}"); return; }
        _server->send(202, "application/json", "{\"queued\":true}");
    }
    FLProgWebUiHttpProtocol _api;
    ESP8266WebServer *_server;
    char _buffer[FLPROG_WEBUI_HTTP_BUFFER_SIZE];
};
#endif
