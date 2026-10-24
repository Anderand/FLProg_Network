import contextlib
import json
import os
from pathlib import Path
import threading
import time
import loader_batch
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import build_stm32_ota as builder
import ota_discovery

class Writer:
    def __init__(self, app): self.app=app
    def write(self, text):
        if text.strip(): self.app.events.put(('log',text.rstrip()))
    def flush(self): pass

def attach(app, notebook, home):
    builder.ROOT=home/'build_tools'
    rows=builder.boards(); names=sorted(rows)
    build=ttk.Frame(notebook,padding=14); notebook.add(build,text='Плата и сборка')
    build.columnconfigure(1,weight=1)
    board=ttk.Combobox(build,state='readonly',values=[rows[n]['label']+' / '+str(rows[n]['flash']//1024)+' KiB' for n in names])
    ttk.Label(build,text='Плата FLProg:').grid(row=0,column=0,sticky='w')
    board.grid(row=0,column=1,columnspan=2,sticky='ew',pady=5)
    ttk.Checkbutton(build,text='Показать непроверенные платы и профили',
                    variable=app.show_unverified,command=app._toggle_unverified).grid(row=9,column=0,columnspan=3,sticky='w')
    visible_names=[]
    ide=tk.StringVar(value=app.settings.get('builder_ide',str(builder.IDE)))
    sketch=tk.StringVar(value=app.settings.get('builder_sketch',''))
    app.builder_ide_var=ide; app.builder_sketch_var=sketch
    def choose(var, directory):
        value=filedialog.askdirectory() if directory else filedialog.askopenfilename(filetypes=[('Скетч FLProg','*.ino')])
        if value: var.set(value)
    for row,label,var,directory in [(1,'Arduino IDE:',ide,True),(2,'Скетч с OTA-блоком:',sketch,False)]:
        ttk.Label(build,text=label).grid(row=row,column=0,sticky='w')
        ttk.Entry(build,textvariable=var).grid(row=row,column=1,sticky='ew',pady=5)
        ttk.Button(build,text='Выбрать…',command=lambda v=var,d=directory:choose(v,d)).grid(row=row,column=2)
    mode=ttk.Combobox(build,state='readonly',values=['Только собрать','После сборки: обновить по OTA','После сборки: первая установка по SWD'])
    mode.current(0);mode.grid(row=3,column=0,columnspan=3,sticky='ew',pady=8)
    state=tk.StringVar(value='Выберите плату. Загрузчик собирается без скетча; пакет — с вашим .ino.')
    app.build_status=state
    ttk.Label(build,textvariable=state,wraplength=850).grid(row=5,column=0,columnspan=3,sticky='w',pady=10)
    progress=ttk.Progressbar(build,maximum=100)
    progress.grid(row=6,column=0,columnspan=3,sticky='ew')
    listing=ttk.Treeview(build,columns=('board','status','time','size'),show='headings',height=15)
    for key,label,width in [('board','Плата',350),('status','Результат',240),('time','Время',90),('size','BIN, байт',100)]:
        listing.heading(key,text=label);listing.column(key,width=width)
    listing.grid(row=7,column=0,columnspan=3,sticky='nsew');build.rowconfigure(7,weight=1)
    scrollbar=ttk.Scrollbar(build,orient='vertical',command=listing.yview)
    scrollbar.grid(row=7,column=3,sticky='ns');listing.configure(yscrollcommand=scrollbar.set)
    app.build_report=None
    report_file=builder.ROOT/'last_build_report.json'
    if report_file.exists():
        try: app.build_report=json.loads(report_file.read_text(encoding='utf-8'))
        except (ValueError,OSError): pass
    def refresh_loaders():
        report=app.build_report
        items=report['rows'] if report else {}
        now=time.time();counts={key:0 for key in ('queued','building','success','failed')}
        active=[]
        for n in names:
            if n not in visible_names:
                if listing.exists(n):listing.delete(n)
                continue
            item=items.get(n);file=builder.ROOT/'output'/n/'bootloader.bin'
            status='Есть файл (не эта сборка)' if file.exists() else 'Не собран'
            elapsed='';size=file.stat().st_size if file.exists() else ''
            if item:
                phase=item['status'];counts[phase]+=1
                status={'queued':'В очереди','building':'Собирается…','success':'Готово','failed':'ОШИБКА'}[phase]
                seconds=now-item['started'] if phase=='building' else item['seconds']
                elapsed='{}:{:02d}'.format(int(seconds)//60,int(seconds)%60) if item['started'] else ''
                size=item['size'] or ''
                if phase=='building': active.append(rows[n]['label'])
            values=(rows[n]['label'],status,elapsed,size)
            if listing.exists(n): listing.item(n,values=values)
            else: listing.insert('', 'end',iid=n,values=values)
        if report:
            total=len(items);done=counts['success']+counts['failed']
            progress.configure(value=100*done/max(1,total))
            seconds=int((report['finished'] or now)-report['started'])
            summary='Готово: {}/{} | Ошибок: {} | В очереди: {} | Время: {}:{:02d}'.format(counts['success'],total,counts['failed'],counts['queued'],seconds//60,seconds%60)
            state.set(('ИТОГ: ' if report['finished'] else '')+summary+('\nСейчас: '+', '.join(active) if active else ''))
    app.refresh_loaders=refresh_loaders
    def tick():
        refresh_loaders();app.root.after(1000,tick)
    tick()
    def show_log(_event=None):
        chosen=listing.selection()
        if not chosen:return
        path=builder.ROOT/'logs'/(chosen[0]+'_bootloader.log')
        if path.exists():os.startfile(str(path))
    listing.bind('<Double-1>',show_log)
    def start(kind):
        if app.busy: return
        if not app.show_unverified.get() or board.current()<0:
            messagebox.showinfo('Платы для испытаний','В каталоге сборки находятся непроверенные платы. Включите их показ. Проверенный FLE4D-30MT 1.0.1 доступен на вкладке «Прошивка».',parent=app.root);return
        folder=Path(ide.get());source=sketch.get(); selected=visible_names[board.current()]; action=mode.current()
        if not (folder/'arduino-builder.exe').exists():
            messagebox.showerror('IDE','Не найден arduino-builder.exe.',parent=app.root);return
        if kind=='package' and (not source or not Path(source).is_file()):
            messagebox.showerror('Скетч','Выберите свой .ino с блоком OTA.',parent=app.root);return
        builder.IDE=folder;builder.CORE=folder/'portable/packages/STMicroelectronics/hardware/stm32/3.0.0'
        app.busy=True;app._save_settings();state.set('Сборка… Подробности — в логе на вкладке «Прошивка».')
        def worker():
            try:
                with contextlib.redirect_stdout(Writer(app)):
                    builder.install_profiles()
                    targets=list(visible_names) if kind=='all' else [selected]
                    report=loader_batch.run(builder,targets,source if kind=='package' else None,
                        lambda value:app.events.put(('build_report',value)))
                failed=[n for n,item in report['rows'].items() if item['status']=='failed']
                if failed:
                    app.events.put(('build_failed',report))
                    return
                package=builder.ROOT/'output'/selected/(selected+'.fwpkg') if kind=='package' else None
                app.events.put(('build_complete',(str(package) if package else '',action if package else 0)))
            except Exception as exc:
                app.events.put(('build_status','Ошибка сборки: '+str(exc)))
                app.events.put(('error',str(exc)))
        threading.Thread(target=worker,daemon=True).start()
    app.start_build=start
    buttons=ttk.Frame(build);buttons.grid(row=4,column=0,columnspan=3,sticky='w')
    for text,kind in [('Собрать загрузчик','loader'),('Собрать BIN и пакет','package'),('Собрать все загрузчики','all')]:
        ttk.Button(buttons,text=text,command=lambda k=kind:start(k)).pack(side='left',padx=3)
    def open_output():
        if board.current()<0:return
        folder=builder.ROOT/'output'/visible_names[board.current()];folder.mkdir(parents=True,exist_ok=True);os.startfile(str(folder))
    ttk.Button(buttons,text='Файлы платы',command=open_output).pack(side='left',padx=3)
    def select_board_profile():
        if app.busy or board.current()<0 or not app.show_unverified.get():return
        profile_id='board_'+visible_names[board.current()].lower()
        app._refresh_profiles(profile_id)
        app.bin_var.set('');app._save_settings();notebook.select(0)
        app._log('Выбран профиль платы. Загрузчик готов; выберите OTA BIN вашего проекта или соберите пакет на вкладке «Плата и сборка».')
    ttk.Button(buttons,text='Выбрать профиль платы',command=select_board_profile).pack(side='left',padx=3)
    ttk.Label(build,text='Проверенный FLE4D-30MT 1.0.1 — на вкладке «Прошивка». Каталог сборки содержит платы для испытаний; включите галочку, чтобы их выбрать. SPI/Ethernet задаются в проекте FLProg.',wraplength=850).grid(row=8,column=0,columnspan=3,sticky='w',pady=8)
    def refresh_board_choices():
        previous=visible_names[board.current()] if 0<=board.current()<len(visible_names) else None
        visible_names[:]=names if app.show_unverified.get() else []
        board['values']=[rows[n]['label']+' / '+str(rows[n]['flash']//1024)+' KiB — не проверена' for n in visible_names]
        if visible_names:board.current(visible_names.index(previous) if previous in visible_names else 0)
        else:board.set('')
        for button in buttons.winfo_children():button.configure(state='normal' if visible_names else 'disabled')
        refresh_loaders()
    app.refresh_board_choices=refresh_board_choices
    refresh_board_choices()

    scanner=ttk.Frame(notebook,padding=14);notebook.add(scanner,text='Поиск OTA')
    subnet=tk.StringVar(value='192.168.100.0/24');port=tk.StringVar(value='3233')
    controls=ttk.Frame(scanner);controls.pack(fill='x')
    ttk.Label(controls,text='Подсеть:').pack(side='left');ttk.Entry(controls,textvariable=subnet,width=23).pack(side='left',padx=5)
    ttk.Label(controls,text='Порт FLProg OTA:').pack(side='left');ttk.Entry(controls,textvariable=port,width=7).pack(side='left',padx=5)
    app.scan_status=tk.StringVar(value='Показываются ответы FLProg OTA и объявления Arduino OTA через mDNS.')
    ttk.Label(scanner,textvariable=app.scan_status,wraplength=850).pack(fill='x',pady=10)
    app.scan_progress=ttk.Progressbar(scanner,maximum=100);app.scan_progress.pack(fill='x')
    tree=ttk.Treeview(scanner,columns=('ip','port','service','detail'),show='headings')
    for key,label,width in [('ip','IP',140),('port','Порт',65),('service','Обнаружение',180),('detail','Сведения',430)]:
        tree.heading(key,text=label);tree.column(key,width=width)
    tree.pack(fill='both',expand=True,pady=8);app.scan_tree=tree;app.scan_rows={};app.scan_items={};app.scan_stop=threading.Event()
    def start_scan():
        if app.busy:return
        try:
            import ipaddress
            network=ipaddress.ip_network(subnet.get(),strict=False);p=int(port.get())
            if network.version!=4 or network.num_addresses>4096 or not 1<=p<=65535:raise ValueError()
        except ValueError:
            messagebox.showerror('Сеть','Укажите IPv4-подсеть /20 или меньше и порт 1–65535.');return
        app.busy=True;app.scan_stop.clear();app.scan_rows.clear();app.scan_items.clear()
        for item in tree.get_children():tree.delete(item)
        app.scan_status.set('Поиск OTA…');app.scan_progress.configure(value=0)
        def worker():
            try:
                ota_discovery.scan(str(network),p,lambda row:app.events.put(('scan_found',row)),
                    lambda done,total:app.events.put(('scan_progress',(done,total))),app.scan_stop,
                    lambda message:app.events.put(('log',message)))
                app.events.put(('scan_done',None))
            except Exception as exc:app.events.put(('error',str(exc)))
        threading.Thread(target=worker,daemon=True).start()
    ttk.Button(controls,text='Найти OTA',command=start_scan).pack(side='left',padx=5)
    ttk.Button(controls,text='Остановить',command=app.scan_stop.set).pack(side='left')
    def use_selected(_event=None):
        selection=tree.selection()
        if not selection:return
        row=app.scan_rows[tree.item(selection[0],'text')]
        try: expected=int(app._selected()[2]['ota']['port'])
        except ValueError:expected=3233
        if row['port']!=expected:
            messagebox.showinfo('Другой OTA-протокол','Порт устройства отличается от порта выбранного профиля. Выберите совместимый профиль.');return
        app.ip_var.set(row['ip']);app._save_settings();notebook.select(0)
        app._log('Выбрано OTA-устройство: {}:{}'.format(row['ip'],row['port']))
    tree.bind('<Double-1>',use_selected)
    selected_detail=tk.StringVar()
    def show_detail(_event=None):
        selection=tree.selection()
        selected_detail.set(tree.item(selection[0],'values')[3] if selection else '')
    tree.bind('<<TreeviewSelect>>',show_detail)
    ttk.Label(scanner,textvariable=selected_detail,wraplength=850).pack(fill='x',pady=5)
    ttk.Button(scanner,text='Использовать выбранный IP',command=use_selected).pack(anchor='w')
    ttk.Label(scanner,text='Legacy: предположительно старый FLProg OTA по ответу ERR!. Такая проверка не пишет Flash, но может увеличить счётчик ошибок OTA. Открытый порт без ответа не показывается.',wraplength=850).pack(fill='x',pady=8)

def event(app,kind,payload,import_package):
    if kind=='build_report':
        app.build_report=payload;app.refresh_loaders()
    elif kind=='build_failed':
        app._set_idle();app.build_report=payload;app.refresh_loaders()
        failed=[n for n,item in payload['rows'].items() if item['status']=='failed']
        app._set_result('Сборка завершена. Ошибок: '+str(len(failed)), '#a00000')
        for name in failed:app._log(name+': '+payload['rows'][name]['error'])
    elif kind=='build_status':app.build_status.set(payload)
    elif kind=='build_complete':
        package,action=payload;app._set_idle();app.refresh_loaders()
        if package:
            folder=import_package(package,app.profiles_dir)
            app._refresh_profiles(folder.name);app.bin_var.set('');app._save_settings()
            if folder.name not in app.profiles:
                app.build_status.set('Пакет собран и импортирован. Для выбора включите показ непроверенных плат.')
                app._set_result('Пакет собран; автоматическая прошивка не выполнялась.', '#176b2c')
                return
            app.build_status.set('Готово. Пакет выбран на вкладке «Прошивка».')
            app._set_result('УСПЕХ: загрузчик и приложение собраны; пакет выбран.', '#176b2c')
            app._log('Сборка завершена, выбран пакет: '+package)
            app.notebook.select(0)
            if action:app._start('ota' if action==1 else 'swd')
        else:
            app.refresh_loaders()
            app._set_result('УСПЕХ: сборка загрузчиков завершена.', '#176b2c')
            app._log('РЕЗУЛЬТАТ: сборка загрузчиков завершена.')
    elif kind=='scan_found':
        key='{}:{}'.format(payload['ip'],payload['port'])
        old=app.scan_rows.get(key)
        priority={'FLProg OTA':3,'Arduino OTA / mDNS':2,'FLProg OTA? / legacy':1}
        if old and priority.get(old['service'],0)>=priority.get(payload['service'],0):return
        app.scan_rows[key]=payload
        values=tuple(payload[k] for k in ('ip','port','service','detail'))
        if key in app.scan_items:app.scan_tree.item(app.scan_items[key],values=values)
        else:app.scan_items[key]=app.scan_tree.insert('', 'end',text=key,values=values)
    elif kind=='scan_progress':
        done,total=payload;app.scan_progress.configure(value=100*done/max(1,total))
        app.scan_status.set('Проверено {}/{}. Найдено OTA: {}'.format(done,total,len(app.scan_rows)))
    elif kind=='scan_done':
        app.scan_status.set(('Остановлено' if app.scan_stop.is_set() else 'Поиск завершён')+'. Найдено OTA: '+str(len(app.scan_rows)))
        app._set_idle()
