const fs=require('fs'),vm=require('vm'),assert=require('assert');
const coreSource=fs.readFileSync(process.argv[2],'utf8'),simSource=fs.readFileSync(process.argv[3],'utf8');
const doc={project:{id:'scenario_demo'},channels:[
 {id:'setpoint',type:'float',direction:'duplex'},{id:'run',type:'bool',direction:'command'},
 {id:'busy',type:'bool',direction:'publish'},{id:'result',type:'bool',direction:'publish'},
 {id:'count',type:'int32',direction:'publish'}, {id:'credential',type:'text',direction:'command'}],
 pages:[{id:'main',widgets:[{id:'start',type:'button',channel:'run',bindings:[{role:'busy',channel:'busy'},{role:'result',channel:'result'}]},
 {id:'secret',type:'password-input',channel:'credential'}]}]};
const clone=x=>JSON.parse(JSON.stringify(x));
const context={TextEncoder,Date};vm.createContext(context);vm.runInContext(coreSource,context);const api=vm.runInContext('PreviewScenarios',context);
const values={setpoint:25,run:false,busy:false,result:false,count:1,credential:'PRIVATE_PASSWORD'};
const state={values,online:true,automatic:true},before=clone(doc);
let now=1000;const recorder=new api.Recorder(doc,state,()=>now);
now=1200;recorder.accept({action:'set',id:'setpoint',value:30.5});
now=1300;recorder.accept({action:'command',id:'run',widget:'start',value:true});
now=1400;assert.equal(recorder.accept({action:'set',id:'credential',value:'NEW_PRIVATE_PASSWORD'}),false);
now=3600;const scenario=recorder.finish();
assert.equal(scenario.steps.length,2);assert.equal(scenario.steps[0].afterMs,200);assert.equal(scenario.tailMs,2300);
assert(!JSON.stringify(scenario).includes('PRIVATE_PASSWORD'));assert(!('credential' in scenario.initial.values));
assert.deepEqual(doc,before);assert.equal(state.values.setpoint,25);
assert.equal(JSON.stringify(api.validate(doc,clone(scenario))),JSON.stringify(scenario));
let broken=clone(scenario);broken.projectId='another';assert.throws(()=>api.validate(doc,broken),/другому/);
const changed=clone(doc);changed.channels[0].type='text';assert.throws(()=>api.validate(changed,scenario),/изменились/);
broken=clone(scenario);broken.steps[0].afterMs=-1;assert.throws(()=>api.validate(doc,broken),/задержка/);
broken=clone(scenario);broken.tailMs=600001;assert.throws(()=>api.validate(doc,broken),/10 минут/);
broken=clone(scenario);broken.steps[0].value=NaN;assert.throws(()=>api.validate(doc,broken),/конечное/);
broken=clone(scenario);broken.steps[0]={afterMs:0,action:'set',id:'credential',value:'PRIVATE_PASSWORD'};assert.throws(()=>api.validate(doc,broken),/пароль/);
broken=clone(scenario);broken.initial.values.credential='PRIVATE_PASSWORD';assert.throws(()=>api.validate(doc,broken),/Снимок/);
broken=clone(scenario);broken.steps[1].widget='missing';assert.throws(()=>api.validate(doc,broken),/виджету/);
broken=clone(scenario);broken.steps=Array.from({length:201},()=>({action:'restart',afterMs:0}));assert.throws(()=>api.validate(doc,broken),/200/);
broken=clone(scenario);broken.steps[0].action='fetch';assert.throws(()=>api.validate(doc,broken),/Неизвестное/);
broken=clone(scenario);broken.channels.reverse();assert.equal(api.validate(doc,broken).steps.length,2);
assert.throws(()=>api.action(doc,{action:'set',id:'count',value:1.5}),/int32/);
assert.throws(()=>api.action(doc,{action:'online',value:'false'}),/bool/);
const timers=[],messages=[],listeners={};const parent={postMessage:data=>messages.push(data)};
const sim={previewDocument:doc,parent,URL,URLSearchParams,TextEncoder,Date,setTimeout:f=>timers.push(f),window:{addEventListener:(name,f)=>listeners[name]=f}};
vm.createContext(sim);vm.runInContext(simSource,sim);
async function send(data){await listeners.message({source:parent,data:{simulation:true,...data}})}
async function get(){return (await (await sim.window.fetch('/flprog-webui/state')).json()).values}
async function test(){
 await send({action:'restore',...scenario.initial,playback:true,requestId:'restore'});
 assert.equal(messages.find(x=>x.requestId==='restore').ok,true);
 assert.equal((await get()).setpoint,25);
 assert.equal((await sim.window.fetch('/flprog-webui/write?channel=run&value=true&widget=start',{method:'POST'})).status,423);
 await send({action:'set',id:'setpoint',value:30.5,requestId:'step1'});
 await send({action:'command',id:'run',value:true,widget:'start',requestId:'step2'});
 assert.equal((await get()).busy,true);assert.equal(timers.length,1);
 await send({action:'command',id:'run',value:true,widget:'start',requestId:'duplicate'});
 assert.equal(messages.find(x=>x.requestId==='duplicate').ok,false);assert.equal(timers.length,1);
 const previous=await get();await send({action:'restore',values:{setpoint:99,credential:'x'},online:true,automatic:true,requestId:'bad-restore'});
 assert.equal(messages.find(x=>x.requestId==='bad-restore').ok,false);assert.equal((await get()).setpoint,previous.setpoint);
 await send({action:'restore',...scenario.initial,playback:true,requestId:'repeat'});
 timers.shift()();assert.equal((await get()).result,false);assert.equal((await get()).busy,false);
 await send({action:'command',id:'run',value:true,widget:'start',requestId:'step3'});assert.equal((await get()).busy,true);
 timers.shift()();assert.equal((await get()).result,true);assert.equal((await get()).busy,false);
 await send({action:'command',id:'run',value:true,widget:'start',requestId:'step4'});
 await send({action:'playback',value:false,cancelPending:true,requestId:'stop'});timers.shift()();
 assert.equal((await get()).busy,true); // Stopping does not invent a completion.
 await send({action:'restart',requestId:'restart'});assert.equal((await get()).busy,false);
 await send({action:'online',value:false,requestId:'offline'});await assert.rejects(()=>sim.window.fetch('/flprog-webui/state'),/потери связи/);
 await send({action:'online',value:true,requestId:'online'});assert.equal((await get()).run,false);
 await assert.rejects(()=>sim.window.fetch('http://192.168.100.17/'),/сеть отключена/);
 assert.equal(messages.filter(x=>x.acceptedAction?.action==='command').length,3);
 console.log('PASS: typed scenarios, bounded import, secrets excluded, stable contract, restore atomic, command ACK/busy, repeated run, cancel timers, offline and network isolation');
}
test().catch(error=>{console.error(error);process.exit(1)});
