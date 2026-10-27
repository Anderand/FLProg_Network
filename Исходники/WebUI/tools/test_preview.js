const fs=require('fs'),vm=require('vm'),assert=require('assert');
async function test(){
 const channels=[{id:'setpoint',type:'float',direction:'duplex'},{id:'run',type:'bool',direction:'command'},{id:'busy',type:'bool',direction:'publish'},{id:'result',type:'text',direction:'publish'},{id:'count',type:'int32',direction:'duplex'}];
 const document={channels,pages:[{id:'main',title:'Главная',widgets:[{id:'start',type:'button',channel:'run',bindings:[{role:'busy',channel:'busy'},{role:'result',channel:'result'}]}]}]};
 const messages=[],timers=[],listeners={};const parent={postMessage:d=>messages.push(d)};
 const c={previewDocument:document,parent,URL,TextEncoder,Date,setTimeout:f=>timers.push(f),window:{addEventListener:(name,f)=>listeners[name]=f}};
 vm.createContext(c);vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),c);
 const send=d=>listeners.message({source:parent,data:{simulation:true,...d}});
 const state=async()=>await (await c.window.fetch('/flprog-webui/state')).json();
 const command=()=>c.window.fetch('/flprog-webui/write?channel=run&value=true&widget=start',{method:'POST'});
 assert.equal((await state()).values.setpoint,0);
 send({action:'set',id:'setpoint',value:'24.5'});assert.equal((await state()).values.setpoint,24.5);
 send({action:'set',id:'count',value:1.5});assert.equal((await state()).values.count,0);
 send({action:'set',id:'busy',value:true});assert.equal((await command()).status,409);
 send({action:'set',id:'busy',value:false});assert.equal((await command()).status,202);assert.equal((await state()).values.busy,true);
 assert.equal((await command()).status,409);timers.shift()();assert.equal((await state()).values.result,'Выполнено');assert.equal((await state()).values.busy,false);
 await command();send({action:'restart'});timers.shift()();assert.equal((await state()).values.result,'');assert.equal((await state()).revision,1);
 send({action:'automatic',value:false});await command();assert.equal((await state()).values.busy,false);assert.equal(timers.length,0);
 send({action:'online',value:false});await assert.rejects(()=>state(),/потери связи/);send({action:'online',value:true});assert.equal((await state()).values.run,true);
 assert.equal((await c.window.fetch('/flprog-webui/write?channel=result&value=x',{method:'POST'})).status,422);
 await assert.rejects(()=>c.window.fetch('http://192.168.100.8/'),/сеть отключена/);
 listeners.message({source:{},data:{simulation:true,action:'set',id:'busy',value:true}});assert.equal((await state()).values.busy,false);
 channels.push({id:'permit',type:'bool',direction:'publish'}); // Dedicated context below checks the server-equivalent permission gate.
 const enabledDoc=JSON.parse(JSON.stringify(document));enabledDoc.pages[0].widgets[0].bindings.push({role:'enabled',channel:'permit'});
 const ec={...c,previewDocument:enabledDoc,window:{addEventListener(){}},parent:{postMessage(){}}};vm.createContext(ec);vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),ec);
 assert.equal((await ec.window.fetch('/flprog-webui/write?channel=run&value=true',{method:'POST'})).status,409);vm.runInContext("simSet('permit',true)",ec);assert.equal((await ec.window.fetch('/flprog-webui/write?channel=run&value=true',{method:'POST'})).status,202);
 console.log('PASS: preview typed values, busy lock, result, manual mode, restart cancels pending completion, offline/reconnect, readonly, network isolation');
}
test().catch(e=>{console.error(e);process.exit(1)});
