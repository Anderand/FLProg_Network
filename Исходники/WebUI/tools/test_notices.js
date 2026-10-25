const fs=require('fs'),vm=require('vm'),assert=require('assert');
const assets=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const node=()=>({children:[],dataset:{},style:{},textContent:'',setAttribute(){},append(...x){this.children.push(...x)},remove(){this.removed=true}});
let counter=0,timers=new Map(),aside;
const c={v:{sp:25,result:true,busy:false},Date,Error,Number,String,Math,Object,encodeURIComponent,
document:{createElement:node,querySelector:()=>aside,body:{append(x){aside=x}}},
setTimeout:(f,ms)=>{timers.set(++counter,{f,ms});return counter},clearTimeout:id=>timers.delete(id)};
vm.createContext(c);
for(const part of ['notice-view','notice-track','notice-sync'])vm.runInContext(assets['/flprog-webui/controls.js?part='+part].body,c);
const text=card=>[card.textContent,...card.children.flatMap(x=>[x.textContent,...(x.children||[]).map(y=>y.textContent)])].join(' ');
function check(){
 const w={id:'field',type:'number-input',label:'Уставка',channel:'sp'};
 let p=c.noticeStart('sp','30.5',w);c.noticeSync(false);assert.equal(p.card.dataset.stage,'sending');
 c.noticeSent(p);c.noticeAck(p);c.noticeSync(false);assert.equal(p.card.dataset.stage,'accepted');
 c.v.sp=30.5;c.noticeSync(false);assert.equal(p.card.dataset.stage,'confirmed');assert(text(p.card).includes('Отправлено'));assert(text(p.card).includes('Принято контроллером'));assert(text(p.card).includes('Подтверждено данными'));
 const button={id:'run',type:'button',channel:'run',bindings:[{role:'busy',channel:'busy'},{role:'result',channel:'result'}]};
 p=c.noticeStart('run',true,button);c.noticeSent(p);c.noticeAck(p);c.noticeSync(false);assert.equal(p.card.dataset.stage,'accepted','Old true must not confirm');
 c.v.busy=true;c.v.result=false;c.noticeSync(false);assert.equal(p.card.dataset.stage,'accepted');c.v.busy=false;c.v.result=true;c.noticeSync(false);assert.equal(p.card.dataset.stage,'confirmed');
 p=c.noticeStart('run',true,button);c.noticeAck(p);c.noticeSync(true);assert.equal(p.card.dataset.stage,'error');assert.equal(c.noticePending.length,0);
 p=c.noticeStart('sp',40,w);c.noticeSent(p);c.noticeAck(p);c.noticeOffline();assert.equal(p.card.dataset.stage,'error');c.v.sp=40;c.noticeSync(false);assert.equal(p.card.dataset.stage,'error','Reconnect must not confirm uncertain command');
 p=c.noticeStart('sp',42,w);timers.get(p.timer).f();assert.equal(p.card.dataset.stage,'error');assert.throws(()=>c.noticeSent(p),/не отправлена/);
 p=c.noticeStart('sp',43,w);c.noticeAck(p);let next=c.noticeStart('sp',44,w);assert(!c.noticePending.includes(p));c.noticeFail(next,'HTTP 409');assert.equal(next.card.dataset.stage,'error');
 p=c.noticeStart('secret','password-value',{id:'secret',channel:'secret',type:'password-input'});c.noticeAck(p);c.v.secret='password-value';c.noticeSync(false);assert(!text(p.card).includes('password-value'));
 assert(c.noticeCards.length<=5);
 console.log('PASS: notices fresh readback, old result, busy cycle, restart, offline, timeout, supersession, errors, password, bounded cards');
}
check();
async function integration(){
 let writes=0;c.a=[];c.lastOK=Date.now();c.commandBusy=false;c.N=()=>{};c.M=t=>c.lastMessage=t;c.O=()=>false;c.q=async()=>c.noticeSync(false);
 vm.runInContext(assets['/flprog-webui/controls.js?part=commands'].body,c);c.K=async()=>true;
 const w={id:'integration',type:'number-input',channel:'sp',label:'Уставка',confirmation:'Apply?'};
 c.v.sp=25;c.f=async(u,o,sent)=>{sent();writes++;c.v.sp=31;return {queued:true}};
 assert.equal(await c.p('sp','31',w),true);assert.equal(writes,1);assert.equal(c.noticeCards.at(-1).dataset.stage,'confirmed');
 c.K=async()=>false;assert.equal(await c.p('sp','32',w),false);assert.equal(writes,1);assert(text(c.noticeCards.at(-1)).includes('отменена'));
 c.K=async()=>true;c.f=async(u,o,sent)=>{sent();writes++;throw Error('HTTP 409')};assert.equal(await c.p('sp','33',w),false);assert(text(c.noticeCards.at(-1)).includes('409'));
 c.f=async(u,o,sent)=>{sent();return {queued:false}};assert.equal(await c.p('sp','33',w),false);assert(text(c.noticeCards.at(-1)).includes('Нет подтверждения приёма'));assert(!text(c.noticeCards.at(-1)).includes('Принято контроллером'));
 c.f=async(u,o,sent)=>{sent();let e=Error('timeout');e.name='AbortError';throw e};assert.equal(await c.p('sp','33',w),false);assert(text(c.noticeCards.at(-1)).includes('результат неизвестен'));
 c.f=async(u,o,sent)=>{c.noticeOffline();sent();writes++;return {queued:true}};const before=writes;assert.equal(await c.p('sp','34',w),false);assert.equal(writes,before,'Cancellation before dispatch must prevent write');
 console.log('PASS: actual command integration, sent/ack/readback, cancel, server rejection and queued offline cancellation');
}
integration().catch(e=>{console.error(e);process.exit(1)});
