# coding: utf-8
"""Explicit real ESP settings test. Does not send PLC commands."""
import os,json,time,socket,urllib.request,urllib.parse,urllib.error,http.cookiejar
from html.parser import HTMLParser
from pathlib import Path
base=os.environ['ESP_SETTINGS_URL'];password=os.environ['ESP_SETTINGS_PASSWORD']
assert base=='http://192.168.100.14:8080/','Only the explicitly authorized test ESP'
class Form(HTMLParser):
 def __init__(self):super().__init__();self.fields={};self.selected=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='input' and a.get('name') and a.get('type')!='checkbox':self.fields[a['name']]=a.get('value','')
  if tag=='option' and 'selected' in a:self.fields['format']=a['value']
def client():return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(c):return c.open(base,timeout=4).read().decode('utf-8')
def post(c,path,data):return c.open(urllib.request.Request(base+path,data=urllib.parse.urlencode(data).encode()),timeout=4).read().decode('utf-8')
def denied(c,path,data,status):
 try:post(c,path,data)
 except urllib.error.HTTPError as e:assert e.code==status;return
 raise AssertionError('Request unexpectedly accepted')
def login(c):post(c,'login',{'password':password});return get(c)
c=client();assert 'name=password' in get(c)
denied(c,'save',{},403);denied(c,'login',{'password':'wrong-password'},403)
page=login(c);f=Form();f.feed(page);before=dict(f.fields)
assert before['ssid']=='<configured Wi-Fi>' and before['password']=='' and before['setupPassword']==''
assert 'tcp://192.168.100.14:3234' in page
bad=dict(before,token='invalid');denied(c,'save',bad,403)
bad=dict(before,port='8080');denied(c,'save',bad,400)
assert 'Сохранено' in post(c,'save',before)
time.sleep(3)
end=time.monotonic()+25
while True:
 try:
  fresh=client();after_page=login(fresh);break
 except (OSError,urllib.error.URLError):
  if time.monotonic()>end:raise
  time.sleep(.5)
a=Form();a.feed(after_page)
for key in ('ssid','rx','tx','baud','format','port','idle'):assert a.fields[key]==before[key],key
assert a.fields['password']==''
with socket.create_connection(('192.168.100.14',3234),timeout=3):pass
report=dict(version='Universal0.4',ip='192.168.100.14',settings_port=8080,tcp_port=3234,unauthenticated_save_rejected=True,wrong_password_rejected=True,csrf_rejected=True,reserved_port_rejected=True,network_and_uart_preserved_after_save=True,wifi_password_not_echoed=True,tcp_reachable=True,plc_commands_sent=False)
Path(os.environ['ESP_REPORT']).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
