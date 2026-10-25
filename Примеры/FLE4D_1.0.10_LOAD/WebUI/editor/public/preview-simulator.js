// Runs only inside the sandboxed preview, never on the controller.
const simChannels=new Map(previewDocument.channels.map(c=>[c.id,c]));
const simWidgets=previewDocument.pages.flatMap(p=>p.widgets.map(w=>({...w,page:p.id,min:w.min??0,max:w.max??100,step:w.step??1,confirmation:w.confirmation??(w.type==='button'?'Отправить команду?':'')})));
let simValues={},simRevision=1,simStarted=Date.now(),simOnline=true,simGeneration=0,simAutomatic=true;
const simDefault=c=>c.type==='bool'?false:c.type==='text'?'':0;
function simPublish(message){parent.postMessage({preview:true,...message},'*')}
function simState(){simPublish({values:{...simValues},online:simOnline,revision:simRevision})}
function simSet(id,value){const c=simChannels.get(id);if(!c)throw Error('Канал не найден');if(c.type==='bool'){if(typeof value!=='boolean')throw Error('Нужен bool')}else if(c.type==='text'){value=String(value);if(new TextEncoder().encode(value).length>63)throw Error('Не больше 63 байт')}else{value=Number(value);if(!Number.isFinite(value)||(c.type==='int32'&&(!Number.isInteger(value)||value< -2147483648||value>2147483647)))throw Error('Неверное число')}simValues[id]=value;simRevision++;simState()}
function simReset(){simGeneration++;simStarted=Date.now();simRevision=1;simValues=Object.fromEntries([...simChannels].map(([id,c])=>[id,simDefault(c)]));simState()}
simReset();
window.addEventListener('message',event=>{if(event.source!==parent||!event.data?.simulation)return;const d=event.data;try{if(d.action==='set')simSet(d.id,d.value);if(d.action==='online'){simOnline=!!d.value;simState()}if(d.action==='restart'){simReset();simPublish({log:'ПЛК перезапущен: значения и счётчики сброшены'})}if(d.action==='automatic')simAutomatic=!!d.value}catch(e){simPublish({log:'Ошибка: '+e.message})}});
if(typeof document!=='undefined')document.addEventListener('click',event=>{if(event.target.closest('a')){event.preventDefault();simPublish({log:'Переход по ссылке отключён в локальном предпросмотре'})}},true);
window.fetch=async function(input,options={}){
 if(!simOnline)throw new TypeError('Имитация потери связи');
 const url=new URL(String(input),'http://preview.invalid');
 if(url.origin!=='http://preview.invalid')throw Error('Внешняя сеть отключена');
 const p=url.searchParams;let result,status=200;
 if(url.pathname==='/flprog-webui/item'){
  if(p.has('page')){const i=Number(p.get('page')),page=previewDocument.pages[i];if(!page)throw Error('Страница не найдена');result={id:page.id,title:page.title,indices:simWidgets.map((w,i)=>w.page===page.id?i:-1).filter(i=>i>=0),pages:previewDocument.pages.length,theme:previewDocument.theme}}
  else result=simWidgets[Number(p.get('index'))];
 }else if(url.pathname==='/flprog-webui/state')result={uptime:Date.now()-simStarted,revision:simRevision,values:{...simValues}};
 else if(url.pathname==='/flprog-webui/write'&&options.method==='POST'){
  const id=p.get('channel'),c=simChannels.get(id),w=simWidgets.find(w=>w.id===p.get('widget'));
  const locked=simWidgets.some(w=>[w.channel,...(w.bindings||[]).filter(b=>b.role==='setpoint').map(b=>b.channel)].includes(id)&&(w.bindings||[]).some(b=>b.role==='busy'&&simValues[b.channel]===true));
  if(locked){status=409;result={error:'Команда уже выполняется'}}
  else if(!c||c.direction==='publish'){status=422;result={error:'Канал только для чтения'}}
  else{try{let value=p.get('value');if(c.type==='bool'){if(!['true','false','1','0'].includes(value))throw Error('Неверный bool');value=value==='true'||value==='1'}simSet(id,value);result={queued:true};status=202;simPublish({log:'Принята команда: '+id+' = '+String(simValues[id])});if(simAutomatic&&w){const bindings=w.bindings||[],busy=bindings.find(b=>b.role==='busy'),res=bindings.find(b=>b.role==='result'),generation=simGeneration;if(busy)simSet(busy.channel,true);setTimeout(()=>{if(generation!==simGeneration)return;if(res){const type=simChannels.get(res.channel)?.type;simSet(res.channel,type==='bool'?true:type==='text'?'Выполнено':1)}if(busy)simSet(busy.channel,false);simPublish({log:'Имитация выполнения завершена: '+w.label})},2000)}}catch(e){status=422;result={error:e.message}}}
 }else{status=404;result={error:'Этот API не моделируется'}}
 return {ok:status<400,status,json:async()=>result};
};
simPublish({log:'Предпросмотр запущен. Все данные локальные; FBD не исполняется.'});
