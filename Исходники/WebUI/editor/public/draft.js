// Editor design only. Live PLC values and preview state never enter this store.
function createProjectDraftStore(storage){
 const key='flprog.webui.project-draft.v1';let blocked=false,lastError='',lastRaw=null;
 const valid=d=>d&&d.schema==='flprog.webui/1.0'&&d.project&&typeof d.project.id==='string'&&Array.isArray(d.channels)&&d.channels.every(c=>c&&typeof c.id==='string'&&typeof c.type==='string')&&Array.isArray(d.pages)&&d.pages.length>0&&d.pages.every(p=>p&&typeof p.id==='string'&&Array.isArray(p.widgets)&&p.widgets.every(w=>w&&typeof w.id==='string'&&typeof w.type==='string'));
 return {
  load(){try{const raw=storage.getItem(key);lastRaw=raw;if(!raw)return null;const d=JSON.parse(raw);if(d.version!==1||!valid(d.model))throw Error('Неверный формат черновика');return d}catch(e){blocked=true;lastError='Черновик не восстановлен: '+e.message;return null}},
  save(model,pageId){if(blocked)return false;try{if(!valid(model))throw Error('Проект не готов к сохранению');if(storage.getItem(key)!==lastRaw)throw Error('Черновик изменён в другой вкладке. Сохраните свой проект в .flpui');const raw=JSON.stringify({version:1,model,pageId});if(raw.length>2000000)throw Error('Черновик слишком большой; сохраните файл .flpui');storage.setItem(key,raw);lastRaw=raw;lastError='';return true}catch(e){lastError='Черновик не сохранён: '+e.message;return false}},
  allowWrites(){try{lastRaw=storage.getItem(key);blocked=false;lastError=''}catch(e){lastError='Черновик недоступен: '+e.message}},
  error(){return lastError}
 };
}
