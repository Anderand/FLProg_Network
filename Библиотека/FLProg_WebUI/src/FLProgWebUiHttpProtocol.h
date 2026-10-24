/* Allocation-free HTTP payloads for FLProg_WebUI.
 * A platform transport owns sockets and calls this class; this file does not
 * include WiFi, Ethernet or FLProg_Network. */
#pragma once

#include "FLProgWebUi.h"
#include <stdio.h>
#include <stdlib.h>

class FLProgWebUiHttpProtocol {
public:
    explicit FLProgWebUiHttpProtocol(FLProgWebUiModel &model) : _model(model) {}
    bool state(char *out, size_t size) const {
        Writer w(out, size); w.puts("{\"schema\":\"flprog.webui/1.0\",\"channels\":{");
        for (uint8_t i=0; i<_model.count(); ++i) {
            if (i) w.put(','); const FLProgWebUiChannelDescriptor *d=_model.descriptor(i);
            w.json(d->id); w.put(':');
            switch (_model.typeAt(i)) {
                case FLPROG_WEBUI_BOOL: w.puts(_model.boolAt(i) ? "true" : "false"); break;
                case FLPROG_WEBUI_INT32: w.number(_model.intAt(i)); break;
                case FLPROG_WEBUI_FLOAT: w.decimal(_model.floatAt(i)); break;
                default: w.json(_model.textAt(i)); break;
            }
        }
        w.puts("}}"); return w.ok();
    }
    // A small, independently cacheable state response. The FLProg_Network
    // HTTP server deliberately has a bounded response queue, so Web UI never
    // serialises the entire channel catalogue into one HTTP response.
    bool stateOne(const char *channel, char *out, size_t size) const {
        const int16_t index = _model.indexOf(channel);
        if (index < 0) return false;
        Writer w(out, size);
        w.puts("{\"channel\":"); w.json(_model.descriptor((uint8_t)index)->id); w.puts(",\"value\":");
        switch (_model.typeAt((uint8_t)index)) {
            case FLPROG_WEBUI_BOOL: w.puts(_model.boolAt((uint8_t)index) ? "true" : "false"); break;
            case FLPROG_WEBUI_INT32: w.number(_model.intAt((uint8_t)index)); break;
            case FLPROG_WEBUI_FLOAT: w.decimal(_model.floatAt((uint8_t)index)); break;
            default: w.json(_model.textAt((uint8_t)index)); break;
        }
        w.put('}'); return w.ok();
    }
    bool write(const char *channel, const char *value) {
        const int16_t index=_model.indexOf(channel); if (index < 0 || !value || _model.directionAt((uint8_t)index) == FLPROG_WEBUI_PUBLISH) return false;
        switch (_model.typeAt((uint8_t)index)) {
            case FLPROG_WEBUI_BOOL: return _model.queueBool(index, eq(value,"1") || eq(value,"true") || eq(value,"on"));
            case FLPROG_WEBUI_INT32: return _model.queueInt(index, (int32_t)strtol(value, 0, 10));
            case FLPROG_WEBUI_FLOAT: return _model.queueFloat(index, strtof(value, 0));
            default: return _model.queueText(index, value);
        }
    }
private:
    class Writer {
    public:
        Writer(char *out, size_t size) : _out(out), _size(size), _at(0), _ok(out && size) { if (_ok) _out[0]=0; }
        bool ok() const { return _ok; }
        void put(char c) { if (!_ok || _at+1>=_size) {_ok=false; return;} _out[_at++]=c; _out[_at]=0; }
        void puts(const char *s) { while (s && *s) put(*s++); }
        void number(int32_t value) { char b[16]; snprintf(b,sizeof(b),"%ld",(long)value); puts(b); }
        void decimal(float value) { char b[24]; snprintf(b,sizeof(b),"%.3f",(double)value); puts(b); }
        void json(const char *s) { put('"'); for (;s && *s;++s) { if (*s=='"'||*s=='\\') put('\\'); if ((unsigned char)*s<0x20) put(' '); else put(*s); } put('"'); }
    private: char *_out; size_t _size,_at; bool _ok;
    };
    static bool eq(const char *a, const char *b) { return a && b && strcmp(a,b)==0; }
    FLProgWebUiModel &_model;
};
