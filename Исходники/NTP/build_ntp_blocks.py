# coding: utf-8
"""Own NTP Basic/Professional blocks, using the established FLProg serializers."""
import ast,argparse,sys,uuid,re
from pathlib import Path
import xml.etree.ElementTree as X
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'Исходники/WebUI/tools'))
from build_start_block import Document
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output
basic=out/'Basic';pro=out/'Professional';basic.mkdir(parents=True,exist_ok=True);pro.mkdir(parents=True,exist_ok=True)
src=(R/'Исходники/MQTT/build_mqtt_blocks.py').read_text(encoding='utf-8-sig');tree=ast.parse(src)
code='\n\n'.join(ast.get_source_segment(src,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('build','resolve_code'))
code=code.replace('flprog/mqtt/v0.3/','flprog/ntp/timezone/v0.1/').replace('FLProg MQTT ','FLProg NTP ').replace('<flprogMqttUserBlocks.h>','<flprogNtpUserBlocks.h>').replace('FLProg_Network_MQTT_','FLProg_NTP_').replace('mqttSelectedNetwork','ntpSelectedNetwork')
ns=dict(OUT=basic,X=X,uuid=uuid);exec(code,ns)
loop=ns['resolve_code']()+'''ntpBlock.control(ntpSelectedNetwork, EN, SYNC, SERVER, PERIOD_S, TIMEOUT_MS, UTC_MIN, DST_MODE);
VALID = ntpBlock.valid();
SYNCED = ntpBlock.synced;
Busy = EN && ntpBlock.ntp.busy();
ERR = ntpBlock.error();
Error = ERR != 0;
YEAR = VALID ? ntpBlock.local.year : 0;
MONTH = VALID ? ntpBlock.local.month : 0;
DAY = VALID ? ntpBlock.local.day : 0;
HOUR = VALID ? ntpBlock.local.hours : 0;
MINUTE = VALID ? ntpBlock.local.minutes : 0;
SECOND = VALID ? ntpBlock.local.seconds : 0;
WEEKDAY = VALID ? ntpBlock.local.weekDay : 0;
DST_ACTIVE = VALID && ntpBlock.local.daylight;
OFFSET_MIN = VALID ? ntpBlock.local.offsetMinutes : 0;'''
info='NTP LocalTime v0.1. Сеть берётся из проекта: NET_KIND1=W5500,2=WiFi,0=реестр; NET_NUM1..8 для интерфейсов. SPI/Ethernet не перенастраивает. EN включает сервис; SYNC фронт повторного запроса. SERVER — имя NTP сервера. PERIOD_S0=3600с, TIMEOUT_MS0=15000мс. UTC_MIN — зимнее/стандартное смещение в минутах (-720..840), пример UTC+7=420, UTC+5:30=330. DST_MODE0=без перевода,1=ЕС (+60мин),2=США (+60мин). Только районы, применяющие выбранные правила; исторической базы нет. Вызов блока каждый цикл, сеть обслуживается общим network.pool(), календарь пересчитывается раз в секунду/при смене настройки. Старые NTP методы сохраняют UTC. Выходы даты/времени местные; WEEKDAY0=воскресенье. VALID означает ранее полученное время, не непрерывную доступность сервера; SYNCED — импульс успешной синхронизации. ERR100=сеть не найдена,101=неверные параметры/пустой SERVER,102=пояс/DST;1..13=ошибки NTP. Собственные сезонные правила доступны в C++ API setDaylightRules. Выходы не являются UTC Unix timestamp.'
ns['build']('LocalTime',[('EN','Boolean'),('SYNC','Boolean'),('NET_KIND','Long'),('NET_NUM','Long'),('SERVER','String'),('PERIOD_S','Long'),('TIMEOUT_MS','Long'),('UTC_MIN','Long'),('DST_MODE','Long')],[('VALID','Boolean'),('SYNCED','Boolean'),('Busy','Boolean'),('Error','Boolean'),('ERR','Long'),('YEAR','Long'),('MONTH','Long'),('DAY','Long'),('HOUR','Long'),('MINUTE','Long'),('SECOND','Long'),('WEEKDAY','Long'),('DST_ACTIVE','Boolean'),('OFFSET_MIN','Long')],loop,[('FLProgNtpUserBlock','ntpBlock',';')],info=info)
src=(R/'Исходники/MQTT/build_mqtt_professional_blocks.py').read_text(encoding='utf-8-sig');tree=ast.parse(src)
code='\n\n'.join(ast.get_source_segment(src,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('named','professional'))
code=code.replace('MQTT','NTP').replace('1863','1871').replace('<flprogMqttUserBlocks.h>','<flprogNtpUserBlocks.h>')
ns=dict(X=X,re=re,Document=Document);exec(code,ns)
(pro/'FLProg_NTP_LocalTime_Professional.ubi').write_bytes(ns['professional'](basic/'FLProg_NTP_LocalTime.ubi',0))
for path in out.rglob('*.ubi'):
 root=X.parse(path).getroot();seen=set()
 for n in root.iter():
  if n.get('sixx.id'):
   assert n.get('sixx.id') not in seen;seen.add(n.get('sixx.id'))
  if n.get('sixx.idref'):assert n.get('sixx.idref') in seen,'Forward/missing reference'
print('Basic and Professional NTP blocks generated and references checked:',out)
