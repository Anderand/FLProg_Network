# coding: utf-8
"""Compare actual C++ timezone conversion with the independent IANA zoneinfo oracle."""
import subprocess,random,json,calendar,os
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
w=Path(os.environ.get('NTP_TEST_OUTPUT',Path(__file__).resolve().parent/'out'));w.mkdir(parents=True,exist_ok=True);exe=w/'timezone_peer.exe'
cases=[(0,420,'Asia/Novosibirsk'),(0,345,'Asia/Kathmandu'),(0,-720,None),(0,840,None),(1,60,'Europe/Berlin'),(2,-300,'America/New_York'),(2,-210,'America/St_Johns'),(3,600,'Australia/Sydney'),(4,630,'Australia/Lord_Howe')]
rng=random.Random(57);total=0
for mode,offset,name in cases:
 values={0,1,0xffffffff,0xfffffffe}
 # Modern recurring rules, not a historical timezone database.
 if mode:values=set()
 for year in (2015,2024,2025,2026,2036,2038,2099,2100):
  lo=int(datetime(year,1,1,tzinfo=timezone.utc).timestamp());hi=int(datetime(year+1,1,1,tzinfo=timezone.utc).timestamp())
  values.update(rng.randrange(lo,hi) for _ in range(160))
  for month in (3,4,10,11):
   for day in range(1,calendar.monthrange(year,month)[1]+1):
    for hour in range(24):
     stamp=int(datetime(year,month,day,hour,tzinfo=timezone.utc).timestamp())
     if name:
      z=ZoneInfo(name);a=datetime.fromtimestamp(stamp-1,timezone.utc).astimezone(z);b=datetime.fromtimestamp(stamp+3600,timezone.utc).astimezone(z)
      if a.utcoffset()!=b.utcoffset():values.update(stamp+n for n in (-1,0,1,1799,1800,1801,3599,3600,3601))
 values=sorted(values);p=subprocess.run([str(exe),str(mode),str(offset)],input='\n'.join(map(str,values)),text=True,capture_output=True,check=True)
 lines=p.stdout.splitlines();assert len(lines)==len(values)
 for utc,line in zip(values,lines):
  v=list(map(int,line.split()));z=ZoneInfo(name) if name else timezone(timedelta(minutes=offset))
  dt=datetime.fromtimestamp(utc,timezone.utc).astimezone(z)
  off=int(dt.utcoffset().total_seconds()/60)
  # Fixed profiles intentionally ignore historical changes of a named region.
  if mode==0:dt=datetime.fromtimestamp(utc,timezone.utc).astimezone(timezone(timedelta(minutes=offset)));off=offset
  expected=[utc+off*60,dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,(dt.weekday()+1)%7,off,int(bool(dt.dst())) if mode else 0]
  assert v==expected,(mode,name,utc,v,expected)
 total+=len(values)
# Custom negative shift crossing UTC New Year: first Sunday January 00:00 standard(+14).
stamp=int(datetime(2022,1,1,10,tzinfo=timezone.utc).timestamp())
p=subprocess.run([str(exe),'5','840'],input=f'{stamp-1}\n{stamp}\n',text=True,capture_output=True,check=True)
a,b=[list(map(int,x.split())) for x in p.stdout.splitlines()];assert a[-2:]==[840,0] and b[-2:]==[780,1]
report=dict(cpp_iana_comparisons=total,custom_negative_new_year=True,north_south=True,half_hour_dst=True,epoch_edges=True,invalid_settings_preserve_previous=True)
(w/'TIMEZONE_TESTS.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
