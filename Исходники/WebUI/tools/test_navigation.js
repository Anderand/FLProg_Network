const fs=require('fs'),vm=require('vm'),assert=require('assert');
const assets=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
function setup(){
 const store=new Map(),calls=[],timers=[],s={dataset:{},textContent:''},m={hidden:false,setAttribute(){},append(b){this.button=b}},nav={children:[],set innerHTML(v){this.children=[...v.matchAll(/<button>/g)].map(()=>({}))}},main={setAttribute(){}};
 const c={console,Date,encodeURIComponent,location:{pathname:'/'},localStorage:{getItem:k=>store.get(k),setItem:(k,v)=>store.set(k,v)},document:{hidden:false,createElement:()=>({}),documentElement:{style:{setProperty(){}}},querySelector:k=>({'#s':s,'#m':m,'#n':nav,main})[k]},setTimeout:f=>timers.push(f),setInterval(){},pollStop(){},pollEpoch:0,syncPending:true,pollStarted:false,pollSchedule(){},pollConfig(){},N(){},R(){},commandBusy:false,lastOK:1};
 vm.createContext(c);for(const p of ['/flprog-webui/controls.js?part=navigation','/flprog-webui/boot-init.js','/flprog-webui/boot.js'])vm.runInContext(assets[p].body,c);
 c.f=async u=>{calls.push(u);if(u.includes('page=0'))return{id:'first',title:'First',pages:2,indices:[0]};if(u.includes('page=1'))return{id:'second',title:'Second',indices:[1,2]};if(u.includes('index='))return{id:'w'+u.split('=').at(-1),page:c.g};return{revision:1,uptime:100,values:{sp:27}}};
 return{c,store,calls,nav,m};
}
(async()=>{
 let {c,store,calls,nav,m}=setup();await c.B();assert.equal(c.g,'first');assert.equal(c.n.length,2);assert(!c.syncPending);await nav.children[1].onclick();assert.equal(c.g,'second');assert.equal(store.get(c.navKey),'second');assert(calls.at(-1).endsWith('page=second'));
 // Reload boot restores a valid saved page; no duplicate menu entries.
 await c.B();assert.equal(c.g,'second');assert.equal(c.n.length,2);assert.equal(nav.children.length,2);
 store.set(c.navKey,'removed');await c.B();assert.equal(c.g,'first');
 c.localStorage={getItem(){throw Error('denied')},setItem(){throw Error('denied')}};await c.B();assert.equal(c.g,'first');
 // A failed menu read exposes a retry and leaves commands/data locked.
 const good=c.f;c.f=async u=>{if(u.includes('page=1'))throw Error('503');return good(u)};await c.B();assert(!c.navReady);assert(c.syncPending);assert(m.button);let before=calls.length;await c.q();assert.equal(calls.length,before);c.f=good;await m.button.onclick();assert(c.navReady);assert.equal(c.n.length,2);
 // Widget batch is committed only when all descriptors arrive. No partial state.
 let failed=true;c.f=async u=>{if(u.includes('index=2')&&failed)throw Error('503');return good(u)};
 await nav.children[1].onclick();assert(!c.navReady);assert(c.syncPending);assert.equal(c.a[1],undefined);assert(!c.n[1].loaded);failed=false;await m.button.onclick();assert(c.navReady);assert(c.n[1].loaded);assert.equal(c.a[2].id,'w2');assert(calls.at(-1).endsWith('page=second'));
 // No navigation path ever sends a POST or calls the command function.
 assert(calls.every(u=>u.startsWith('/flprog-webui/item?')||u.startsWith('/flprog-webui/state?')));
 console.log('Navigation: restore, removed ID, denied storage, menu retry, atomic widget retry, full sync, no writes OK');
})().catch(e=>{console.error(e);process.exitCode=1});
