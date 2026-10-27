// Runs only inside the sandboxed preview, never on the controller.
const simChannels=new Map(previewDocument.channels.map(c=>[c.id,c]));
const simWidgets=previewDocument.pages.flatMap(p=>p.widgets.map(w=>({...w,groupStyle:{border:true,padding:12,gap:10,...(p.groupStyles?.[(w.group||'').trim()]||{})},page:p.id,min:w.min??0,max:w.max??100,step:w.step??1,confirmation:w.confirmation??(w.type==='button'?'Отправить команду?':'')})));
let simValues={},simRevision=1,simStarted=Date.now(),simOnline=true,simGeneration=0,simAutomatic=true,simPlayback=false;
const simDefault=c=>c.type==='bool'?false:c.type==='text'?'':0;
const simSecret=id=>simChannels.get(id)?.secret===true||id==='wifi_password'||id==='ap_password'||simWidgets.some(w=>w.type==='password-input'&&[w.channel,...(w.bindings||[]).filter(b=>b.role==='setpoint').map(b=>b.channel)].includes(id));
function simPublish(message){parent.postMessage({preview:true,...message},'*')}
function simState(){simPublish({values:{...simValues},online:simOnline,automatic:simAutomatic,revision:simRevision})}
function simTyped(id,value){const c=simChannels.get(id);if(!c)throw Error('Канал не найден');if(c.type==='bool'){if(typeof value!=='boolean')throw Error('Нужен bool')}else if(c.type==='text'){value=String(value);if(new TextEncoder().encode(value).length>63)throw Error('Не больше 63 байт')}else{value=Number(value);if(!Number.isFinite(value)||(c.type==='int32'&&(!Number.isInteger(value)||value< -2147483648||value>2147483647)))throw Error('Неверное число')}return value}
function simSet(id,value){simValues[id]=simTyped(id,value);simRevision++;simState()}
function simReset(){simGeneration++;simStarted=Date.now();simRevision=1;simValues=Object.fromEntries([...simChannels].map(([id,c])=>[id,simDefault(c)]));simState()}
simReset();
window.addEventListener('message',async event=>{
 if(event.source!==parent||!event.data?.simulation)return;const d=event.data;
 try{
  let accepted=null;
  if(simPlayback&&!d.requestId)throw Error('Идёт воспроизведение сценария');
  if(d.action==='set'){simSet(d.id,d.value);accepted={action:'set',id:d.id,value:simValues[d.id]}}
  else if(d.action==='online'){if(typeof d.value!=='boolean')throw Error('Нужен bool');simOnline=d.value;simState();accepted={action:'online',value:d.value}}
  else if(d.action==='restart'){simReset();simPublish({log:'ПЛК перезапущен: значения и счётчики сброшены'});accepted={action:'restart'}}
  else if(d.action==='automatic'){if(typeof d.value!=='boolean')throw Error('Нужен bool');simAutomatic=d.value;simState();accepted={action:'automatic',value:d.value}}
  else if(d.action==='snapshot'){simState()}
  else if(d.action==='restore'){
   if(typeof d.online!=='boolean'||typeof d.automatic!=='boolean'||!d.values||typeof d.values!=='object')throw Error('Неверный снимок');
   const values=Object.fromEntries([...simChannels].map(([id,c])=>[id,simDefault(c)]));
   for(const [id,value]of Object.entries(d.values)){
    const c=simChannels.get(id);if(!c||simSecret(id))throw Error('Канал снимка отсутствует или содержит пароль');
    values[id]=simTyped(id,value);
   }
   simGeneration++;simStarted=Date.now();simRevision=1;simValues=values;simOnline=d.online;simAutomatic=d.automatic;simPlayback=d.playback===true;simState();
  }
  else if(d.action==='command'){
   const params=new URLSearchParams({channel:d.id,value:String(d.value),widget:d.widget});
   const response=await window.fetch('/flprog-webui/write?'+params,{method:'POST',simulationReplay:true});
   if(!response.ok){const body=await response.json();throw Error(body.error||'Команда отклонена')}
  }
  else if(d.action==='playback'){simPlayback=d.value===true;if(d.cancelPending)simGeneration++}
  else throw Error('Неизвестное действие');
  if(accepted)simPublish({acceptedAction:accepted,replay:simPlayback});
  if(d.requestId)simPublish({requestId:d.requestId,ok:true});
 }catch(e){simPublish({log:'Ошибка: '+e.message});if(d.requestId)simPublish({requestId:d.requestId,ok:false,error:e.message})}
});
if(typeof document!=='undefined')document.addEventListener('click',event=>{if(event.target.closest('a')){event.preventDefault();simPublish({log:'Переход по ссылке отключён в локальном предпросмотре'})}},true);
window.fetch=async function(input,options={}){
 if(!simOnline)throw new TypeError('Имитация потери связи');
 const url=new URL(String(input),'http://preview.invalid');
 if(url.origin!=='http://preview.invalid')throw Error('Внешняя сеть отключена');
 const p=url.searchParams;let result,status=200;
 if(url.pathname==='/flprog-webui/item'){
  if(p.has('page')){const i=Number(p.get('page')),page=previewDocument.pages[i];if(!page)throw Error('Страница не найдена');result={id:page.id,title:page.title,indices:simWidgets.map((w,i)=>w.page===page.id?i:-1).filter(i=>i>=0),pages:previewDocument.pages.length,theme:previewDocument.theme,polling:previewDocument.polling||{intervalMs:1300,pauseWhenHidden:true}}}
  else result=simWidgets[Number(p.get('index'))];
 }else if(url.pathname==='/flprog-webui/state')result={uptime:Date.now()-simStarted,revision:simRevision,values:{...simValues}};
 else if(url.pathname==='/flprog-webui/write'&&options.method==='POST'){
  if(simPlayback&&!options.simulationReplay)return {ok:false,status:423,json:async()=>({error:'Идёт воспроизведение сценария'})};
  const id=p.get('channel'),c=simChannels.get(id),w=simWidgets.find(w=>w.id===p.get('widget'));
  const locked=simWidgets.some(w=>[w.channel,...(w.bindings||[]).filter(b=>b.role==='setpoint').map(b=>b.channel)].includes(id)&&(w.bindings||[]).some(b=>(b.role==='busy'&&simValues[b.channel]===true)||(b.role==='enabled'&&(simChannels.get(b.channel)?.type!=='bool'||simChannels.get(b.channel)?.direction==='command'||simValues[b.channel]!==true))));
  const patterned=simWidgets.find(x=>x.pattern&&(x.channel===id||(x.bindings||[]).some(b=>b.role==='setpoint'&&b.channel===id))&&(typeof patternMatches!=='function'||!patternMatches(x.pattern,p.get('value')||'')||new TextEncoder().encode(p.get('value')||'').length>(x.maxLength||63)));
  if(id==='device_model'||id==='firmware_version'){status=422;result={error:'readonly identity'}}
  else if(['reset_flags','reset_cause','heap_used','heap_arena_free','system_uptime','flash_total','flash_app_capacity','flash_app_used','flash_app_free','ram_total','ram_app_capacity','ram_static_used','ram_available_estimate','ram_used_estimate','ccm_total','ccm_used'].includes(id)){status=422;result={error:'readonly diagnostics'}}
  else if(patterned){status=422;result={error:patterned.validationMessage||'invalid field value'}}
  else if(locked){status=409;result={error:'Управление заблокировано: busy/enabled'}}
  else if(!c||c.direction==='publish'){status=422;result={error:'Канал только для чтения'}}
  else{try{let value=p.get('value');if(c.type==='bool'){if(!['true','false','1','0'].includes(value))throw Error('Неверный bool');value=value==='true'||value==='1'}simSet(id,value);result={queued:true};status=202;simPublish({log:'Принята команда: '+id+' = '+String(simValues[id]),acceptedAction:{action:'command',id,value:simValues[id],widget:w?.id},replay:simPlayback});if(simAutomatic&&w){const bindings=w.bindings||[],busy=bindings.find(b=>b.role==='busy'),res=bindings.find(b=>b.role==='result'),generation=simGeneration;if(busy)simSet(busy.channel,true);setTimeout(()=>{if(generation!==simGeneration)return;if(res){const type=simChannels.get(res.channel)?.type;simSet(res.channel,type==='bool'?true:type==='text'?'Выполнено':1)}if(busy)simSet(busy.channel,false);simPublish({log:'Имитация выполнения завершена: '+w.label})},2000)}}catch(e){status=422;result={error:e.message}}}
 }else{status=404;result={error:'Этот API не моделируется'}}
 return {ok:status<400,status,json:async()=>result};
};
simPublish({log:'Предпросмотр запущен. Все данные локальные; FBD не исполняется.'});
