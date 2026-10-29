# coding: utf-8
"""Portable standalone FLProg Bridge; no dependency on editor or manager."""
import argparse
import json
import queue
import sys
import threading
import time
import webbrowser
from pathlib import Path
from client import Client, BridgeError
from demo import DemoPort
from http_api import State, make_server, VERSION
from device_web import synchronize

def serial_port(name,baud):
    import serial
    port=serial.Serial(port=None,baudrate=baud,timeout=0.03,write_timeout=0.3)
    port.dtr=False;port.rts=False;port.port=name
    port.open();return port

def open_transport(name,baud):
    if name.startswith('tcp://'):
        from tcp_port import TcpPort
        return TcpPort(name)
    return serial_port(name,baud)


def arguments():
    p=argparse.ArgumentParser(description='FLProg Bridge — самостоятельный мост связи COM ↔ HTTP API')
    p.add_argument('--port',help='Явно выбранный COM-порт; без параметра порт не открывается')
    p.add_argument('--tcp',help='Явно выбранный ESP-мост: IP:порт (прототип TCP ↔ UART)')
    p.add_argument('--baud',type=int,default=115200,choices=[9600,19200,38400,57600,115200,230400,460800,921600])
    p.add_argument('--http-port',type=int,default=0,help='0 — свободный локальный порт')
    p.add_argument('--site',type=Path,help='Папка статического сайта с bridge.json')
    p.add_argument('--demo',action='store_true',help='Эмулятор без доступа к COM')
    p.add_argument('--demo-tcp',action='store_true',help='Демо ESP/ПЛК через локальный TCP без аппаратуры')
    p.add_argument('--allow-writes',action='store_true',help='Разрешить команды; политика ПЛК также должна их разрешать')
    p.add_argument('--headless',action='store_true');p.add_argument('--no-browser',action='store_true')
    p.add_argument('--no-reconnect',action='store_true',help='Отключить восстановление сеанса после потери связи')
    p.add_argument('--status-file',type=Path,help='Записать фактический локальный URL после запуска')
    args=p.parse_args()
    if args.demo_tcp and (args.port or args.tcp or args.demo or args.site):
        p.error('--demo-tcp использует только локальные демонстрационные каналы; не сочетайте с COM, ESP или папкой сайта')
    if args.tcp:
        if args.port or args.demo:p.error('--tcp нельзя сочетать с --port или --demo')
        from tcp_port import endpoint
        try:endpoint(args.tcp)
        except ValueError as error:p.error(str(error))
        args.port=args.tcp if args.tcp.startswith('tcp://') else 'tcp://'+args.tcp
    if args.demo and args.port:p.error('--demo и --port несовместимы')
    if not 0<=args.http_port<=65535:p.error('HTTP-порт: 0..65535')
    return args


class Window:
    def __init__(self,state,server,args):
        import tkinter as tk
        from tkinter import ttk
        self.tk=tk;self.state=state;self.server=server;self.events=queue.Queue();self.connecting=False;self.shown_session=0;self.demo_tcp=None
        self.root=tk.Tk();self.root.title('FLProg — Мост связи '+VERSION);self.root.geometry('800x630');self.root.minsize(740,590)
        body=ttk.Frame(self.root,padding=20);body.pack(fill='both',expand=True);body.columnconfigure(1,weight=1)
        ttk.Label(body,text='Мост связи',font=('Segoe UI',18,'bold')).grid(row=0,column=0,columnspan=3,sticky='w')
        ttk.Label(body,text='Самостоятельный COM / TCP ↔ HTTP мост. Редактор для работы не нужен.').grid(row=1,column=0,columnspan=3,sticky='w',pady=(4,18))
        self.port=tk.StringVar(value=args.port or '');self.baud=tk.StringVar(value=str(args.baud));self.writes=tk.BooleanVar(value=args.allow_writes)
        ttk.Label(body,text='COM или tcp://IP:порт:').grid(row=2,column=0,sticky='w')
        self.ports=ttk.Combobox(body,textvariable=self.port);self.ports.grid(row=2,column=1,sticky='ew',padx=8)
        ttk.Button(body,text='Обновить список',command=self.refresh).grid(row=2,column=2)
        ttk.Label(body,text='Скорость:').grid(row=3,column=0,sticky='w',pady=10)
        ttk.Combobox(body,textvariable=self.baud,state='readonly',values=[9600,19200,38400,57600,115200,230400,460800,921600]).grid(row=3,column=1,sticky='ew',padx=8)
        buttons=ttk.Frame(body);buttons.grid(row=4,column=0,columnspan=3,sticky='ew',pady=8)
        self.connect_button=ttk.Button(buttons,text='Подключить',command=lambda:self.connect(False));self.connect_button.pack(side='left')
        self.disconnect_button=ttk.Button(buttons,text='Отключить',command=self.disconnect);self.disconnect_button.pack(side='left',padx=6)
        self.demo_button=ttk.Button(buttons,text='Демо без контроллера',command=lambda:self.connect(True));self.demo_button.pack(side='left')
        self.tcp_demo_button=ttk.Button(buttons,text='Демо TCP/ESP',command=lambda:self.connect(False,True));self.tcp_demo_button.pack(side='left',padx=6)
        ttk.Button(buttons,text='Обрыв демо',command=self.drop_demo).pack(side='left')
        options=ttk.Frame(body);options.grid(row=5,column=0,columnspan=3,sticky='w',pady=8)
        ttk.Checkbutton(options,text='Разрешить команды',variable=self.writes,command=self.update_writes).pack(side='left')
        self.reconnect=tk.BooleanVar(value=state.auto_reconnect)
        ttk.Checkbutton(options,text='Восстанавливать связь автоматически',variable=self.reconnect,command=lambda:setattr(self.state,'auto_reconnect',self.reconnect.get())).pack(side='left',padx=18)
        self.mute_demo=tk.BooleanVar(value=False)
        ttk.Checkbutton(options,text='ПЛК молчит (демо)',variable=self.mute_demo,command=self.set_demo_mute).pack(side='left')
        self.status=tk.StringVar(value='COM-порт не открыт. Выберите порт или запустите демо.')
        ttk.Label(body,textvariable=self.status,wraplength=700).grid(row=6,column=0,columnspan=3,sticky='w',pady=10)
        self.url='http://127.0.0.1:'+str(server.server_port)+'/'
        ttk.Button(body,text='Открыть веб-интерфейс',command=lambda:webbrowser.open(self.url)).grid(row=7,column=0,columnspan=3,sticky='ew',pady=8)
        ttk.Label(body,text=self.url).grid(row=8,column=0,columnspan=3,sticky='w')
        ttk.Label(body,text='Резервный веб:').grid(row=9,column=0,sticky='w',pady=12)
        self.site=tk.StringVar(value=str(state.site) if state.site else '')
        ttk.Entry(body,textvariable=self.site,state='readonly').grid(row=9,column=1,sticky='ew',padx=8)
        ttk.Button(body,text='Выбрать папку…',command=self.choose_site).grid(row=9,column=2)
        ttk.Label(body,text='Новая прошивка: веб автоматически загружается из Flash ПЛК по UART, папка на ПК не нужна.\nДля прежней прошивки можно выбрать резервную папку с bridge.json. Проверяются ID/API/SHA-256.',wraplength=740).grid(row=10,column=0,columnspan=3,sticky='w',pady=8)
        self.log=tk.Text(body,height=5,wrap='word');self.log.grid(row=11,column=0,columnspan=3,sticky='nsew');body.rowconfigure(11,weight=1)
        self.root.protocol('WM_DELETE_WINDOW',self.close);self.root.after(100,self.drain);self.refresh()
        if args.port or args.demo or args.demo_tcp:self.root.after(100,lambda:self.connect(args.demo,args.demo_tcp))

    def refresh(self):
        from serial.tools import list_ports
        self.ports['values']=[p.device for p in list_ports.comports()]

    def update_writes(self):self.state.allow_writes=self.writes.get()

    def choose_site(self):
        if self.connecting or self.state.client:
            self.status.set('Перед сменой веб-проекта отключите COM.');return
        from tkinter import filedialog
        value=filedialog.askdirectory(parent=self.root,title='Папка веб-проекта с bridge.json')
        if not value:return
        try:
            selected=State(value,self.state.allow_writes)
            self.state.site=selected.site;self.state.manifest=selected.manifest;self.state.project=selected.project;self.state.resources=selected.resources
            self.state.fallbackSite=selected.site;self.state.webSource='local';self.state.resourceReport=None
            self.site.set(str(selected.site));self.status.set('Веб-проект выбран. Подключитесь через COM или TCP для проверки соответствия ПЛК.')
        except Exception as e:self.status.set('Ошибка веб-проекта: '+str(e))

    def disconnect(self):
        if self.connecting:return
        c=self.state.client;self.state.client=None
        if c:threading.Thread(target=c.close,daemon=True).start()
        if self.demo_tcp:
            endpoint=self.demo_tcp.endpoint;self.demo_tcp.close();self.demo_tcp=None
            if self.port.get()==endpoint:self.port.set('')
        self.status.set('Отключено. Для команд после подключения нужно заново прочитать данные.')

    def drop_demo(self):
        if not self.demo_tcp:self.status.set('Обрыв доступен только в режиме «Демо TCP/ESP».');return
        self.demo_tcp.drop_clients();self.status.set('ДЕМО: TCP-связь прервана. Ожидается новый сеанс, команды не повторяются.')

    def set_demo_mute(self):
        if self.demo_tcp:self.demo_tcp.muted=self.mute_demo.get()

    def connect(self,demo,tcp_demo=False):
        if self.connecting:return
        port=self.port.get().strip()
        if not (demo or tcp_demo) and not port:self.status.set('Выберите COM-порт или введите tcp://IP:порт.');return
        if (demo or tcp_demo) and self.state.site:self.status.set('Демо каналов доступно при запуске без папки сайта. Для своего проекта подключите ПЛК.');return
        self.disconnect();self.connecting=True
        for b in (self.connect_button,self.disconnect_button,self.demo_button,self.tcp_demo_button):b.configure(state='disabled')
        baud=int(self.baud.get());self.status.set('Подключение к локальному TCP-эмулятору…' if tcp_demo else 'Подключение к эмулятору…' if demo else 'Подключение '+port+'…')
        def worker():
            c=None;sim=None;opened=False
            try:
                if tcp_demo:
                    from demo_tcp import DemoTcpServer
                    sim=DemoTcpServer()
                c=Client(DemoPort() if demo else open_transport(sim.endpoint if sim else port,baud));opened=True;info=c.handshake()
                if sim:sim.muted=self.demo_mute_value
                if not (demo or tcp_demo):synchronize(self.state,c,lambda done,total:self.events.put(('resource_progress',(done,total))))
                self.events.put(('connected',(c,info,demo or tcp_demo,sim)))
            except Exception as e:
                if c:c.close()
                if sim:sim.close()
                message=str(e)
                if port.startswith('tcp://') and not opened:message='TCP-порт моста недоступен. Проверьте IP, порт и сеть. '+message
                self.events.put(('error',message))
        self.demo_mute_value=self.mute_demo.get()
        threading.Thread(target=worker,daemon=True).start()

    def drain(self):
        while not self.events.empty():
            kind,data=self.events.get()
            if kind=='resource_progress':
                done,total=data;self.status.set('Веб из Flash ПЛК: '+str(done*100//total)+'% ('+str(done)+' / '+str(total)+' байт)');continue
            self.connecting=False
            for b in (self.connect_button,self.disconnect_button,self.demo_button,self.tcp_demo_button):b.configure(state='normal')
            if kind=='connected':
                c,info,demo,sim=data;self.state.client=c;self.state.demo=demo;self.demo_tcp=sim
                if sim:self.port.set(sim.endpoint)
                self.shown_session=c.session
                identity=info.get('identity',{})
                services=', '.join({1:'WebUI',2:'Modbus',3:'MQTT',4:'Ресурсы из Flash'}.get(i,'Служба '+str(i)) for i in info['services'])
                text=('ДЕМО TCP/ESP: только localhost, ESP и ПЛК не используются. ' if sim else 'ДЕМО БЕЗ КОНТРОЛЛЕРА. ' if demo else 'Связь установлена. ')
                text+='Модель: {} · проект: {} · версия: {}\nДоступно: {}'.format(identity.get('model','—'),identity.get('projectId','—'),identity.get('firmware','—'),services or 'нет служб')
                if self.state.site:
                    try:self.state.active();text+='\nВеб-проект соответствует прошивке.'
                    except BridgeError as error:text+='\n'+str(error)
                if self.state.webSource=='device':text+='\nВеб получен с ПЛК'+(' (проверенный кеш).' if self.state.resourceReport['cacheHit'] else ' по UART.')
            else:text='Ошибка: '+data
            self.status.set(text);self.log.insert('end',text+'\n');self.log.see('end')
        if self.state.client and not self.state.client.online:self.status.set(self.state.client.last_error or 'Связь потеряна. Подключитесь заново.')
        if self.state.client and self.state.client.online and self.shown_session!=self.state.client.session:
            c=self.state.client;self.shown_session=c.session
            text='Связь восстановлена. Команды не повторялись; веб заново прочитает данные ПЛК.'
            try:self.state.active()
            except BridgeError as error:text+='\n'+str(error)
            self.status.set(text);self.log.insert('end',text+'\n');self.log.see('end')
        self.root.after(100,self.drain)

    def close(self):
        # No automatic upload; background workers terminate with this process.
        if self.demo_tcp:self.demo_tcp.close();self.demo_tcp=None
        self.root.destroy()


def main():
    args=arguments();site=args.site if args.site and (args.site/'bridge.json').is_file() else None
    state=State(site,args.allow_writes);state.auto_reconnect=not args.no_reconnect;server=make_server(state,args.http_port)
    demo_server=None
    url='http://127.0.0.1:'+str(server.server_port)+'/'
    if args.headless and args.demo_tcp:
        from demo_tcp import DemoTcpServer
        demo_server=DemoTcpServer();args.port=demo_server.endpoint
    if args.headless and (args.port or args.demo):
        state.client=Client(DemoPort() if args.demo else open_transport(args.port,args.baud));state.client.handshake();state.demo=args.demo or args.demo_tcp
        if not state.demo:synchronize(state,state.client)
    if args.status_file:args.status_file.write_text(json.dumps(dict(url=url,version=VERSION,demo=bool(args.demo or args.demo_tcp))),encoding='utf-8')
    stop=threading.Event()
    def heartbeat():
        last_reconnect=0
        while not stop.wait(1.0):
            c=state.client
            if not c or c.lock.locked():continue
            if c.online:
                try:c.request(0,2)
                except BridgeError:pass
            elif state.auto_reconnect and time.monotonic()-last_reconnect>=2:
                last_reconnect=time.monotonic()
                try:
                    if hasattr(c.transport,'port'):
                        with c.lock:
                            c.transport.close();c.transport.open()
                    c.handshake();synchronize(state,c)
                except (BridgeError,OSError) as error:
                    c.online=False;c.last_error=str(error)
    threading.Thread(target=heartbeat,daemon=True).start()
    if args.headless:
        if sys.stdout:print(url,flush=True)
        if not args.no_browser:webbrowser.open(url)
        try:server.serve_forever()
        finally:
            stop.set()
            server.server_close()
            if state.client:state.client.close()
            if demo_server:demo_server.close()
    else:
        threading.Thread(target=server.serve_forever,daemon=True).start()
        ui=Window(state,server,args)
        try:ui.root.mainloop()
        finally:
            stop.set()
            server.shutdown();server.server_close()
            if state.client:state.client.close()


if __name__=='__main__':main()
