"""Read-only FLProg identification and Arduino OTA DNS-SD discovery."""
import concurrent.futures
import ipaddress
import socket
import select
import struct
import time

def probe(host, port, timeout=0.8):
    try:
        with socket.create_connection((host, port), timeout) as client:
            client.settimeout(timeout)
            client.sendall(b'FLPINFO?')
            data = b''
            while len(data) < 24:
                try:
                    chunk = client.recv(24-len(data))
                except socket.timeout:
                    if data: return None
                    # Old receivers wait for a 48-byte header. Complete the
                    # unsupported FLPINFO? header with zeros. Magic validation
                    # rejects it BEFORE authentication, erase or transfer start.
                    # Never send a valid upload header as a discovery probe.
                    client.sendall(bytes(40))
                    reply = b''
                    while len(reply) < 4:
                        part = client.recv(4-len(reply))
                        if not part: return None
                        reply += part
                    if reply == b'ERR!':
                        return dict(ip=host, port=port, service='FLProg OTA? / legacy',
                                    detail='Ответ ERR! старого протокола; модель не определена. Проверка может увеличить счётчик ошибок OTA.')
                    return None
                if not chunk: return None
                data += chunk
            if data[:8] != b'FLPOTA2\0': return None
            layout, flash, address, maximum = struct.unpack('<IIII', data[8:])
            if layout not in (1, 2, 3, 4) or not 0x08000000 < address < 0x08200000:
                return None
            detail = 'Layout {}; Flash {} KiB; app 0x{:08X}; max {} KiB'.format(layout,flash//1024,address,maximum//1024)
            extra = b''
            try:
                while len(extra) < 84:
                    chunk = client.recv(84-len(extra))
                    if not chunk: break
                    extra += chunk
            except socket.timeout:
                pass
            if len(extra) == 84 and extra[:4] == b'ID01':
                model = extra[4:52].split(b'\0',1)[0].decode('utf-8',errors='replace')
                version = extra[52:84].split(b'\0',1)[0].decode('utf-8',errors='replace')
                detail = '{}; версия: {}; {}'.format(model or 'Модель не задана',version or 'не задана',detail)
            return dict(ip=host, port=port, service='FLProg OTA', detail=detail)
    except (OSError, ValueError): return None

def dns_name(packet, start):
    labels=[]; pos=start; end=None; seen=set()
    for _ in range(128):
        if pos in seen or pos>=len(packet): raise ValueError('Invalid DNS name')
        seen.add(pos); length=packet[pos]; pos+=1
        if length & 0xC0 == 0xC0:
            if pos>=len(packet): raise ValueError('Invalid DNS pointer')
            if end is None: end=pos+1
            pos=((length&63)<<8)|packet[pos]; continue
        if length==0: return '.'.join(labels).lower(), end if end is not None else pos
        if length>63 or pos+length>len(packet): raise ValueError('Invalid DNS label')
        labels.append(packet[pos:pos+length].decode('ascii',errors='replace')); pos+=length
    raise ValueError('DNS name too long')

def mdns_records(packet, source):
    if len(packet)<12: return []
    _,flags,questions,answers,authority,additional=struct.unpack('!6H',packet[:12])
    if not flags&0x8000: return []
    pos=12; result=[]
    try:
        for _ in range(questions): _,pos=dns_name(packet,pos); pos+=4
        for _ in range(answers+authority+additional):
            name,pos=dns_name(packet,pos)
            kind,cls,ttl,size=struct.unpack_from('!HHIH',packet,pos); pos+=10
            if pos+size>len(packet): return []
            if kind==33 and ttl and name.endswith('._arduino._tcp.local') and size>=7:
                port=struct.unpack_from('!H',packet,pos+4)[0]
                if port: result.append(dict(ip=source,port=port,service='Arduino OTA / mDNS',detail=name))
            pos+=size
    except (ValueError,struct.error,IndexError): return []
    return result

def browse_mdns(network, found, stop, warning, seconds=4):
    # QM listens for multicast replies; QU also asks for a unicast response.
    # A separate ephemeral socket avoids sharing Windows UDP 5353 delivery
    # with Arduino IDE/Bonjour. Direct DNS-SD queries work when multicast
    # responses do not reach this process. No OTA upload packets are sent.
    question=b'\x08_arduino\x04_tcp\x05local\0'
    header=struct.pack('!6H',0,0,1,0,0,0)
    multicast_query=header+question+struct.pack('!HH',12,1)
    unicast_query=header+question+struct.pack('!HH',12,0x8001)
    sockets=[];seen=set()
    try:
        direct=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        sockets.append(direct);direct.bind(('',0))
        direct.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,255)
        addresses={'0.0.0.0'}
        try:
            addresses.update(entry[4][0] for entry in socket.getaddrinfo(socket.gethostname(),None,socket.AF_INET)
                             if ipaddress.ip_address(entry[4][0]) in network)
        except OSError:pass
        multicast=None
        try:
            multicast=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
            multicast.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            multicast.bind(('',5353));sockets.append(multicast)
        except OSError as exc:
            if multicast is not None:multicast.close()
            multicast=None
            warning('Multicast mDNS недоступен; выполняется прямой поиск: '+str(exc))
        for address in sorted(addresses):
            if multicast is not None:
                try:
                    multicast.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,
                                         socket.inet_aton('224.0.0.251')+socket.inet_aton(address))
                    multicast.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_IF,socket.inet_aton(address))
                    multicast.sendto(multicast_query,('224.0.0.251',5353))
                except OSError:pass
            try:
                direct.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_IF,socket.inet_aton(address))
                direct.sendto(unicast_query,('224.0.0.251',5353))
            except OSError:pass
        # Restore normal routing after sending on each multicast interface.
        direct.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_IF,socket.inet_aton('0.0.0.0'))
        for host in network.hosts():
            if stop.is_set():return
            try:direct.sendto(unicast_query,(str(host),5353))
            except OSError:pass
        deadline=time.monotonic()+seconds
        while not stop.is_set() and time.monotonic()<deadline:
            ready,_,_=select.select(sockets,[],[],min(0.25,max(0,deadline-time.monotonic())))
            for sock in ready:
                try:packet,source=sock.recvfrom(9000)
                except OSError:continue
                if ipaddress.ip_address(source[0]) not in network:continue
                for row in mdns_records(packet,source[0]):
                    key=(row['ip'],row['port'],row['detail'])
                    if key not in seen:
                        seen.add(key);found(row)
    except OSError as exc:warning('mDNS недоступен: '+str(exc))
    finally:
        for sock in sockets:sock.close()

def scan(network, port, found, progress, stop, warning):
    network=ipaddress.ip_network(network,strict=False)
    if network.version!=4 or network.num_addresses>4096:
        raise ValueError('Выберите IPv4-подсеть не больше /20.')
    hosts=list(network.hosts())
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as pool:
        browse=pool.submit(browse_mdns,network,found,stop,warning)
        def check(host): return None if stop.is_set() else probe(str(host),port)
        jobs=[pool.submit(check,host) for host in hosts]
        completed=0
        for job in concurrent.futures.as_completed(jobs):
            row=job.result(); completed+=1
            if row: found(row)
            progress(completed,len(hosts))
        browse.result()
