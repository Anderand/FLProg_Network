# coding: utf-8
"""Read the full web from a real PLC into a fresh cache, with Ethernet unplugged."""
from pathlib import Path
import hashlib,json,socket,sys,time
R=Path(__file__).resolve().parents[2];W=Path(r'E:\SAI\FLProg_Network\_work\bridge_flash_20261028')
sys.path[:0]=[str(R/'flprog_bridge'),str(Path(r'E:\SAI\FLProg_Network\_work\bridge_20261028\deps'))]
from app import serial_port
from client import Client
from device_web import device_site
cache=W/'offline_empty_cache';assert not cache.exists(),'Fresh cache required'
c=Client(serial_port('COM5',115200))
try:
    identity=c.handshake();assert identity['identity']['firmware']=='1.0.9-BRIDGE-FLASH' and 4 in identity['services']
    # Channel numbers come from our build contract, not a local website used by the bridge.
    doc=json.loads((W/'generated_site/project.json').read_text(encoding='utf-8'))
    indices={v['id']:v['index'] for v in doc['channels']}
    ids=('network_ready','network_ip','system_uptime')
    before=c.read_channels([indices[key] for key in ids])
    ethernet_reachable=False
    try:
        with socket.create_connection(('192.168.100.19',80),timeout=2):ethernet_reachable=True
    except OSError:pass
    assert not ethernet_reachable,'Ethernet must be unreachable for this check'
    start=time.monotonic();exchanges=c.exchanges;folder,first=device_site(c,cache=cache);first_seconds=time.monotonic()-start;first_exchanges=c.exchanges-exchanges
    assert first['cacheHit'] is False and first['bytes']==15438
    start=time.monotonic();exchanges=c.exchanges;again,second=device_site(c,cache=cache);cached_seconds=time.monotonic()-start;cached_exchanges=c.exchanges-exchanges
    assert second['cacheHit'] is True and again==folder and cached_exchanges==1
    manifest=json.loads((folder/'bridge.json').read_text(encoding='utf-8'))
    assert manifest['projectHash']==identity['identity']['webHash']
    for name,digest in manifest['files'].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest
    after=c.read_channels([indices[key] for key in ids])
    assert c.decoder.errors==0
    result=dict(identity=identity,before=before,after=after,first=first,second=second,first_seconds=round(first_seconds,3),cached_seconds=round(cached_seconds,3),first_exchanges=first_exchanges,cached_exchanges=cached_exchanges,files_verified=list(manifest['files']),folder=str(folder),cache_was_empty=True,user_confirmed_ethernet_unplugged=True,ethernet_tcp_reachable=ethernet_reachable,network_ready_reported=before[indices['network_ready']]['value'],known_network_status_issue='DHCP bound fast path restores readiness between physical-link checks; retained IP is not proof of cable presence.',bad_frames=c.decoder.errors,commands_sent=False)
    (W/'OFFLINE_FLASH.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({key:result[key] for key in ('first_seconds','cached_seconds','first_exchanges','cached_exchanges','cache_was_empty','ethernet_tcp_reachable','network_ready_reported','bad_frames')}))
finally:c.close()
