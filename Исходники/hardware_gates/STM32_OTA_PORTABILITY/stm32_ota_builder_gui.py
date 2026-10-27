import contextlib
import os
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import build_stm32_ota as builder

ROOT = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
builder.ROOT = ROOT

class QueueWriter:
    def __init__(self, events): self.events = events
    def write(self, text):
        if text: self.events.put(('log', text))
    def flush(self): pass

def main():
    root = tk.Tk()
    root.title('FLProg — сборщик STM32 OTA и загрузчиков')
    root.geometry('900x590')
    events = queue.Queue()
    rows = builder.boards()
    names = sorted(rows)
    labels = [rows[name]['label'] + ' — ' + str(rows[name]['flash']//1024) + ' КБ Flash' for name in names]
    frame = ttk.Frame(root, padding=12); frame.pack(fill='both', expand=True)
    frame.columnconfigure(1, weight=1); frame.rowconfigure(6, weight=1)
    ttk.Label(frame, text='Плата FLProg:').grid(row=0, column=0, sticky='w')
    selected = ttk.Combobox(frame, values=labels, state='readonly'); selected.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5)
    selected.current(names.index('FLProg_FLE4_24_1'))
    ide = tk.StringVar(value=str(builder.IDE)); sketch = tk.StringVar()
    ttk.Label(frame, text='Папка Arduino IDE:').grid(row=1, column=0, sticky='w')
    ttk.Entry(frame, textvariable=ide).grid(row=1, column=1, sticky='ew')
    def choose_ide():
        value = filedialog.askdirectory(title='Папка с arduino-builder.exe')
        if value: ide.set(value)
    ttk.Button(frame, text='Выбрать…', command=choose_ide).grid(row=1, column=2)
    ttk.Label(frame, text='Скетч FLProg (.ino):').grid(row=2, column=0, sticky='w')
    ttk.Entry(frame, textvariable=sketch).grid(row=2, column=1, sticky='ew', pady=5)
    def choose_sketch():
        value = filedialog.askopenfilename(filetypes=[('Arduino sketch', '*.ino')])
        if value: sketch.set(value)
    ttk.Button(frame, text='Выбрать…', command=choose_sketch).grid(row=2, column=2)
    ttk.Label(frame, text='Загрузчик можно собрать без скетча. Для пакета нужен ваш проект с блоком OTA.').grid(row=3, column=0, columnspan=3, sticky='w', pady=8)
    actions = ttk.Frame(frame); actions.grid(row=4, column=0, columnspan=3, sticky='w')
    status = tk.StringVar(value='Готовые загрузчики находятся в папке bootloaders рядом с EXE.')
    ttk.Label(frame, textvariable=status, wraplength=850).grid(row=5, column=0, columnspan=3, sticky='w', pady=10)
    log = tk.Text(frame, wrap='word'); log.grid(row=6, column=0, columnspan=3, sticky='nsew')
    busy = [False]
    def start(loader_only):
        if busy[0]: return
        board = names[selected.current()]
        folder = Path(ide.get())
        if not (folder/'arduino-builder.exe').is_file():
            messagebox.showerror('Arduino IDE', 'Не найден arduino-builder.exe в выбранной папке.'); return
        source = None if loader_only else sketch.get()
        if not loader_only and not Path(source).is_file():
            messagebox.showerror('Скетч', 'Выберите экспортированный скетч FLProg с блоком OTA.'); return
        builder.IDE = folder
        builder.CORE = folder/'portable/packages/STMicroelectronics/hardware/stm32/3.0.0'
        busy[0] = True
        for button in build_buttons: button.configure(state='disabled')
        status.set('Сборка… Это может занять несколько минут.')
        log.insert('end', '\nСборка: ' + rows[board]['label'] + '\n')
        def work():
            try:
                with contextlib.redirect_stdout(QueueWriter(events)):
                    builder.install_profiles()
                    result = builder.build(board, source)
                events.put(('done', str(result.parent)))
            except Exception as exc: events.put(('error', str(exc)))
        threading.Thread(target=work, daemon=True).start()
    build_buttons = [ttk.Button(actions, text='Собрать загрузчик', command=lambda: start(True)),
                     ttk.Button(actions, text='Собрать BIN и пакет', command=lambda: start(False))]
    for button in build_buttons: button.pack(side='left', padx=3)
    def open_folder(name):
        folder=ROOT/name; folder.mkdir(exist_ok=True); os.startfile(str(folder))
    ttk.Button(actions, text='Готовые загрузчики', command=lambda: open_folder('bootloaders')).pack(side='left', padx=3)
    ttk.Button(actions, text='Результаты сборки', command=lambda: open_folder('output')).pack(side='left', padx=3)
    bottom = ttk.Frame(frame); bottom.grid(row=7, column=0, columnspan=3, sticky='w', pady=6)
    def copy_log():
        root.clipboard_clear(); root.clipboard_append(log.get('1.0', 'end-1c'))
    ttk.Button(bottom, text='Копировать лог', command=copy_log).pack(side='left')
    ttk.Button(bottom, text='Очистить лог', command=lambda: log.delete('1.0', 'end')).pack(side='left', padx=5)
    log.insert('end', 'Новые загрузчики F407 512 КБ и F103 256/512 КБ собраны, но ещё не проверены на платах.\n'
               'Выбирайте точную модель платы. Программа выполняет сборку; прошивка — через менеджер STM32 OTA.\n')
    def poll():
        try:
            while True:
                kind, text = events.get_nowait()
                if kind == 'log': log.insert('end', text); log.see('end')
                else:
                    busy[0] = False
                    for button in build_buttons: button.configure(state='normal')
                    status.set(('Сборка завершена: ' if kind == 'done' else 'Ошибка: ') + text)
                    log.insert('end', status.get()+'\n'); log.see('end')
        except queue.Empty: pass
        root.after(150, poll)
    def close():
        if busy[0]: messagebox.showinfo('Сборка', 'Дождитесь завершения сборки.'); return
        root.destroy()
    root.protocol('WM_DELETE_WINDOW', close); poll(); root.mainloop()

if __name__ == '__main__': main()
