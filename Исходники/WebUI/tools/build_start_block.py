# coding: utf-8
"""One professional FLProg starter. Contains schema metadata and our own code only."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
START_NAME='FLProg_WebUI_Start.ubi'

class Document:
 def __init__(self):self.serial=0;self.ident=184100100
 def node(self,parent,typ,name=None,text=None,env='Arduino'):
  attrs={'sixx.id':str(self.serial),'sixx.type':typ,'sixx.env':env};self.serial+=1
  if name:attrs['sixx.name']=name
  n=ET.Element('sixx.object',attrs)if parent is None else ET.SubElement(parent,'sixx.object',attrs)
  if text is not None:n.text=str(text)
  return n
 def value(self,p,name,text,typ='String'):return self.node(p,typ,name,text,'Core')
 def flag(self,p,name,value):return ET.SubElement(p,'sixx.object',{'sixx.name':name,'sixx.type':'True'if value else'False','sixx.env':'Core'})
 def ref(self,p,name,obj):
  a={'sixx.idref':obj.get('sixx.id')}
  if name:a['sixx.name']=name
  return ET.SubElement(p,'sixx.object',a)
 def identity(self,p):self.ident+=1;return self.value(p,'id',self.ident,'SmallInteger')
 def collection(self,p,name):return self.node(p,'OrderedCollection',name,env='Core')
 def text(self,p,name,value=''):
  n=self.node(p,'Text',name,env='Core');self.value(n,'string',value)
  runs=self.node(n,'RunArray','runs',env='Core');lengths=self.node(runs,'Array','runs',env='Core');values=self.node(runs,'Array','values',env='Core')
  if value:
   self.node(lengths,'SmallInteger',text=len(value),env='Core')
   self.node(values,'UndefinedObject',env='Core')
  return n
 def library(self,p,typ,name,common=False,main=False):
  n=self.node(p,typ,name);self.identity(n);items=self.collection(n,'items');self.flag(n,'isCommon',common);self.flag(n,'isMain',main);return n,items
 def code(self,p,name,common=False,main=False):
  n=self.node(p,'UserCodeMultiBlockCodeData',name);self.identity(n);libs={}
  for section in ['declare','setup','loop','function']:
   sec=self.node(n,'UserCodeMultiBlockCodeData'+section.capitalize()+'Section',section+'Section');self.identity(sec)
   for part in (['code']if section=='function'else ['start','stop']+(['insert']if section=='loop'else [])):
    field='codePart'if part=='code'else'inseptPart'if part=='insert'else part+'Part'
    lib,items=self.library(sec,'UserCodeMultiBlockCodePartsLibrary',field,common,main)
    self.value(lib,'position','neitral'if part=='code'else part,'Symbol');self.value(lib,'section',section,'Symbol');libs[section,part]=items
   self.flag(sec,'isCommon',common);self.flag(sec,'isMain',main)
  self.flag(n,'isCommon',common);self.flag(n,'isMain',main);return n,libs
 def fragment(self,items,section,parts,position='start'):
  f=self.node(items,'UserCodeMultiBlockCodePartsInstance');self.identity(f);code=self.collection(f,'codeText')
  for part in parts:
   n=self.node(code,'UserCodeMultiBlockEditorCodeObject')
   if isinstance(part,str):
    self.value(n,'value',part);self.value(n,'type','plainText','Symbol');keys=self.collection(n,'keys');k=self.node(keys,'UserCodeMultiBlockEditorCodePlainTextKey');self.value(k,'string',part);self.node(k,'ColorValue','color','Graphics.ColorValue black','Graphics')
   else:
    tag=self.node(n,'UserCodeMultiBlockUseInCodeStandartParametrTag','value');self.identity(tag);self.ref(tag,'object',part);self.value(n,'type','codeTag','Symbol')
   self.flag(n,'isComment',False);self.flag(n,'isTextConstant',False)
  self.value(f,'conditionType','none','Symbol');self.value(f,'codeName','Web UI '+section);self.flag(f,'isCommon',False);self.flag(f,'isMain',False);self.value(f,'position',position,'Symbol');self.value(f,'section',section,'Symbol');self.flag(f,'isNotViewInclude',False)

def start_block_bytes():
 d=Document();root=d.node(None,'UserCodeMultiBlockBlockLibraryElement');main=d.node(root,'UserCodeMultiBlock','mainBlock');d.value(main,'id',184100001,'SmallInteger')
 p=d.node(main,'UserCodeMultiBlockMainParametrs','mainParametrs');d.identity(p);d.value(p,'folderName','FLProg Web UI');d.text(p,'info','Один стартовый блок. ID проекта задаётся перед компиляцией. Сеть и SPI настраиваются в проекте FLProg.')
 d.code(main,'codeData',True,True)
 lib,items=d.library(main,'UserCodeMultiBlockBlockInstancesLibrary','blockInstancesLibrary')
 block=d.node(items,'UserCodeMultiBlockBlockInstance');d.identity(block);d.value(block,'name','Web UI Start');d.value(block,'label','Web UI Start');d.code(block,'commonCodeData',True,False);_,code=d.code(block,'codeData')
 d.library(block,'UserCodeMultiBlockParametrsLibrary','commonParametrsLibrary',True,False)
 _,params=d.library(block,'UserCodeMultiBlockParametrsLibrary','instanceParametrsLibrary')
 param=d.node(params,'UserCodeMultiBlockStandartParametr');d.identity(param);d.value(param,'name','ID проекта');d.value(param,'description','ID из редактора, например web_slave. Без кавычек, расширения и пути.');d.value(param,'conditionType','none','Symbol')
 typ=d.node(param,'StringDataType class','type');instances=d.collection(typ,'instanceCollection');instance=d.node(instances,'StringDataType');d.ref(instances,None,instance)
 species=d.node(param,'UserCodeMultiBlockInputFieldParametrSpecies','parametrSpecies');d.identity(species);d.value(species,'defaultValue','');d.flag(param,'isInsertWithoutBrackets',True)
 d.fragment(code['declare','start'],'declare',['#include <',param,'_webui.h>\n'])
 d.fragment(code['setup','stop'],'setup',['FLPROG_WEBUI_BEGIN_SELECTED();\n'],position='stop')
 for name,incoming in [('inputsLibrary',True),('outputsLibrary',False)]:
  io,_=d.library(block,'UserCodeMultiBlockInputsOutputsLibrary',name);d.flag(io,'isInputs',incoming)
 for name,common in [('commonConditionsLibrary',True),('instanceConditionsLibrary',False)]:d.library(block,'UserCodeMultiBlockConditionsLibrary',name,common,False)
 view=d.node(block,'UserCodeMultiBlockEditorUserDataParametrsView','userDataParametrsView');d.identity(view);vi=d.collection(view,'items');entry=d.node(vi,'UserCodeMultiBlockEditorUserDataViewTreeElement');d.identity(entry);d.ref(entry,'object',param);d.value(entry,'altName','ID проекта');d.ref(view,'blockInstance',block)
 d.flag(block,'isUseItOnce',True);d.text(block,'info','Введите ID проекта из редактора Web UI. Один экземпляр на проект FLProg. При смене макета с тем же ID блок менять не нужно.');d.value(block,'oldId',184100002,'SmallInteger');d.value(block,'nodeId',184100003,'SmallInteger');d.collection(block,'extLibsIDs');d.flag(block,'isReadOnly',False)
 labels=d.node(block,'UserCodeMultiBlockDinamicLabelsLibrary','dinmicsLabelsLibrary');d.identity(labels);d.collection(labels,'items')
 bv=d.node(lib,'UserCodeMultiBlockEditorUserDataBlocksView','userDataBlocksView');d.identity(bv);bi=d.collection(bv,'items');be=d.node(bi,'UserCodeMultiBlockEditorUserDataViewTreeElement');d.identity(be);d.ref(be,'object',block);d.value(be,'altName','');d.ref(bv,'blockInstancesLibrary',lib);d.value(bv,'folderName','FLProg Web UI')
 for name,typ in [('commonParametrsLibrary','UserCodeMultiBlockParametrsLibrary'),('commonExtLibsLibrary','UserCodeMultiBlockExtLibsLibrary'),('conditionsLibrary','UserCodeMultiBlockConditionsLibrary')]:d.library(main,typ,name,True,True)
 d.flag(main,'isAsStandart',False)
 pos=d.node(main,'UserCodeMiltiBlockEditorPositiomStore','editorPositionStore');d.collection(pos,'expandElements');d.value(pos,'treeScroolPosition','0@0','Point');d.node(pos,'Dictionary','positionStoreDictionary',env='Core');d.flag(pos,'isShowServiceInformation',False);d.value(pos,'selectedIdString','');d.value(pos,'parametrsTreeWidth',400,'SmallInteger');d.node(pos,'Rectangle','mainWindowDisplayBox','0@23 corner: 1400@900','Graphics')
 d.collection(main,'templates');d.flag(main,'isReadOnly',False)
 # SIXx resolves references in stream order. Define the parameter inside its
 # first code tag, then reference that SAME object from the parameter library.
 # A forward idref imported visibly but lost the parameter during codegen.
 first_ref=next(n for n in root.iter()if n.get('sixx.idref')==param.get('sixx.id'))
 parent=next(n for n in root.iter()if first_ref in list(n));offset=list(parent).index(first_ref)
 params.remove(param);d.ref(params,None,param);parent.remove(first_ref);param.set('sixx.name','object');parent.insert(offset,param)
 # All object identities are stable and unique; references are backward only.
 numbers=[n.get('sixx.id')for n in root.iter()if n.get('sixx.id')is not None];assert len(numbers)==len(set(numbers))
 assert all(n.get('sixx.idref')in numbers for n in root.iter()if n.get('sixx.idref')is not None)
 seen=set()
 for n in root.iter():
  if n.get('sixx.idref')is not None:assert n.get('sixx.idref')in seen
  if n.get('sixx.id')is not None:seen.add(n.get('sixx.id'))
 return ET.tostring(root,encoding='utf-16',xml_declaration=True)

if __name__=='__main__':
 out=ROOT/'runtime/FLProg_WebUI/user_blocks'/START_NAME;out.write_bytes(start_block_bytes());print(out)
