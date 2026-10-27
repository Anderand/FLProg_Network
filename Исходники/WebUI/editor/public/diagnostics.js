// Pure planning: reuse public channels and never overwrite an existing page.
function networkDiagnosticsPageTemplate(){return {id:'network-diagnostics',title:'Диагностика контроллера',system:'network-diagnostics',widgets:[
{id:'network_diag_heading',type:'heading',label:'Диагностика контроллера',x:1,y:1,w:12,h:1},
{id:'network_diag_ip',type:'status-row',label:'IP-адрес',channel:'network_ip',group:'Сеть проекта',x:1,y:1,w:6,h:1},
{id:'network_diag_ready',type:'status-row',label:'Сеть подключена',channel:'network_ready',group:'Сеть проекта',x:7,y:1,w:6,h:1},
{id:'network_diag_mac',type:'status-row',label:'MAC-адрес',channel:'network_mac',group:'Сеть проекта',x:1,y:2,w:12,h:1},
{id:'network_diag_gateway',type:'status-row',label:'Шлюз',channel:'network_gateway',group:'Сеть проекта',x:1,y:3,w:6,h:1},
{id:'network_diag_model',type:'status-row',label:'Модель контроллера',channel:'device_model',placeholder:'Не задано',group:'Устройство',x:1,y:1,w:12,h:1},
{id:'network_diag_version',type:'status-row',label:'Версия прошивки',channel:'firmware_version',placeholder:'Не задано',group:'Устройство',x:1,y:2,w:12,h:1},
{id:'network_diag_reset',type:'status-row',label:'Расшифровка флагов сброса',channel:'reset_cause',placeholder:'Недоступно',group:'Устройство',x:1,y:3,w:12,h:1},
{id:'network_diag_flags',type:'status-row',label:'Маска сброса (накопленная)',channel:'reset_flags',placeholder:'Недоступно',group:'Устройство',x:1,y:4,w:12,h:1},
{id:'network_diag_heap_used',type:'status-row',label:'ОЗУ: динамически занято, байт',channel:'heap_used',placeholder:'Недоступно',group:'Оперативная память',x:1,y:4,w:12,h:1},
{id:'network_diag_heap_free',type:'status-row',label:'ОЗУ: свободные блоки в выделенном пуле, байт',channel:'heap_arena_free',placeholder:'Недоступно',group:'Оперативная память',x:1,y:5,w:12,h:1},
{"id": "system_flash_total", "type": "status-row", "label": "Flash контроллера: всего, байт", "channel": "flash_total", "placeholder": "Недоступно", "group": "Flash", "x": 1, "y": 1, "w": 12, "h": 1},
{"id": "system_flash_app_capacity", "type": "status-row", "label": "Flash: доступно приложению, байт", "channel": "flash_app_capacity", "placeholder": "Недоступно", "group": "Flash", "x": 1, "y": 2, "w": 12, "h": 1},
{"id": "system_flash_app_used", "type": "status-row", "label": "Flash: размер приложения, байт", "channel": "flash_app_used", "placeholder": "Недоступно", "group": "Flash", "x": 1, "y": 3, "w": 12, "h": 1},
{"id": "system_flash_app_free", "type": "status-row", "label": "Flash: свободно для приложения, байт", "channel": "flash_app_free", "placeholder": "Недоступно", "group": "Flash", "x": 1, "y": 4, "w": 12, "h": 1},
{"id": "system_ram_total", "type": "status-row", "label": "ОЗУ контроллера: всего, байт", "channel": "ram_total", "placeholder": "Недоступно", "group": "Оперативная память", "x": 1, "y": 1, "w": 12, "h": 1},
{"id": "system_ram_app_capacity", "type": "status-row", "label": "ОЗУ: доступно приложению, байт", "channel": "ram_app_capacity", "placeholder": "Недоступно", "group": "Оперативная память", "x": 1, "y": 2, "w": 12, "h": 1},
{"id": "system_ram_static_used", "type": "status-row", "label": "ОЗУ: переменные программы, байт", "channel": "ram_static_used", "placeholder": "Недоступно", "group": "Оперативная память", "x": 1, "y": 3, "w": 12, "h": 1},
{"id": "system_ram_available_estimate", "type": "status-row", "label": "ОЗУ: доступно для выделений (оценка), байт", "channel": "ram_available_estimate", "placeholder": "Недоступно", "group": "Оперативная память", "x": 1, "y": 7, "w": 12, "h": 1},
{"id": "system_ram_used_estimate", "type": "status-row", "label": "ОЗУ: занято и зарезервировано (оценка), байт", "channel": "ram_used_estimate", "placeholder": "Недоступно", "group": "Оперативная память", "x": 1, "y": 6, "w": 12, "h": 1},
{"id": "system_ccm_total", "type": "status-row", "label": "Дополнительная ОЗУ CCM: всего, байт", "channel": "ccm_total", "placeholder": "Недоступно", "group": "Дополнительная память CCM", "x": 1, "y": 1, "w": 12, "h": 1},
{"id": "system_ccm_used", "type": "status-row", "label": "Дополнительная ОЗУ CCM: занято, байт", "channel": "ccm_used", "placeholder": "Недоступно", "group": "Дополнительная память CCM", "x": 1, "y": 2, "w": 12, "h": 1},
{"id": "system_uptime_value", "type": "status-row", "label": "Время работы после запуска", "channel": "system_uptime", "unit": "с", "group": "Устройство", "x": 1, "y": 5, "w": 12, "h": 1},
{id:'network_diag_subnet',type:'status-row',label:'Маска подсети',channel:'network_subnet',group:'Сеть проекта',x:7,y:3,w:6,h:1}
]}}
function networkDiagnosticsPlan(document,catalog){
 const existing=(document.pages||[]).findIndex(p=>p.id==='network-diagnostics');
 if(existing>=0)return {changed:false,pageIndex:existing};
 const ids=['network_ip','network_ready','network_mac','network_gateway','network_subnet','device_model','firmware_version','reset_flags','reset_cause','heap_used','heap_arena_free',"flash_total","flash_app_capacity","flash_app_used","flash_app_free","ram_total","ram_app_capacity","ram_static_used","ram_available_estimate","ram_used_estimate","ccm_total","ccm_used",'system_uptime'];
 if(!catalog?.systemParameters)throw Error('Каталог API ещё не загружен');
 const next=JSON.parse(JSON.stringify(document)),used=new Set(next.channels.filter(c=>Number.isInteger(c.index)&&c.index<=100).map(c=>c.index));
 for(const id of ids){
  const parameter=catalog.systemParameters.find(p=>p.id===id);if(!parameter)throw Error('В каталоге API отсутствует '+id);
  const current=next.channels.find(c=>c.id===id);
  if(current){if(current.type!==parameter.type||current.direction==='command'||!current.source||current.source==='user')throw Error('Канал '+id+' уже занят другим контрактом');continue}
  let index=0;while(used.has(index)&&index<=100)index++;if(index>100)throw Error('Нет свободного номера API 0–100');used.add(index);
  next.channels.push({id,label:parameter.title,type:parameter.type,direction:'publish',source:parameter.source,index});
 }
 const page=networkDiagnosticsPageTemplate(),widgetIds=new Set(next.pages.flatMap(p=>p.widgets.map(w=>w.id)));
 for(const w of page.widgets){let id=w.id,n=2;while(widgetIds.has(id))id=w.id+'_'+n++;w.id=id;widgetIds.add(id)}
 next.pages.push(page);return {changed:true,pageIndex:next.pages.length-1,model:next};
}
