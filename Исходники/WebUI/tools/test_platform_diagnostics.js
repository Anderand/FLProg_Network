const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ids=['reset_flags','reset_cause','heap_used','heap_arena_free','system_uptime','flash_total','flash_app_capacity','flash_app_used','flash_app_free','ram_total','ram_app_capacity','ram_static_used','ram_available_estimate','ram_used_estimate','ccm_total','ccm_used'];
const c={previewDocument:{channels:ids.map(id=>({id,type:'text',direction:'duplex'})),pages:[{id:'main',title:'Main',widgets:[]}]},parent:{postMessage(){}},Date,TextEncoder,URL,setTimeout(){},window:{addEventListener(){}}};
vm.createContext(c);vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),c);
(async()=>{
 for(const id of ids){
  assert.equal((await c.window.fetch('/flprog-webui/write?channel='+id+'&value=FAKE',{method:'POST'})).status,422);
  const d=await (await c.window.fetch('/flprog-webui/state?page=main')).json();assert.equal(d.values[id],'');
  c.simSet(id,'123');const after=await (await c.window.fetch('/flprog-webui/state?page=main')).json();assert.equal(after.values[id],'123');
 }
 console.log('PASS: unavailable by default; diagnostic writes rejected even duplex; local simulation remains possible');
})().catch(e=>{console.error(e);process.exitCode=1});
