/*
 * Bounded-response Web UI transport for FLProg_Network.
 *
 * A page is intentionally composed of small responses: metadata, one widget,
 * one channel state and one scan record. This is essential on ESP8266 where
 * FLProgNetworkHttpServer has a fixed response queue. The adapter uses only
 * public FLProg_Network APIs and can serve the same UI through STA and SoftAP.
 */
#pragma once

#include <flprogNetwork.h>
#include "../FLProgWebUiHttpProtocol.h"

#ifndef FLPROG_WEBUI_FLPROG_HTTP_BUFFER_SIZE
#define FLPROG_WEBUI_FLPROG_HTTP_BUFFER_SIZE 1024U
#endif

// ESP8266 has only 32 KiB of user IRAM.  HTTP handlers run from the normal
// cooperative loop (never from an ISR), therefore their code is safe in flash.
// Keeping the large JSON and page-generation routines there is important when
// a FLProg project also uses Wi-Fi, OTA and several generated blocks.
#if defined(ESP8266)
// Do not use ICACHE_FLASH_ATTR in a header: its ESP8266-core implementation
// embeds __FILE__ into the assembler section name, while Windows paths contain
// backslashes and break the assembler. A stable explicit IROM section is safe
// here because these functions are only entered from the cooperative loop.
#define FLPROG_WEBUI_HTTP_STRINGIFY_INNER(value) #value
#define FLPROG_WEBUI_HTTP_STRINGIFY(value) FLPROG_WEBUI_HTTP_STRINGIFY_INNER(value)
// Every function needs its own section: GCC rejects one common IROM section
// when it would otherwise contain methods with incompatible section flags.
#define FLPROG_WEBUI_HTTP_FLASH __attribute__((section(".irom0.text.flpwebui." FLPROG_WEBUI_HTTP_STRINGIFY(__COUNTER__))))
#else
#define FLPROG_WEBUI_HTTP_FLASH
#endif

class FLProgWebUiFlprogNetworkPagedHttp {
public:
    FLProgWebUiFlprogNetworkPagedHttp(FLProgWebUiModel &model, const FLProgWebUiWidgetDescriptor *widgets, uint8_t count)
        : model(model), api(model), widgets(widgets), widgetCount(count), pages(0), pageCount(0), theme(defaultTheme()), network(0), settingsLoaded(false), apSettingsLoaded(false) {}

    FLProgWebUiFlprogNetworkPagedHttp(FLProgWebUiModel &model, const FLProgWebUiWidgetDescriptor *widgets, uint8_t count, const FLProgWebUiThemeDescriptor &theme)
        : model(model), api(model), widgets(widgets), widgetCount(count), pages(0), pageCount(0), theme(theme), network(0), settingsLoaded(false), apSettingsLoaded(false) {}

    FLProgWebUiFlprogNetworkPagedHttp(FLProgWebUiModel &model, const FLProgWebUiWidgetDescriptor *widgets, uint8_t count, const FLProgWebUiPageDescriptor *pages, uint8_t pageCount, const FLProgWebUiThemeDescriptor &theme)
        : model(model), api(model), widgets(widgets), widgetCount(count), pages(pages), pageCount(pageCount), theme(theme), network(0), settingsLoaded(false), apSettingsLoaded(false) {}

    bool FLPROG_WEBUI_HTTP_FLASH begin(FLProgNetworkInterface &value, uint16_t port = 80)
    {
        if (active()) return false;
        server.setBrowserHeaderCompatibility(true);
        // A shared SoftAP listener is supported only when the primary HTTP
        // server owns one client slot. The browser therefore sends requests
        // serially; this also avoids exhausting ESP8266 sockets.
        if (!server.begin(value, port, FLPROG_NETWORK_ROUTE_DEFAULT, 1)) return false;
        network = &value;
        active() = this;

        const FLProgNetworkPlatformCapabilities caps = FLProgNetworkInterface::platformCapabilities();
        if (caps.wifiApCompiled && !server.addSharedListener(value, FLPROG_NETWORK_ROUTE_WIFI_AP))
        {
            end();
            return false;
        }

        // The paged UI stays within the 14-route FLProg_Network budget while
        // keeping each response below the bounded HTTP response buffer.
        // Page zero includes metadata; every descriptor remains a small response.
        const bool ready =
            server.addHandler("/", index, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/app.css", css, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/scan.js", scanScript, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/controls.js", controlScript, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/widgets.js", widgetScript, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/boot-view.js", bootViewScript, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/boot.js", bootScript, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/item", item, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/state", state, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/scan", scan, FLPROG_WEB_SERVER_GET) &&
            server.addHandler("/flprog-webui/scan/start", scanStart, FLPROG_WEB_SERVER_POST) &&
            server.addHandler("/flprog-webui/write", write, FLPROG_WEB_SERVER_POST);
        if (!ready) end();
        return ready;
    }

    void FLPROG_WEBUI_HTTP_FLASH end()
    {
        server.end();
        if (active() == this) active() = 0;
        network = 0;
    }

private:
    class Json {
    public:
        Json(char *data, size_t size) : data(data), size(size), at(0), valid(data && size)
        {
            if (valid) data[0] = 0;
        }
        bool good() const { return valid; }
        void character(char value)
        {
            if (!valid || at + 1 >= size) { valid = false; return; }
            data[at++] = value;
            data[at] = 0;
        }
        void text(const char *value) { while (value && *value) character(*value++); }
        void string(const char *value)
        {
            character('"');
            for (; value && *value; ++value)
            {
                if (*value == '"' || *value == '\\') character('\\');
                if ((unsigned char)*value < 32) character(' '); else character(*value);
            }
            character('"');
        }
        void unsignedNumber(unsigned value) { char result[12]; snprintf(result, sizeof(result), "%u", value); text(result); }
        void signedNumber(int32_t value) { char result[16]; snprintf(result, sizeof(result), "%ld", (long)value); text(result); }
        void decimal(float value) { char result[20]; snprintf(result, sizeof(result), "%.3f", (double)value); text(result); }
    private:
        char *data;
        size_t size;
        size_t at;
        bool valid;
    };

    static FLProgWebUiFlprogNetworkPagedHttp *&active()
    {
        static FLProgWebUiFlprogNetworkPagedHttp *instance = 0;
        return instance;
    }

    static void FLPROG_WEBUI_HTTP_FLASH sendJson(FLProgNetworkHttpServer *value, Json &json)
    {
        if (!json.good()) value->send(507, "application/json", "{\"error\":\"item too large\"}");
        else value->send(200, "application/json", active()->buffer);
    }

    static void FLPROG_WEBUI_HTTP_FLASH index(FLProgNetworkHttpServer *value)
    {
        static const char asset[] PROGMEM =
            "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            "<style>.el{background:transparent;border:0;border-radius:0;padding:4px 0}.el.head h1{margin:0;font-size:28px}.el.txt{color:#d6e2f4}.el.div hr{border:0;border-top:1px solid #34465f}.el.lnk a{color:#a78bfa}.el.row{display:flex;justify-content:space-between;border-bottom:1px solid #34465f;padding:7px 0}.el.row b{font-weight:800}</style><main><nav id=n></nav><div id=s>Загрузка интерфейса…</div></main><div id=m hidden></div>"
            "<script>(async()=>{let p=['scan.js','controls.js','widgets.js','boot-view.js','boot.js'],v='webui38';try{for(let x of p)await new Promise((ok,no)=>{let e=document.createElement('script');e.src='/flprog-webui/'+x+'?v='+v;e.async=false;e.onload=()=>setTimeout(ok,80);e.onerror=()=>no(Error(x));document.head.append(e)});let c=document.createElement('link');c.rel='stylesheet';c.href='/flprog-webui/app.css?v='+v;document.head.append(c)}catch(e){document.querySelector('#s').textContent='Ошибка загрузки: '+e.message}})()</script>";
        value->sendProgmem(200, "text/html; charset=utf-8", asset);
    }

    static void FLPROG_WEBUI_HTTP_FLASH css(FLProgNetworkHttpServer *value)
    {
        static const char asset[] PROGMEM =
            ":root{--bg:#0b1120;--card:#162237;--accent:#7367ff;--line:#7186a8}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:#fff;font:16px system-ui}main{max-width:1100px;margin:auto;padding:12px}#n{display:flex;gap:5px;overflow:auto;margin-bottom:10px;border-bottom:2px solid var(--line)}button{min-height:35px;padding:8px 10px;border:1px solid #8fa6c8;border-radius:8px;background:#263754;color:#fff}button.on{background:var(--accent)}button:disabled{opacity:.7}#n button{border:0;background:0;color:#fff;white-space:nowrap;font-weight:700}#s{display:grid;grid-template-columns:repeat(12,1fr);gap:10px}.w{min-width:0;padding:13px;border:1px solid var(--line);border-radius:12px;background:var(--card)}.n{color:#fff;font-size:15px;font-weight:700}.v{margin-top:8px;color:#fff;font-size:23px;font-weight:800;word-break:break-word}.binding-values{display:grid;gap:4px;margin-top:9px;padding-top:7px;border-top:1px solid var(--line);font-size:13px;color:#dbeafe}input,select{width:100%;min-height:37px;margin-top:10px;border:1px solid #8fa6c8;border-radius:8px;padding:8px;background:#091323;color:#fff}.w>button{width:100%;margin-top:10px}.scan,.days{display:grid;gap:6px;margin-top:10px;color:#fff}.days{grid-template-columns:repeat(7,1fr)}.gauge,.progress{margin-top:10px}.gauge i,.progress i{display:block;height:12px;margin-top:8px;border-radius:9px;background:linear-gradient(90deg,var(--accent) var(--p),#0b1525 var(--p))}.net{width:100%;margin-top:6px;text-align:left}.check{display:block;margin-top:12px;color:#fff}";
        value->sendProgmem(200, "text/css", asset);
    }

    static void FLPROG_WEBUI_HTTP_FLASH scanScript(FLProgNetworkHttpServer *value)
    {
        static const char asset[] PROGMEM =
            "function C(w,x,d){let h=window._flpChart||(window._flpChart={}),r=w.max-w.min||1,c=document.createElement('canvas'),ctx=c.getContext('2d');c.width=260;c.height=70;c.style.cssText='width:100%;height:70px;margin-top:8px;background:#08101c';let series=[{id:w.channel,value:x,color:w.color||'#6ee7ff'}];(w.bindings||[]).filter(b=>b.role=='series1'||b.role=='series2').forEach(b=>series.push({id:b.channel,value:v[b.channel],color:b.role=='series1'?'#f59e0b':'#34d399'}));series.forEach(a=>{let q=h[a.id]||[];q.push(+a.value||0);q=q.slice(-24);h[a.id]=q;ctx.strokeStyle=a.color;ctx.beginPath();q.forEach((n,i)=>{let X=i*260/23,Y=66-62*(n-w.min)/r;i?ctx.lineTo(X,Y):ctx.moveTo(X,Y)});ctx.stroke()});d.append(c);return 1}";
        value->sendProgmem(200, "application/javascript", asset);
    }

    static void FLPROG_WEBUI_HTTP_FLASH widgetScript(FLProgNetworkHttpServer *value)
    {
        static const char asset[] PROGMEM =
            "function V(w,x,s){let d=document.createElement('section'),input=/input/.test(w.type),target=(w.bindings||[]).find(b=>b.role=='setpoint')?.channel||w.channel,controlValue=v[target]===undefined?x:v[target];d.className='w';d.style.gridColumn=w.x+' / span '+w.w;d.style.gridRow=w.y+' / span '+w.h;d.style.borderColor=w.color||t.accent||'#475569';if(w.type=='heading'){d.className+=' el head';d.innerHTML='<h1>'+e(w.label)+'</h1>';s.append(d);return}if(w.type=='divider'){d.className+=' el div';d.innerHTML='<hr>';s.append(d);return}if(w.type=='link'){d.className+=' el lnk';let a=document.createElement('a');a.href=w.options||'#';a.textContent=w.label||w.options;d.append(a);s.append(d);return}if(w.type=='status-row'){d.className+=' el row';d.innerHTML='<span>'+e(w.label)+'</span><b>'+e(x)+'</b>';s.append(d);return}d.innerHTML='<div class=n>'+e(w.icon)+' '+e(w.label)+'</div>';if(w.code){d.innerHTML+='<div class=v>'+w.code.replace(/{{label}}/g,e(w.label)).replace(/{{value}}/g,e(x)).replace(/{{icon}}/g,e(w.icon))+'</div>';s.append(d);return}if(w.type=='static-text'){d.className+=' el txt';d.innerHTML+='<div>'+e(w.options||'')+'</div>'}else if(w.type=='wifi-scan'){S(d)}else if(w.type=='chart'){C(w,x,d)}else if(!X(w,/^(checkbox|weekdays|select|number-input|color-input|date-input|time-input)$/.test(w.type)?controlValue:x,d)&&!input)d.innerHTML+='<div class=v>'+e(w.type=='indicator'&&typeof x=='boolean'?(x?'Подключено':'Нет подключения'):x)+'</div>';if(w.type=='slider'){let i=document.createElement('input');i.type='range';i.min=w.min;i.max=w.max;i.step=w.step;i.value=controlValue;i.oninput=()=>{v[target]=+i.value};i.onchange=()=>p(target,i.value);d.append(i)}else if(w.type=='switch'){let i=document.createElement('button');i.textContent=controlValue?'Включено':'Выключено';i.onclick=()=>p(target,!controlValue);d.append(i)}else if(input){let i=document.createElement('input');i.type=w.type=='password-input'?'password':'text';i.value=w.type=='password-input'?'':controlValue||'';i.placeholder=w.type=='password-input'?'Введите новый пароль':'';i.onchange=()=>{if(i.value||w.type!='password-input')p(target,i.value)};d.append(i)}else if(w.type=='button'){let i=document.createElement('button');i.textContent=w.label;i.onclick=()=>{if(confirm('Отправить команду?'))p(target,true)};d.append(i)}let extras=(w.bindings||[]).filter(b=>['alarm','busy','result'].includes(b.role));if(extras.length){let info=document.createElement('div');info.className='binding-values';extras.forEach(b=>{let row=document.createElement('div');row.textContent=b.role+': '+(v[b.channel]===undefined?'—':v[b.channel]);info.append(row)});d.append(info)}s.append(d)}";
        value->sendProgmem(200, "application/javascript", asset);
    }

    static void FLPROG_WEBUI_HTTP_FLASH controlScript(FLProgNetworkHttpServer *value)
    {
        static const char asset[] PROGMEM =
            "function X(w,x,d){let k=w.type,i,z=Math.max(0,Math.min(100,100*(x-w.min)/(w.max-w.min||1))),target=(w.bindings||[]).find(b=>b.role=='setpoint')?.channel||w.channel;if(I(w,x,d))return 1;if(k=='radial-gauge'){d.innerHTML+='<div style=\\\\\\\"width:88px;height:88px;padding:25px 0;text-align:center;border-radius:50%;background:conic-gradient('+w.color+' '+z+'%,#0b1525 0)\\\\\\\">'+e(x)+'</div>';return 1}if(k=='battery'){d.innerHTML+='<div style=\\\\\\\"margin-top:10px;border:2px solid '+w.color+';padding:3px\\\\\\\"><i style=\\\\\\\"display:block;height:22px;width:'+z+'%;background:'+w.color+'\\\\\\\"></i></div>';return 1}if(k=='segment-display'){d.innerHTML+='<div style=\\\\\\\"margin-top:10px;padding:8px;background:#050805;color:#7cff9c;font:28px monospace;letter-spacing:3px\\\\\\\">'+e(x)+'</div>';return 1}if(k=='traffic-light'){d.innerHTML+='<div style=\\\\\\\"margin-top:10px;width:32px;height:32px;border-radius:50%;background:'+(x?'#36d399':'#ef4444')+'\\\\\\\"></div>';return 1}if(k=='gauge'||k=='progress'){d.innerHTML+='<div class='+k+'><b>'+e(x)+'</b><i style=\\\\\\\"--p:'+z+'%\\\\\\\"></i></div>';return 1}if(k=='checkbox'){i=document.createElement('label');i.className='check';i.innerHTML='<input type=checkbox '+(x?'checked':'')+'> Включено';i.firstChild.onchange=()=>p(target,i.firstChild.checked)}else if(k=='weekdays'){i=document.createElement('div');i.className='days';'Пн Вт Ср Чт Пт Сб Вс'.split(' ').forEach((z,n)=>{let b=document.createElement('button');b.textContent=z;b.className=(x&(1<<n))?'on':'';b.onclick=()=>p(target,(x^(1<<n)));i.append(b)})}else if(k=='select'){i=document.createElement('select');(w.options||'').split(';').forEach(z=>{let o=document.createElement('option');o.value=z;o.textContent=z;o.selected=z==x;i.append(o)});i.onchange=()=>p(target,i.value)}else if(/^(number|color|date|time)-input$/.test(k)){i=document.createElement('input');i.type=k.split('-')[0];i.value=x||'';i.min=w.min;i.max=w.max;i.step=w.step||'any';i.onchange=()=>p(target,i.value)}else return 0;d.append(i);return 1}";
        value->sendProgmem(200, "application/javascript", asset);
    }

    static void FLPROG_WEBUI_HTTP_FLASH bootScript(FLProgNetworkHttpServer *value)
    {
        static const char asset[] PROGMEM =
            "var a=[],t={},g='',n=[],v={},busy=0,rv=0,loadedPage='';var f=async u=>{let r=await fetch(u);if(!r.ok)throw Error('HTTP '+r.status);return r.json()};function e(v){let x=document.createElement('span');x.textContent=v==null?'':v;return x.innerHTML}function M(v){let x=document.querySelector('#m');x.textContent=v;x.hidden=!v}async function p(k,v){try{let r=await fetch('/flprog-webui/write?channel='+encodeURIComponent(k)+'&value='+encodeURIComponent(v),{method:'POST'});if(!r.ok)throw Error('Настройки не приняты');await q()}catch(x){M(x.message)}}"
            "async function q(){if(busy)return;busy=1;try{let u='/flprog-webui/state?page='+encodeURIComponent(g);if(loadedPage==g)u+='&since='+rv;let d=await f(u);rv=d.revision||rv;Object.assign(v,d.values||{});loadedPage=g;let z=a.filter(w=>w.page==g),s=document.querySelector('#s');if(s.dataset.page!==g){s.replaceChildren();s.dataset.page=g}z.forEach((w,i)=>{let old=s.children[i],x=(w.bindings||[]).find(b=>b.role=='value')?v[(w.bindings||[]).find(b=>b.role=='value').channel]:v[w.channel],signature=JSON.stringify([x,...(w.bindings||[]).map(b=>v[b.channel])]);if(old&&(old.contains(document.activeElement)||w.type=='wifi-scan'||(w.type!='chart'&&old._signature===signature)))return;let holder=document.createElement('div');V(w,x,holder);let next=holder.firstElementChild;next._value=x;next._signature=signature;if(old)old.replaceWith(next);else s.append(next)});M('')}catch(x){M('Ошибка обновления: '+x.message)}finally{busy=0}}"
            "async function L(x){if(!x||x.loaded)return;for(let i of x.indices||[])a[i]=await f('/flprog-webui/item?index='+i);x.loaded=1}async function B(){try{let m=await f('/flprog-webui/item?page=0');t=m.theme||{};n.push(m);for(let i=1;i<m.pages;i++)n.push(await f('/flprog-webui/item?page='+i));g=n[0]?n[0].id:'main';let z=document.querySelector('#n');z.innerHTML=n.map(x=>'<button>'+e(x.title)+'</button>').join('');[...z.children].forEach((x,i)=>x.onclick=async()=>{g=n[i].id;loadedPage='';v={};[...z.children].forEach(y=>y.className='');x.className='on';await L(n[i]);q()});if(z.children[0])z.children[0].className='on';let r=document.documentElement.style;r.setProperty('--bg',t.background||'');r.setProperty('--card',t.card||'');r.setProperty('--text',t.text||'');r.setProperty('--accent',t.accent||'');await L(n[0]);await q();setInterval(q,1300)}catch(x){let h='Ошибка запуска: '+(x.message||x);document.querySelector('#s').textContent=h;M(h)}}setTimeout(B,350)";
        value->sendProgmem(200, "application/javascript", asset);
    }

    static void FLPROG_WEBUI_HTTP_FLASH bootViewScript(FLProgNetworkHttpServer *value)
    {
        static const char asset[] PROGMEM =
            "function I(w,x,d){let z=100*(x-w.min)/(w.max-w.min||1),c=w.color||'#7367ff';z=Math.max(0,Math.min(100,z));if(w.type=='sector-gauge'){d.innerHTML+='<i style=\"display:block;width:100px;height:50px;margin:8px auto;padding-top:27px;text-align:center;border-radius:100px 100px 0 0;background:conic-gradient(from 270deg,'+c+' '+z+'%,#091323 0 50%,transparent 0)\">'+e(x)+'</i>';return 1}if(w.type=='bar-meter'){d.innerHTML+='<b style=\"display:block;height:38px;margin-top:8px;background:'+c+';clip-path:inset('+(100-z)+'% 0 0)\"></b>';return 1}}";
        value->sendProgmem(200, "application/javascript", asset);
    }

    static void FLPROG_WEBUI_HTTP_FLASH scanStart(FLProgNetworkHttpServer *value)
    {
        if (!active() || !active()->network || !FLProgNetworkInterface::platformCapabilities().wifiScanCompiled)
        {
            value->send(501, "application/json", "{\"error\":\"Wi-Fi scan is unavailable\"}");
            return;
        }
        if (!active()->network->startWifiScan(false))
        {
            value->send(409, "application/json", "{\"error\":\"scan busy\"}");
            return;
        }
        value->send(202, "application/json", "{\"queued\":true}");
    }

    static void FLPROG_WEBUI_HTTP_FLASH scan(FLProgNetworkHttpServer *value)
    {
        if (!active() || !active()->network) { value->send(503, "application/json", "{}"); return; }
        if (value->hasArgumentKey("index"))
        {
            const unsigned index = strtoul(value->argumentValueAtKey("index").c_str(), 0, 10);
            const int16_t count = active()->network->wifiScanCount();
            if (index > 255 || index >= (unsigned)(count > 0 ? count : 0)) { value->send(404, "application/json", "{}"); return; }
            Json json(active()->buffer, sizeof(active()->buffer));
            const String ssid = active()->network->wifiScanSsid((uint8_t)index);
            json.text("{\"ssid\":"); json.string(ssid.c_str());
            json.text(",\"rssi\":"); json.signedNumber(active()->network->wifiScanRssi((uint8_t)index));
            json.text(",\"channel\":"); json.signedNumber(active()->network->wifiScanChannel((uint8_t)index));
            json.text(",\"secure\":"); json.text(active()->network->wifiScanEncryption((uint8_t)index) ? "true" : "false");
            json.character('}');
            sendJson(value, json);
            return;
        }
        Json json(active()->buffer, sizeof(active()->buffer));
        const int16_t total = active()->network->wifiScanCount();
        const unsigned count = total <= 0 ? 0 : (total > 20 ? 20U : (unsigned)total);
        json.text("{\"running\":"); json.text(active()->network->wifiScanRunning() ? "true" : "false");
        json.text(",\"count\":"); json.unsignedNumber(count);
        json.text(",\"total\":"); json.unsignedNumber(total > 0 ? (unsigned)total : 0);
        json.text(",\"error\":"); json.unsignedNumber(active()->network->wifiScanLastError());
        json.character('}');
        sendJson(value, json);
    }

    static void FLPROG_WEBUI_HTTP_FLASH item(FLProgNetworkHttpServer *value)
    {
        if (!active()) { value->send(503, "application/json", "{}"); return; }
        if (value->hasArgumentKey("page"))
        {
            const unsigned index = strtoul(value->argumentValueAtKey("page").c_str(), 0, 10);
            const uint8_t count = active()->pageCount ? active()->pageCount : active()->derivedPageCount();
            if (index >= count) { value->send(404, "application/json", "{\"error\":\"unknown page\"}"); return; }
            const char *id = active()->pageCount ? active()->pages[index].id : active()->derivedPage((uint8_t)index);
            const char *title = active()->pageCount ? active()->pages[index].title : active()->friendlyTitle(id);
            Json json(active()->buffer, sizeof(active()->buffer));
            json.text("{\"id\":"); json.string(id); json.text(",\"title\":"); json.string(title);
            // Tell the browser exactly which small descriptor responses belong to
            // this page.  It can then defer other pages until the user opens them.
            json.text(",\"indices\":[");
            bool firstWidget = true;
            for (uint8_t widgetIndex = 0; widgetIndex < active()->widgetCount; ++widgetIndex)
            {
                const char *widgetPage = active()->widgets[widgetIndex].page ? active()->widgets[widgetIndex].page : "main";
                if (strcmp(widgetPage, id) != 0) continue;
                if (!firstWidget) json.character(',');
                json.unsignedNumber(widgetIndex);
                firstWidget = false;
            }
            json.character(']');
            if (index == 0)
            {
                const FLProgWebUiThemeDescriptor &currentTheme = active()->theme;
                json.text(",\"widgets\":"); json.unsignedNumber(active()->widgetCount);
                json.text(",\"pages\":"); json.unsignedNumber(active()->pageCount ? active()->pageCount : active()->derivedPageCount());
                json.text(",\"theme\":{\"background\":"); json.string(currentTheme.background);
                json.text(",\"card\":"); json.string(currentTheme.card);
                json.text(",\"text\":"); json.string(currentTheme.text);
                json.text(",\"accent\":"); json.string(currentTheme.accent); json.character('}');
            }
            json.character('}');
            sendJson(value, json);
            return;
        }
        if (!value->hasArgumentKey("index")) { value->send(400, "application/json", "{\"error\":\"index required\"}"); return; }
        const unsigned index = strtoul(value->argumentValueAtKey("index").c_str(), 0, 10);
        if (index >= active()->widgetCount) { value->send(404, "application/json", "{\"error\":\"unknown widget\"}"); return; }
        const FLProgWebUiWidgetDescriptor &item = active()->widgets[index];
        Json json(active()->buffer, sizeof(active()->buffer));
        json.text("{\"type\":"); json.string(item.type); json.text(",\"label\":"); json.string(item.label);
        json.text(",\"channel\":"); json.string(item.channel); json.text(",\"icon\":"); json.string(item.icon);
        json.text(",\"color\":"); json.string(item.color); json.text(",\"page\":"); json.string(item.page ? item.page : "main"); json.text(",\"options\":"); json.string(item.options ? item.options : ""); json.text(",\"code\":"); json.string(item.code ? item.code : "");
        json.text(",\"bindings\":[");
        for (uint8_t i = 0; item.bindings && i < item.bindingCount; ++i)
        {
            if (i) json.character(',');
            json.text("{\"role\":"); json.string(item.bindings[i].role);
            json.text(",\"channel\":"); json.string(item.bindings[i].channel);
            json.text(",\"direction\":"); json.string(item.bindings[i].direction); json.character('}');
        }
        json.character(']');
        json.text(",\"min\":"); json.decimal(item.minimum); json.text(",\"max\":"); json.decimal(item.maximum); json.text(",\"step\":"); json.decimal(item.step);
        json.text(",\"x\":"); json.unsignedNumber(item.x); json.text(",\"y\":"); json.unsignedNumber(item.y);
        json.text(",\"w\":"); json.unsignedNumber(item.width); json.text(",\"h\":"); json.unsignedNumber(item.height); json.character('}');
        sendJson(value, json);
    }

    void FLPROG_WEBUI_HTTP_FLASH jsonValue(Json &json, uint8_t index)
    {
        switch (model.typeAt(index))
        {
            case FLPROG_WEBUI_BOOL: json.text(model.boolAt(index) ? "true" : "false"); break;
            case FLPROG_WEBUI_INT32: json.signedNumber(model.intAt(index)); break;
            case FLPROG_WEBUI_FLOAT: json.decimal(model.floatAt(index)); break;
            default: json.string(model.textAt(index)); break;
        }
    }

    bool FLPROG_WEBUI_HTTP_FLASH channelBefore(const char *page, const char *channel, uint8_t widgetIndex, uint8_t bindingIndex) const
    {
        for (uint8_t i = 0; i <= widgetIndex; ++i)
        {
            const FLProgWebUiWidgetDescriptor &previous = widgets[i];
            const char *previousPage = previous.page ? previous.page : "main";
            if (strcmp(previousPage, page) != 0) continue;
            if (previous.channel && strcmp(previous.channel, channel) == 0 && (i < widgetIndex || bindingIndex > 0)) return true;
            if (previous.bindings)
                for (uint8_t b = 0; b < previous.bindingCount; ++b)
                    if ((i < widgetIndex || b < bindingIndex) && strcmp(previous.bindings[b].channel, channel) == 0) return true;
        }
        return false;
    }

    void FLPROG_WEBUI_HTTP_FLASH statePage(FLProgNetworkHttpServer *value, const char *page, bool hasRevision, uint16_t since)
    {
        syncSystem();
        Json json(buffer, sizeof(buffer));
        json.text("{\"revision\":"); json.unsignedNumber(model.revision()); json.text(",\"values\":{");
        bool first = true;
        for (uint8_t i = 0; i < widgetCount; ++i)
        {
            const FLProgWebUiWidgetDescriptor &widget = widgets[i];
            const char *widgetPage = widget.page ? widget.page : "main";
            if (strcmp(widgetPage, page) != 0 || strcmp(widget.type, "wifi-scan") == 0) continue;
            for (uint8_t b = 0; b <= widget.bindingCount; ++b)
            {
                const char *channel = b == 0 ? widget.channel : widget.bindings[b - 1].channel;
                if (!channel || strcmp(channel, "wifi_password") == 0 || strcmp(channel, "ap_password") == 0 || channelBefore(page, channel, i, b)) continue;
                const int16_t index = model.indexOf(channel);
                if (index < 0 || (hasRevision && !model.changedSince((uint8_t)index, since))) continue;
                if (!first) json.character(',');
                first = false;
                json.string(channel); json.character(':'); jsonValue(json, (uint8_t)index);
            }
        }
        json.text("}}");
        sendJson(value, json);
    }

    static void FLPROG_WEBUI_HTTP_FLASH state(FLProgNetworkHttpServer *value)
    {
        if (!active()) { value->send(503, "application/json", "{}"); return; }
        if (value->hasArgumentKey("page"))
        {
            const String page = value->argumentValueAtKey("page");
            const bool hasRevision = value->hasArgumentKey("since");
            const uint16_t since = hasRevision ? (uint16_t)strtoul(value->argumentValueAtKey("since").c_str(), 0, 10) : 0;
            active()->statePage(value, page.c_str(), hasRevision, since);
            return;
        }
        if (!value->hasArgumentKey("channel")) { value->send(404, "application/json", "{\"error\":\"unknown channel\"}"); return; }
        const String channel = value->argumentValueAtKey("channel");
        // Passwords are write-only: the browser can replace, never read them.
        if (channel == "wifi_password" || channel == "ap_password") { value->send(404, "application/json", "{\"error\":\"secret channel\"}"); return; }
        active()->syncSystem();
        if (!active()->api.stateOne(channel.c_str(), active()->buffer, sizeof(active()->buffer))) { value->send(404, "application/json", "{\"error\":\"unknown channel\"}"); return; }
        value->send(200, "application/json", active()->buffer);
    }

    static void FLPROG_WEBUI_HTTP_FLASH write(FLProgNetworkHttpServer *value)
    {
        if (!active() || !value->hasArgumentKey("channel") || !value->hasArgumentKey("value")) { value->send(400, "application/json", "{\"error\":\"channel and value required\"}"); return; }
        const String channel = value->argumentValueAtKey("channel");
        const String input = value->argumentValueAtKey("value");
        if (!active()->api.write(channel.c_str(), input.c_str())) { value->send(404, "application/json", "{\"error\":\"unknown or readonly channel\"}"); return; }
        if (active()->network && channel == "wifi_ssid") active()->network->setClientSsid(input);
        if (active()->network && channel == "wifi_password") active()->network->setClientPassword(input);
        if (channel == "network_apply" && !active()->applyStaSettings()) { value->send(422, "application/json", "{\"error\":\"invalid static IP settings\"}"); return; }
        if (channel == "ap_apply" && !active()->applyApSettings()) { value->send(422, "application/json", "{\"error\":\"invalid access point settings\"}"); return; }
        if (channel == "wifi_scan" && (!active()->network || !active()->network->startWifiScan(false))) { value->send(409, "application/json", "{\"error\":\"scan busy or unavailable\"}"); return; }
        value->send(202, "application/json", "{\"queued\":true}");
    }

    static const FLProgWebUiThemeDescriptor &FLPROG_WEBUI_HTTP_FLASH defaultTheme()
    {
        static const FLProgWebUiThemeDescriptor value = {"#0b1120", "#162237", "#edf3ff", "#7367ff"};
        return value;
    }

    const char *FLPROG_WEBUI_HTTP_FLASH derivedPage(uint8_t index) const
    {
        uint8_t found = 0;
        for (uint8_t i = 0; i < widgetCount; ++i)
        {
            const char *id = widgets[i].page ? widgets[i].page : "main";
            bool known = false;
            for (uint8_t previous = 0; previous < i; ++previous)
                if (strcmp(widgets[previous].page ? widgets[previous].page : "main", id) == 0) { known = true; break; }
            if (!known && found++ == index) return id;
        }
        return "main";
    }

    uint8_t FLPROG_WEBUI_HTTP_FLASH derivedPageCount() const
    {
        uint8_t count = 0;
        for (uint8_t i = 0; i < widgetCount; ++i)
        {
            const char *id = widgets[i].page ? widgets[i].page : "main";
            bool known = false;
            for (uint8_t previous = 0; previous < i; ++previous)
                if (strcmp(widgets[previous].page ? widgets[previous].page : "main", id) == 0) { known = true; break; }
            if (!known) ++count;
        }
        return count;
    }

    const char *FLPROG_WEBUI_HTTP_FLASH friendlyTitle(const char *id) const
    {
        if (strcmp(id, "main") == 0) return "Главная";
        if (strcmp(id, "wifi") == 0) return "Wi‑Fi";
        if (strcmp(id, "access-point") == 0) return "Точка доступа";
        if (strcmp(id, "wifi-scanner") == 0) return "Сканер Wi‑Fi";
        return id;
    }

    void FLPROG_WEBUI_HTTP_FLASH publishText(const char *id, const String &value)
    {
        const int16_t index = model.indexOf(id);
        if (index >= 0) model.publishText((uint8_t)index, value.c_str());
    }

    bool FLPROG_WEBUI_HTTP_FLASH parseIp(const char *input, IPAddress &ip)
    {
        unsigned a, b, c, d;
        char trailing;
        if (!input || sscanf(input, "%u.%u.%u.%u%c", &a, &b, &c, &d, &trailing) != 4 || a > 255 || b > 255 || c > 255 || d > 255) return false;
        ip = IPAddress(a, b, c, d);
        return true;
    }

    bool FLPROG_WEBUI_HTTP_FLASH applyStaSettings()
    {
        if (!network) return false;
        const int16_t dhcpIndex = model.indexOf("network_dhcp");
        const bool dhcp = dhcpIndex >= 0 && model.boolAt((uint8_t)dhcpIndex);
        if (!dhcp)
        {
            IPAddress ip, gateway, subnet, dns;
            int16_t index = model.indexOf("network_ip_config"); if (index < 0 || !parseIp(model.textAt((uint8_t)index), ip)) return false;
            index = model.indexOf("network_gateway_config"); if (index < 0 || !parseIp(model.textAt((uint8_t)index), gateway)) return false;
            index = model.indexOf("network_subnet_config"); if (index < 0 || !parseIp(model.textAt((uint8_t)index), subnet)) return false;
            index = model.indexOf("network_dns"); if (index < 0 || !parseIp(model.textAt((uint8_t)index), dns)) return false;
            network->resetDhcp(); network->localIP(ip); network->gateway(gateway); network->subnet(subnet); network->dns(dns);
        }
        else network->setDhcp();
        network->disconnect();
        network->connect();
        settingsLoaded = false;
        return true;
    }

    bool FLPROG_WEBUI_HTTP_FLASH applyApSettings()
    {
        if (!network || !FLProgNetworkInterface::platformCapabilities().wifiApCompiled) return false;
        int16_t index = model.indexOf("ap_ssid");
        if (index < 0) return false;
        const String ssid = model.textAt((uint8_t)index);
        if (ssid.length() == 0 || ssid.length() > 32) return false;
        IPAddress ip, gateway, subnet;
        index = model.indexOf("ap_ip"); if (index < 0 || !parseIp(model.textAt((uint8_t)index), ip)) return false;
        index = model.indexOf("ap_gateway"); if (index < 0 || !parseIp(model.textAt((uint8_t)index), gateway)) return false;
        index = model.indexOf("ap_subnet"); if (index < 0 || !parseIp(model.textAt((uint8_t)index), subnet)) return false;
        const int16_t passwordIndex = model.indexOf("ap_password");
        const String password = passwordIndex < 0 ? String() : String(model.textAt((uint8_t)passwordIndex));
        if (password.length() && (password.length() < 8 || password.length() > 63)) return false;
        const int16_t channelIndex = model.indexOf("ap_channel"), clientsIndex = model.indexOf("ap_max_clients");
        const int16_t hiddenIndex = model.indexOf("ap_hidden"), enabledIndex = model.indexOf("ap_enabled");
        const uint8_t channel = channelIndex < 0 ? 1 : (uint8_t)model.intAt((uint8_t)channelIndex);
        const uint8_t clients = clientsIndex < 0 ? 4 : (uint8_t)model.intAt((uint8_t)clientsIndex);
        if (channel < 1 || channel > 13 || clients < 1 || clients > FLProgNetworkInterface::accessPointMaxClientsLimit()) return false;
        network->setAccessPointSsid(ssid);
        // Blank means “keep existing”: a password is never published or read.
        if (password.length()) network->setAccessPointPassword(password);
        network->setAccessPointChannel(channel);
        network->setAccessPointHidden(hiddenIndex >= 0 && model.boolAt((uint8_t)hiddenIndex));
        network->setAccessPointMaxClients(clients);
        network->setAccessPointIP(ip); network->setAccessPointGateway(gateway); network->setAccessPointSubnet(subnet);
        network->accessPointMode(enabledIndex >= 0 && model.boolAt((uint8_t)enabledIndex));
        apSettingsLoaded = false;
        return true;
    }

    void FLPROG_WEBUI_HTTP_FLASH syncSystem()
    {
        if (!network) return;
        publishText("network_ip", network->localIP().toString());
        publishText("network_gateway", network->gateway().toString());
        publishText("network_subnet", network->subnet().toString());
        publishText("wifi_ssid", network->clientSsid());
        int16_t index = model.indexOf("network_ready"); if (index >= 0) model.publishBool((uint8_t)index, network->isReady());
        index = model.indexOf("wifi_rssi"); if (index >= 0) model.publishInt((uint8_t)index, network->rssi());
        uint8_t *mac = network->mac(); char macText[18];
        snprintf(macText, sizeof(macText), "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
        publishText("network_mac", String(macText));
        if (!settingsLoaded)
        {
            publishText("network_ip_config", network->localIP().toString());
            publishText("network_gateway_config", network->gateway().toString());
            publishText("network_subnet_config", network->subnet().toString());
            publishText("network_dns", network->dns().toString());
            index = model.indexOf("network_dhcp"); if (index >= 0) model.publishBool((uint8_t)index, network->isDhcp());
            settingsLoaded = true;
        }
        if (!FLProgNetworkInterface::platformCapabilities().wifiApCompiled) return;
        index = model.indexOf("ap_ready"); if (index >= 0) model.publishBool((uint8_t)index, network->accessPointIsReady());
        index = model.indexOf("ap_station_count"); if (index >= 0) model.publishInt((uint8_t)index, network->accessPointStationCount());
        index = model.indexOf("ap_pending"); if (index >= 0) model.publishBool((uint8_t)index, network->accessPointConfigurationPending());
        index = model.indexOf("ap_error"); if (index >= 0) model.publishInt((uint8_t)index, network->accessPointLastError());
        publishText("ap_live_ip", network->accessPointIP().toString());
        if (!apSettingsLoaded)
        {
            publishText("ap_ssid", network->accessPointSsid());
            publishText("ap_ip", network->accessPointConfiguredIP().toString());
            publishText("ap_gateway", network->accessPointConfiguredGateway().toString());
            publishText("ap_subnet", network->accessPointConfiguredSubnet().toString());
            index = model.indexOf("ap_enabled"); if (index >= 0) model.publishBool((uint8_t)index, network->accessPointMode());
            index = model.indexOf("ap_channel"); if (index >= 0) model.publishInt((uint8_t)index, network->accessPointChannel());
            index = model.indexOf("ap_hidden"); if (index >= 0) model.publishBool((uint8_t)index, network->accessPointHidden());
            index = model.indexOf("ap_max_clients"); if (index >= 0) model.publishInt((uint8_t)index, network->accessPointMaxClients());
            apSettingsLoaded = true;
        }
    }

    FLProgWebUiModel &model;
    FLProgWebUiHttpProtocol api;
    const FLProgWebUiWidgetDescriptor *widgets;
    uint8_t widgetCount;
    const FLProgWebUiPageDescriptor *pages;
    uint8_t pageCount;
    const FLProgWebUiThemeDescriptor &theme;
    FLProgNetworkInterface *network;
    bool settingsLoaded;
    bool apSettingsLoaded;
    FLProgNetworkHttpServer server;
    char buffer[FLPROG_WEBUI_FLPROG_HTTP_BUFFER_SIZE];
};
#undef FLPROG_WEBUI_HTTP_FLASH
#undef FLPROG_WEBUI_HTTP_STRINGIFY
#undef FLPROG_WEBUI_HTTP_STRINGIFY_INNER
