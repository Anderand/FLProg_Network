# coding: utf-8
import xml.etree.ElementTree as X,re,subprocess,json,os
from pathlib import Path
r=Path(__file__).resolve().parents[3];w=Path(os.environ.get('NTP_TEST_OUTPUT',Path(__file__).resolve().parent/'out'));w.mkdir(parents=True,exist_ok=True);blocks=r/'Блоки_FLProg/NTP'
def named(n,key):return next(a for a in n if a.get('sixx.name')==key)
def extract_pro(path):
 root=X.parse(path).getroot();ids={n.get('sixx.id'):n for n in root.iter() if n.get('sixx.id')}
 def resolve(n):return ids[n.get('sixx.idref')] if n.get('sixx.idref') else n
 parts=[]
 for fragment in root.iter():
  if fragment.get('sixx.type')!='UserCodeMultiBlockCodePartsInstance':continue
  if not any(n.get('sixx.name')=='position' and n.text=='insert' for n in fragment):continue
  for chunk in named(fragment,'codeText'):
   value=resolve(named(chunk,'value'))
   if value.get('sixx.type')=='UserCodeMultiBlockUseInCodeInputOutputTag':parts.append(named(resolve(named(value,'object')),'name').text)
   else:parts.append(value.text or '')
 return ''.join(parts)
b=named(X.parse(blocks/'Basic/FLProg_NTP_LocalTime.ubi').getroot(),'typeClass')
basic=named(named(b,'loopCodePart'),'code').text
pro=extract_pro(blocks/'Professional/FLProg_NTP_LocalTime_Professional.ubi')
assert re.sub(r'\s+','',pro)==re.sub(r'\s+','','{static FLProgNtpUserBlock ntpBlock ;'+basic+'}'),pro[:200]
header='''#include <cassert>
#include <cstdio>
#include "flprogNtpUserBlocks.h"
FLProgNetworkInterface net;
#define FLPROG_WIZNET_INTERFACE1 net
bool EN=true,SYNC=false,VALID,SYNCED,Busy,Error,DST_ACTIVE;
long NET_KIND=1,NET_NUM=1,PERIOD_S=60,TIMEOUT_MS=1000,UTC_MIN=420,DST_MODE=0;
long ERR,YEAR,MONTH,DAY,HOUR,MINUTE,SECOND,WEEKDAY,OFFSET_MIN;
String SERVER="pool.ntp.org";
'''
for kind,code in [('Basic','{static FLProgNtpUserBlock ntpBlock ;'+basic+'}'),('Professional',pro)]:
 source=w/(kind+'_block.cpp');source.write_text(header+'void run()'+code+'''\nint main(){FakeBeginReady=true;run();assert(VALID&&YEAR==2024&&HOUR==7&&OFFSET_MIN==420&&!DST_ACTIVE);UTC_MIN=60;DST_MODE=1;run();assert(HOUR==1);EN=false;run();assert(!VALID&&HOUR==0);puts("PASS: actual generated '''+kind+''' block");}''',encoding='utf-8')
 exe=w/(kind+'_block.exe');cmd=[os.environ.get('NTP_CXX','clang++'),'-std=c++11','-O2','-UNDEBUG','-I',str(Path(__file__).resolve().parent/'stub'),'-I',str(r/'Библиотека/FLProg_Network/src'),'-I',str(r/'Библиотека/FLProg_Network/src/service'),str(source),'-o',str(exe)]
 if Path(cmd[0]).stem.lower()=='zig':cmd.insert(1,'c++')
 subprocess.run(cmd,check=True);subprocess.run([str(exe)],check=True)
(w/'BLOCKS_TESTS.json').write_text(json.dumps(dict(basic_professional_code_equivalent=True,both_extracted_cpp_compiled_and_executed=True,native_stub=True,live_flprog_import=False),indent=2))
