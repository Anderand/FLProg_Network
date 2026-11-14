# coding: utf-8
"""Launch a separate portable Bridge; never opens a serial port itself."""
import os
import subprocess
from pathlib import Path


def find_bridge(home):
    home=Path(home).resolve()
    for folder in (home,home/'Мост_связи',home.parent/'Мост_связи',home.parent/'FLProg_Bridge'):
        candidate=folder/'FLProg_Bridge.exe'
        if candidate.is_file():return candidate
    # Development override, also useful to keep independently installed components.
    configured=os.environ.get('FLPROG_BRIDGE_EXE')
    if configured:
        candidate=Path(configured).resolve()
        if candidate.name.lower()=='flprog_bridge.exe' and candidate.is_file():return candidate
    raise FileNotFoundError('FLProg_Bridge.exe не найден. Поместите папку «Мост_связи» рядом с редактором или менеджером. Мост можно запустить отдельно.')


def tcp_endpoint(value):
    from urllib.parse import urlsplit
    value=value.strip()
    parts=urlsplit(value if value.startswith('tcp://') else 'tcp://'+value)
    try: number=parts.port
    except ValueError: raise ValueError('TCP-порт должен быть числом 1..65535')
    if parts.scheme!='tcp' or not parts.hostname or number is None or not 1<=number<=65535 or parts.username is not None or parts.password is not None or parts.path or parts.query or parts.fragment or any(c.isspace() for c in parts.hostname):
        raise ValueError('Укажите адрес ESP в формате IP:порт, например 192.168.1.50:3234')
    return value if value.startswith('tcp://') else 'tcp://'+value


def launch_bridge(home,port=None,baud=115200,site=None,tcp=None):
    if tcp is not None and port is not None:raise ValueError('Выберите один транспорт: COM или TCP')
    target=tcp_endpoint(tcp) if tcp is not None else None
    executable=find_bridge(home)
    args=[str(executable)]
    if target is not None:args+=['--tcp',target]
    if port is not None:
        import re
        if not re.fullmatch(r'COM[1-9][0-9]*',port,re.I):raise ValueError('Выберите COM-порт')
        if int(baud) not in (9600,19200,38400,57600,115200,230400,460800,921600):raise ValueError('Неверная скорость UART')
        args+=['--port',port,'--baud',str(int(baud))]
    if site:
        folder=Path(site).resolve()
        if not (folder/'bridge.json').is_file():raise ValueError('В папке веб-проекта нет bridge.json')
        args+=['--site',str(folder)]
    flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
    subprocess.Popen(args,cwd=str(executable.parent),creationflags=flags,
                     stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return str(executable)
