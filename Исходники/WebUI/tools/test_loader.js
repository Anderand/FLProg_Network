const fs=require('fs'),vm=require('vm'),assert=require('assert');
const assets=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const scriptCount=JSON.parse(assets['/flprog-webui/controls.js?part=loader'].body.match(/let p=(\[[^\]]+\])/)[1].replaceAll("'",'"')).length;
const root=assets['/'].body,code=root.match(/<script>([\s\S]*)<\/script>/)[1];
async function run(failures=0,hard=false){
 let calls=[],executed=[],messages=[],tries={},timers=new Map(),id=0,context;
 const status={set textContent(s){messages.push(s)},get textContent(){return messages.at(-1)}};
 const loader=assets['/flprog-webui/controls.js?part=loader'].body;
 const fetch=async(u,o)=>{calls.push({u,cache:o.cache});tries[u]=(tries[u]||0)+1;
  if(hard)return{ok:false,status:403};
  if(tries[u]<=failures)throw Error('temporary TCP failure');
  return {ok:true,text:async()=>u.includes('part=loader')?loader:'/* fetched '+u+' */'};
 };
 context=vm.createContext({fetch,AbortController,console,Error,Promise,JSON,Date,
  setTimeout(f,ms){const n=++id;if(ms<1000)queueMicrotask(f);else timers.set(n,f);return n},clearTimeout(n){timers.delete(n)},
  document:{querySelector:()=>status,createElement:tag=>({tag}),head:{append(e){if(e.tag==='script'){if(e.textContent===loader)vm.runInContext(e.textContent,context);else executed.push(e.textContent)}}}}
 });
 vm.runInContext(code,context);
 for(let i=0;i<30*(scriptCount+1);i++)await Promise.resolve();
 return{context,calls,executed,messages,tries,timers};
}
(async()=>{
 let r=await run(1);assert.equal(r.executed.length,scriptCount);assert(r.messages.at(-1).includes('100%'));assert(r.messages.some(x=>x.includes('/'+scriptCount)));assert(r.calls.every(x=>x.cache==='default'));assert(Object.values(r.tries).every(x=>x===2));assert.equal(r.timers.size,0);
 r=await run(20);assert.equal(r.executed.length,0);assert.equal(r.calls.length,3);assert(r.messages.at(-1).includes('Не удалось'));
 r=await run(0,true);assert.equal(r.calls.length,1);assert.equal(r.executed.length,0);
 r=await run();assert.equal(r.executed.length,scriptCount);assert.equal(r.calls.length,scriptCount+2);
 // Data reads explicitly bypass cache. Full body must complete before return.
 let called=false;r.context.fetch=async(u,o)=>{called=o.cache==='no-store';return{ok:true,text:async()=>'{"revision":1}'}};
 assert.equal(await r.context.bootRead('/state'),'{"revision":1}');assert(called);
 // A stalled body is aborted and retried, never executed partially.
 let attempts=0;r.context.fetch=async(u,o)=>{attempts++;return{ok:true,text:()=>new Promise((resolve,reject)=>{o.signal.addEventListener('abort',()=>reject(Error('aborted')));queueMicrotask(()=>{for(const f of r.timers.values())f()})})}};
 await assert.rejects(r.context.bootRead('/stalled'));assert.equal(attempts,3);
 assert.equal(r.timers.size,0);
 console.log('PASS: loader progress, complete-body execution once, transient GET retry, permanent 403, bounded attempts, body timeout, static cache default and data no-store');
})().catch(e=>{console.error(e);process.exitCode=1});
