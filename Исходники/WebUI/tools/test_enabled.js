const fs=require('fs'),vm=require('vm'),assert=require('assert');const assets=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
let writes=0,msg='',sent=0,controls=[{disabled:false,closest:()=>({dataset:{widget:'field'}})}],badge={style:{}};
const c={Date,Error,encodeURIComponent,AbortController,document:{querySelector:()=>badge,querySelectorAll:s=>s==='[data-widget]'?[]:controls},setTimeout,clearTimeout,setInterval(){},v:{},a:[],q:async()=>{},M:t=>{msg=t;c.lastMessage=t}};
vm.createContext(c);for(const part of ['enabled','status','commands'])vm.runInContext(assets['/flprog-webui/controls.js?part='+part].body,c);
c.lastOK=Date.now();c.K=async()=>true;c.f=async(u,o,callback)=>{callback();sent++;writes++;return{queued:true}};
const w={id:'field',channel:'sp',bindings:[{role:'enabled',channel:'permit'},{role:'busy',channel:'busy'}]};c.a=[w];
(async()=>{
 for(const value of [undefined,false,0,1,'true']){c.v.permit=value;assert(c.O(w));assert.equal(await c.p('sp',30,w),false);assert.equal(writes,0);c.N(false);assert(controls[0].disabled)}
 c.v.permit=true;assert(!c.O(w));c.N(false);assert(!controls[0].disabled);assert.equal(await c.p('sp',30,w),true);assert.equal(writes,1);
 c.v.busy=true;assert(c.O(w));assert.equal(await c.p('sp',31,w),false);c.v.busy=false;
 // Permission disappears during the confirmation dialog.
 w.confirmation='Confirm';c.K=async()=>{c.v.permit=false;return true};c.v.permit=true;assert.equal(await c.p('sp',32,w),false);assert.equal(writes,1);
 // Permission disappears while HTTP task waits in the queue: sent hook rechecks.
 c.K=async()=>true;c.v.permit=true;c.f=async(u,o,callback)=>{c.v.permit=false;callback();writes++;return{queued:true}};assert.equal(await c.p('sp',33,w),false);assert.equal(writes,1);
 // Legacy widgets remain usable; restriction affects only bound widgets.
 assert(!c.O({id:'legacy'}));c.v.permit=true;c.v.busy=true;assert(c.O(w));c.v.busy=false;assert(!c.O(w));
 const diagnostic={dataset:{widget:'diag'},querySelector(){},querySelectorAll(){return[]}};c.a=Array(8);c.a[7]={id:'diag',type:'text'};c.document.querySelectorAll=s=>s==='[data-widget]'?[diagnostic]:[];c.gateLabels();c.N(true);
 console.log('Enabled: unknown/false fail closed, true allows, busy independent, confirmation/queue races blocked, legacy unchanged OK');
})().catch(e=>{console.error(e);process.exitCode=1});
