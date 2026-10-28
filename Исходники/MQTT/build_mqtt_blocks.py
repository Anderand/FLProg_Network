# coding: utf-8
from pathlib import Path
import xml.etree.ElementTree as X
import uuid, argparse

parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'releases/MQTT_User_Blocks_v0_3')
OUT=parser.parse_args().output
OUT.mkdir(parents=True, exist_ok=True)

def build(kind, inputs, outputs, loop, declarations, setup='', info=''):
    global serial
    serial = 0
    def obj(parent, typ, name=None, text=None, env='Core'):
        global serial
        a={'sixx.id':str(serial),'sixx.type':typ,'sixx.env':env}; serial+=1
        if name: a['sixx.name']=name
        e=X.SubElement(parent,'sixx.object',a) if parent is not None else X.Element('sixx.object',a)
        e.text=text
        return e
    root=obj(None,'BlocksLibraryElement',env='Arduino')
    b=obj(root,'CodeUserBlock','typeClass',env='Arduino')
    def s(p,n,t): return obj(p,'String',n,t)
    def flag(p,n,v): X.SubElement(p,'sixx.object',{'sixx.name':n,'sixx.type':str(v),'sixx.env':'Core'})
    s(b,'id',str(uuid.uuid5(uuid.NAMESPACE_URL, 'flprog/mqtt/v0.3/'+kind+'/'+str(serial))))
    obj(b,'OrderedCollection','blocks')
    s(b,'label','FLProg MQTT '+kind)
    s(b,'name','FLProg MQTT '+kind)
    for group,pins in [('inputs',inputs),('outputs',outputs)]:
        c=obj(b,'OrderedCollection',group)
        for name,typ in pins:
            a=obj(c,'InputsOutputsAdaptorForUserBlock',env='Arduino')
            s(a,'id',str(uuid.uuid5(uuid.NAMESPACE_URL, 'flprog/mqtt/v0.3/'+kind+'/'+str(serial))))
            p=obj(a,'UniversalBlockInputOutput','object',env='Arduino')
            s(p,'id',str(uuid.uuid5(uuid.NAMESPACE_URL, 'flprog/mqtt/v0.3/'+kind+'/'+str(serial))))
            X.SubElement(p,'sixx.object',{'sixx.name':'block','sixx.idref':'1'})
            obj(p,typ+'DataType','type',env='Arduino')
            flag(p,'isInput','True' if group=='inputs' else 'False')
            s(p,'name',name); flag(p,'isNot','False'); s(a,'comment','')
    for name in ['variables','parametrs','userLibraries']: obj(b,'OrderedCollection',name)
    s(b,'info',info)
    for name,typ,code in [('loopCodePart','Loop',loop),('setupCodePart','Setup',setup)]:
        c=obj(b,'CodeUserBlock'+typ+'CodePart',name,env='Arduino'); s(c,'code',code)
    c=obj(b,'CodeUserBlockDeclareCodePart','declareCodePart',env='Arduino')
    d=obj(c,'OrderedCollection','code')
    inc=obj(d,'CodeUserBlockDeclareDefineBlock',env='Arduino'); s(inc,'define','#include'); s(inc,'name','<flprogMqttUserBlocks.h>')
    for typ,name,tail in declarations:
        v=obj(d,'CodeUserBlockDeclareStandartBlock',env='Arduino')
        s(v,'name',name); s(v,'firstPart',typ); s(v,'lastPart',tail)
    c=obj(b,'CodeUserBlockFunctuinCodePart','functionCodePart',env='Arduino');obj(c,'OrderedCollection','code')
    flag(b,'notCanManyUse','True' if kind=='Core' else 'False')
    path=OUT/('FLProg_Network_MQTT_'+kind+'.ubi')
    path.write_text(X.tostring(root,encoding='unicode'),encoding='utf-16')
    parsed=X.parse(path); ids=[e.get('sixx.id') for e in parsed.iter() if e.get('sixx.id') is not None]
    assert len(ids)==len(set(ids))
    assert all(e.get('sixx.idref') in ids for e in parsed.iter() if e.get('sixx.idref'))

def resolve_code():
    lines=['FLProgNetworkInterface *mqttSelectedNetwork = nullptr;']
    for kind,macro in ((1,'WIZNET'),(2,'WIFI')):
        for i in range(1,9):
            lines += ['#if defined(FLPROG_'+macro+'_INTERFACE'+str(i)+')',
                'if (NET_KIND == '+str(kind)+' && NET_NUM == '+str(i)+') mqttSelectedNetwork = &FLPROG_'+macro+'_INTERFACE'+str(i)+';', '#endif']
    lines += ['if (NET_KIND == 0 && NET_NUM >= 0 && NET_NUM < 255)',
              '    mqttSelectedNetwork = flprogNetworkDevices.getDevice((FLProgNetworkDeviceId)NET_NUM);']
    return '\n'.join(lines)+'\n'

B='Boolean'; S='String'; N='Long' 
build('Core', [('EN',B),('CON',B),('DIS',B),('NET_KIND',N),('NET_NUM',N),('SUB_LIMIT',N),('POLL_MS',N),('Broker',S),('Port',N),('ClientID',S),('User',S),('Password',S)],
 [('Connected',B),('Busy',B),('Error',B),('ERR',N),('State',N),('Subscriptions',N),('SubBytes',N)],
 resolve_code()+'''flpMqttBlocks().control(mqttSelectedNetwork, EN, CON, DIS, Broker, Port, ClientID, User, Password, SUB_LIMIT, POLL_MS);
Connected = flpMqttBlocks().mqtt.connected();
Busy = flpMqttBlocks().mqtt.busy();
ERR = flpMqttBlocks().error();
Error = ERR != 0;
State = flpMqttBlocks().mqtt.state();
Subscriptions = (long)flpMqttBlocks().mqtt.subscriptionCount();
SubBytes = (long)flpMqttBlocks().mqtt.subscriptionMemoryBytes();''', [], info='Один Core на проект. Сеть из проекта: NET_KIND 1=W5500, 2=WiFi, 0=реестр; NET_NUM номер интерфейса 1..8. POLL_MS: 0=10 мс, 1..1000 мс — опрос в простое; при обмене 1 мс, порция 64 байта. Блоки вызывать каждый цикл: фронты сохраняются, сеть обслуживается по таймеру. SUB_LIMIT=0: динамическое расширение по RAM; >0: явный лимит. Subscriptions: подтверждённые фильтры, SubBytes: память таблицы. SPI/Ethernet не изменяет. EN: автоподключение; CON/DIS: фронт. Настройки применяются при EN или CON. MQTT 3.1.1 QoS0 TCP. One Core per project; settings applied on enable/connect.')
build('Publish',[('Send',B),('Topic',S),('Message',S),('Retain',B)],[('Accepted',B),('ERR',N)],
 '''Accepted = false;
if (Send && !mqttPrevSend) {
    Accepted = flpMqttBlocks().mqtt.publish(Topic.c_str(), Message.c_str(), Retain);
    ERR = flpMqttBlocks().mqtt.error();
}
mqttPrevSend = Send;''',[('bool','mqttPrevSend','= false;')], info='Send: положительный фронт. Accepted: принято клиентом, не подтверждение доставки QoS0. При BUSY повторить фронт позже. Rising-edge Send; Accepted is local acceptance, not broker delivery.')
build('Subscribe',[('Subscribe',B),('Topic',S)],[('Accepted',B),('Received',B),('RxTopic',S),('Message',S),('Retained',B),('ERR',N)],
 '''Accepted = false;
Received = false;
if (Subscribe && !mqttPrevSub) {
    Accepted = flpMqttBlocks().mqtt.subscribe(Topic.c_str());
    ERR = flpMqttBlocks().mqtt.error();
}
mqttPrevSub = Subscribe;
if (mqttSeen != flpMqttBlocks().sequence) {
    mqttSeen = flpMqttBlocks().sequence;
    if (flpMqttBlocks().matches(Topic.c_str(), flpMqttBlocks().topic.c_str())) {
        Received = true;
        RxTopic = flpMqttBlocks().topic;
        Message = flpMqttBlocks().message;
        Retained = flpMqttBlocks().retained;
    }
}''',[('bool','mqttPrevSub','= false;'),('uint32_t','mqttSeen','= 0;')],info='Subscribe: фронт после Connected, повторить при BUSY. Таблица фильтров расширяется динамически; лимит задаётся необязательно в Core. Accepted означает отправку в очередь; подтверждённый фильтр появляется в Subscriptions после SUBACK. + и # поддерживаются. Приём: последнее сообщение за цикл, для текста. Rising-edge Subscribe; latest text message per scan, not a lossless queue.')
print('Created and XML-validated 3 UBI files:', OUT)
