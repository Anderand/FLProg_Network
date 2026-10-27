const fs=require('fs'),vm=require('vm'),assert=require('assert');const assets=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
let now=100000,id=0;const timers=new Map(),listeners={},calls=[],control={disabled:false},connection={style:{},setAttribute(){}},message={setAttribute(){}};
const node=()=>({dataset:{},children:[],style:{},setAttribute(){},append(...a){this.children.push(...a)}});
const c={console,Date:class extends Date{static now(){return now}},document:{hidden:false,activeElement:null,createElement:node,querySelector:s=>s==='#connection'?connection:message,querySelectorAll:s=>s==='[data-widget]'?[]:[control],addEventListener:(e,f)=>listeners[e]=f},setTimeout:(f,ms)=>{timers.set(++id,{f,ms});return id},clearTimeout:i=>timers.delete(i),setInterval:()=>{},B:()=>{},R:()=>{},encodeURIComponent,AbortController,TextEncoder,fetch:async()=>({ok:true,json:async()=>({queued:true})})};
vm.createContext(c);
for(const path of ['/flprog-webui/controls.js?part=enabled','/flprog-webui/controls.js?part=status','/flprog-webui/controls.js?part=commands','/flprog-webui/boot.js','/flprog-webui/controls.js?part=polling','/flprog-webui/controls.js?part=form-state','/flprog-webui/controls.js?part=pattern-parse','/flprog-webui/controls.js?part=pattern-match','/flprog-webui/controls.js?part=form-apply'])vm.runInContext(assets[path].body,c);
timers.clear();c.g='main';c.pollStarted=true;c.pollConfig({polling:{intervalMs:2000,pauseWhenHidden:true}});
let response={revision:5,uptime:5000,values:{sp:25}};c.f=async u=>{calls.push(u);return response};
function visible(value){c.document.hidden=!value;listeners.visibilitychange()}
(async()=>{
 await c.q();assert(!calls.at(-1).includes('since='));assert.equal(c.syncPending,false);assert.equal(control.disabled,false);assert.equal(c.freshWindow,6000);
 const field=node(),input={type:'number',value:'25',checkValidity:()=>true,reportValidity(){},blur(){}},button={};c.T({label:'Setpoint',channel:'sp'},input,button,field,'sp');input.value='35';input.oninput();c.R=reset=>field._sync(reset);
 await c.q();assert(calls.at(-1).includes('since=5'));
 c.pollSchedule();assert.equal([...timers.values()].at(-1).ms,2000);
 visible(false);assert.equal(c.pollTimer,0);assert(c.pollBlocked());assert(control.disabled);assert(connection.textContent.includes('приостановлен'));const n=calls.length;await c.q();assert.equal(calls.length,n);
 // Old in-flight response is never committed after a hide/show epoch.
 visible(true);assert.equal([...timers.values()].at(-1).ms,0);assert(c.pollBlocked());
 let resolve;c.f=u=>{calls.push(u);return new Promise(r=>resolve=r)};const old=c.q();visible(false);visible(true);resolve({revision:99,uptime:9000,values:{sp:99}});await old;assert.equal(c.v.sp,25);assert(c.syncPending);
 c.f=async u=>{calls.push(u);return{revision:6,uptime:10000,values:{sp:27}}};await c.q();assert(!calls.at(-1).includes('since='));assert.equal(c.v.sp,27);assert.equal(c.syncPending,false);assert.equal(control.disabled,false);assert.equal(input.value,'35','draft preserved');assert(field.children[1].textContent.includes('27'));
 // Failed full synchronization keeps writes disabled, retry remains full.
 visible(false);visible(true);c.f=async()=>{throw Error('offline')};await c.q();assert(c.syncPending);assert(control.disabled);assert(c.needFull);
 c.f=async u=>{calls.push(u);return{revision:7,uptime:11000,values:{sp:28}}};await c.q();assert(!calls.at(-1).includes('since='));assert(!c.pollBlocked());assert.equal(input.value,'35');
 // Turning background pause off preserves polling, returning still requests full.
 c.pollConfig({polling:{intervalMs:60000,pauseWhenHidden:false}});c.syncPending=false;c.pollSchedule();const prior=c.pollTimer;visible(false);assert.equal(c.pollTimer,prior);await c.q();assert.equal(c.freshWindow,180000);visible(true);assert(c.needFull&&c.syncPending);
 c.pollConfig({polling:{intervalMs:500,pauseWhenHidden:true}});assert.equal(c.freshWindow,5000);c.syncPending=false;
 // Real command function rejects hidden/resync writes; resume does not send draft.
 let writes=0;c.f=async()=>{writes++;return{queued:true}};c.lastOK=now;c.syncPending=true;assert.equal(await c.p('sp','35',{id:'x'}),false);c.syncPending=false;c.document.hidden=true;assert.equal(await c.p('sp','35',{id:'x'}),false);assert.equal(writes,0);
 // A visibility epoch prevents the old timer wrapper from overwriting resume(0).
 c.document.hidden=false;c.q=async()=>{c.pollEpoch++;c.pollSchedule(0)};c.pollSchedule();let task=timers.get(c.pollTimer);await task.f();assert.equal(timers.get(c.pollTimer).ms,0);
 console.log('PASS: polling interval, hidden pause/off option, stale window, full resume, late response discarded, failed resync locks controls, draft preserved, no automatic writes, timer epoch race');
})().catch(e=>{console.error(e);process.exitCode=1});
