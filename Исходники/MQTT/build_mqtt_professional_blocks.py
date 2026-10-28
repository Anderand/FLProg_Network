# coding: utf-8
"""Professional MQTT blocks from our basic block definitions; no third-party code."""
from pathlib import Path
import argparse, sys, re, xml.etree.ElementTree as X
base=Path(__file__).resolve().parents[1]
for candidate in [base/'flprog_webui_next/tools',base/'WebUI/tools']:
    if (candidate/'build_start_block.py').is_file():
        sys.path.insert(0,str(candidate));break
from build_start_block import Document

def named(parent, name):
    return next(n for n in parent if n.get('sixx.name') == name)

def professional(basic, number):
    b=named(X.parse(basic).getroot(),'typeClass')
    kind=basic.stem.rsplit('_',1)[1]
    info=named(b,'info').text
    loop=named(named(b,'loopCodePart'),'code').text
    declarations=[]
    for n in named(named(b,'declareCodePart'),'code'):
        if n.get('sixx.type')=='CodeUserBlockDeclareStandartBlock':
            declarations.append('static '+named(n,'firstPart').text+' '+named(n,'name').text+' '+named(n,'lastPart').text)
    loop='{\n'+'\n'.join(declarations)+'\n'+loop+'\n}\n'
    pins=[]
    for group in ['inputs','outputs']:
        for a in named(b,group):
            pin=named(a,'object')
            pins.append((named(pin,'name').text,named(pin,'type').get('sixx.type'),group=='inputs'))
    d=Document(); d.ident=186300000+number*10000
    root=d.node(None,'UserCodeMultiBlockBlockLibraryElement')
    main=d.node(root,'UserCodeMultiBlock','mainBlock');d.identity(main)
    p=d.node(main,'UserCodeMultiBlockMainParametrs','mainParametrs');d.identity(p)
    d.value(p,'folderName','FLProg MQTT Professional');d.text(p,'info',info)
    d.code(main,'codeData',True,True)
    lib,items=d.library(main,'UserCodeMultiBlockBlockInstancesLibrary','blockInstancesLibrary')
    block=d.node(items,'UserCodeMultiBlockBlockInstance');d.identity(block)
    d.value(block,'name','MQTT '+kind+' Pro');d.value(block,'label','MQTT '+kind)
    d.code(block,'commonCodeData',True,False);_,code=d.code(block,'codeData')
    d.library(block,'UserCodeMultiBlockParametrsLibrary','commonParametrsLibrary',True,False)
    d.library(block,'UserCodeMultiBlockParametrsLibrary','instanceParametrsLibrary')
    pinObjects={};pinTags={};tagLists={}
    for name,typ,incoming in pins:
        n=d.node(None,'UserCodeMultiBlockInputOutput','object');d.identity(n)
        d.flag(n,'isInput',incoming);d.value(n,'name',name)
        t=d.node(n,typ+' class','type');instances=d.collection(t,'instanceCollection')
        instance=d.node(instances,typ);d.ref(instances,None,instance)
        d.flag(n,'hasVariable',True);tagLists[name]=d.collection(n,'useInCodeTags')
        d.value(n,'conditionType','none','Symbol');d.value(n,'label','')
        pinObjects[name]=n
    d.fragment(code['declare','start'],'declare',['#include <flprogMqttUserBlocks.h>\n'])
    # Insertion section executes where this instance is placed in the PLC scheme.
    fragment=d.node(code['loop','insert'],'UserCodeMultiBlockCodePartsInstance');d.identity(fragment)
    chunks=d.collection(fragment,'codeText')
    for part in re.split(r'\b('+'|'.join(re.escape(p[0]) for p in pins)+r')\b',loop):
        if not part:continue
        n=d.node(chunks,'UserCodeMultiBlockEditorCodeObject')
        if part in pinObjects:
            if part not in pinTags:
                tag=d.node(n,'UserCodeMultiBlockUseInCodeInputOutputTag','value');d.identity(tag)
                tag.append(pinObjects[part]);pinTags[part]=tag;d.ref(tagLists[part],None,tag)
            else:d.ref(n,'value',pinTags[part])
            d.value(n,'type','codeTag','Symbol')
        else:
            d.value(n,'value',part);d.value(n,'type','plainText','Symbol')
            keys=d.collection(n,'keys');k=d.node(keys,'UserCodeMultiBlockEditorCodePlainTextKey')
            d.value(k,'string',part);d.node(k,'ColorValue','color','Graphics.ColorValue black','Graphics')
        d.flag(n,'isComment',False);d.flag(n,'isTextConstant',False)
    d.value(fragment,'conditionType','none','Symbol');d.value(fragment,'codeName','MQTT '+kind)
    d.flag(fragment,'isCommon',False);d.flag(fragment,'isMain',False)
    d.value(fragment,'position','insert','Symbol');d.value(fragment,'section','loop','Symbol');d.flag(fragment,'isNotViewInclude',False)
    for field,incoming in [('inputsLibrary',True),('outputsLibrary',False)]:
        io,entries=d.library(block,'UserCodeMultiBlockInputsOutputsLibrary',field);d.flag(io,'isInputs',incoming)
        for name,_,direction in pins:
            if direction==incoming:d.ref(entries,None,pinObjects[name])
    for name,common in [('commonConditionsLibrary',True),('instanceConditionsLibrary',False)]:d.library(block,'UserCodeMultiBlockConditionsLibrary',name,common,False)
    view=d.node(block,'UserCodeMultiBlockEditorUserDataParametrsView','userDataParametrsView');d.identity(view);d.collection(view,'items');d.ref(view,'blockInstance',block)
    d.flag(block,'isUseItOnce',kind=='Core');d.text(block,'info',info)
    d.value(block,'oldId',186390000+number,'SmallInteger');d.value(block,'nodeId',186390100+number,'SmallInteger')
    d.collection(block,'extLibsIDs');d.flag(block,'isReadOnly',False)
    labels=d.node(block,'UserCodeMultiBlockDinamicLabelsLibrary','dinmicsLabelsLibrary');d.identity(labels);d.collection(labels,'items')
    view=d.node(lib,'UserCodeMultiBlockEditorUserDataBlocksView','userDataBlocksView');d.identity(view)
    entries=d.collection(view,'items');entry=d.node(entries,'UserCodeMultiBlockEditorUserDataViewTreeElement');d.identity(entry)
    d.ref(entry,'object',block);d.value(entry,'altName','');d.ref(view,'blockInstancesLibrary',lib);d.value(view,'folderName','FLProg MQTT Professional')
    for name,typ in [('commonParametrsLibrary','UserCodeMultiBlockParametrsLibrary'),('commonExtLibsLibrary','UserCodeMultiBlockExtLibsLibrary'),('conditionsLibrary','UserCodeMultiBlockConditionsLibrary')]:d.library(main,typ,name,True,True)
    d.flag(main,'isAsStandart',False)
    pos=d.node(main,'UserCodeMiltiBlockEditorPositiomStore','editorPositionStore');d.collection(pos,'expandElements');d.value(pos,'treeScroolPosition','0@0','Point');d.node(pos,'Dictionary','positionStoreDictionary',env='Core');d.flag(pos,'isShowServiceInformation',False);d.value(pos,'selectedIdString','');d.value(pos,'parametrsTreeWidth',400,'SmallInteger');d.node(pos,'Rectangle','mainWindowDisplayBox','0@23 corner: 1400@900','Graphics')
    d.collection(main,'templates');d.flag(main,'isReadOnly',False)
    seen=set()
    for n in root.iter():
        if n.get('sixx.idref') is not None:assert n.get('sixx.idref') in seen, n.attrib
        if n.get('sixx.id') is not None:
            assert n.get('sixx.id') not in seen
            seen.add(n.get('sixx.id'))
    return X.tostring(root,encoding='utf-16',xml_declaration=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--basic',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    for i,kind in enumerate(['Core','Publish','Subscribe']):
        out=args.output/('FLProg_Network_MQTT_'+kind+'_Professional.ubi')
        out.write_bytes(professional(args.basic/('FLProg_Network_MQTT_'+kind+'.ubi'),i))
        print(out)
