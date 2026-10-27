// Runs the actual embedded command code with a deterministic transport stub.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const assets=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
for(const [path,asset] of Object.entries(assets)) {
  if(asset.type==='application/javascript')new vm.Script(asset.body,{filename:path});
}
async function test(){
  let sent=0,message='',confirm=true,resolve;
  const c={lastOK:Date.now(),commandBusy:false,a:[],v:{},O:w=>!!w?.bindings?.some(b=>b.role==='busy'&&c.v[b.channel]===true),Date,Error,encodeURIComponent,
    K:async()=>confirm,N:()=>{},M:x=>message=x,q:async()=>{},
    f:async()=>{sent++;return {queued:true}}};
  vm.createContext(c);vm.runInContext(assets['/flprog-webui/controls.js?part=enabled'].body,c);vm.runInContext(assets['/flprog-webui/controls.js?part=commands'].body,c);
  c.K=async()=>confirm;
  const widget={id:'pump',label:'Pump',confirmation:'Start?'};
  confirm=false;assert.strictEqual(await c.p('run',true,widget),false);assert.equal(sent,0);
  confirm=true;assert.strictEqual(await c.p('run',true,widget),true);assert.equal(sent,1);
  assert(message.includes('Принято контроллером'));assert(message.includes('FBD'));
  c.lastOK=Date.now()-6000;assert.strictEqual(await c.p('run',true,widget),false);assert.equal(sent,1);
  c.lastOK=Date.now();c.f=async()=>{sent++;const error=new Error('timeout');error.name='AbortError';throw error};
  assert.strictEqual(await c.p('run',true,widget),false);assert.equal(sent,2);
  assert(message.includes('результат неизвестен'));assert.strictEqual(c.commandBusy,false);
  c.f=()=>{sent++;return new Promise(r=>resolve=r)};
  const first=c.p('run',true,widget);assert.strictEqual(await c.p('run',true,widget),false);
  resolve({queued:true});assert.strictEqual(await first,true);assert.equal(sent,3);
  c.f=async()=>({queued:false});assert.strictEqual(await c.p('run',true,widget),false);
  c.f=async()=>{sent++;return {queued:true}};
  widget.bindings=[{role:'busy',channel:'motor_busy'}];c.v.motor_busy=true;
  let before=sent;assert.strictEqual(await c.p('run',true,widget),false);assert.equal(sent,before);
  c.v.motor_busy=false;assert.strictEqual(await c.p('run',true,widget),true);
  c.K=async()=>{c.v.motor_busy=true;return true};before=sent;
  assert.strictEqual(await c.p('run',true,widget),false);assert.equal(sent,before);
  let fresh=0;
  const state={B:()=>{},setTimeout:()=>{},N:ok=>{if(ok)fresh++},R:()=>{},
    f:async()=>({}),encodeURIComponent};
  vm.createContext(state);vm.runInContext(assets['/flprog-webui/boot.js'].body,state);
  await state.q();assert.equal(fresh,0,'Invalid JSON shape must not mark the connection online');
  state.f=async()=>({revision:1,values:{value:0}});
  await state.q();assert.equal(fresh,1);assert.equal(state.v.value,0);
  const input={disabled:false,closest:()=>({dataset:{widget:'pump'}})},badge={style:{}};
  const ui={a:[{id:'pump',bindings:[{role:'busy',channel:'busy'}]}],v:{busy:true},
    document:{querySelector:()=>badge,querySelectorAll:s=>s==='[data-widget]'?[]:[input]},setInterval:()=>{}};
  vm.createContext(ui);vm.runInContext(assets['/flprog-webui/controls.js?part=enabled'].body,ui);vm.runInContext(assets['/flprog-webui/controls.js?part=status'].body,ui);
  ui.N(true);assert.strictEqual(input.disabled,true);
  ui.v.busy=false;ui.N(false);assert.strictEqual(input.disabled,false);
  const box=()=>({children:[],append(x){this.children.push(x)}});
  const labels={v:{b:true,r:false,a:true},document:{createElement:()=>box()}};
  vm.createContext(labels);vm.runInContext(assets['/flprog-webui/elements.js'].body,labels);
  const target=box();labels.H({bindings:[{role:'busy',channel:'b'},{role:'result',channel:'r'},{role:'alarm',channel:'a'}]},target);
  assert.deepStrictEqual(target.children[0].children.map(x=>x.textContent),['Выполняется: да','Выполнено: нет','Авария: да']);
  console.log('Embedded JS and busy guards: OK (cancel, ack, stale, timeout, duplicate, busy transition, labels)');
}
test().catch(error=>{console.error(error);process.exit(1)});
