const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(require('path').join(__dirname,'../esp32/web/project_viewer.js'),'utf8').replace(/\r/g,'');
const rpcCode=source.slice(0,source.indexOf('\n}')+2);
async function run(op,statuses,resultFailure=false){let starts=0,results=0;
 const context={URLSearchParams,TextDecoder,Uint8Array,Error,Promise,setTimeout:f=>f(),window:{fetch:async(path)=>{
  if(path==='/plc-api/session')return{ok:true,status:200,json:async()=>({token:'t'})};
  if(path==='/plc-api/start'){const status=statuses[Math.min(starts++,statuses.length-1)];return{ok:status===202,status,json:async()=>status===202?{ticket:1}:{error:'busy'}};}
  results++;if(resultFailure)throw Error('response lost');return{ok:true,status:200,json:async()=>({state:3,session:'s',payloadHex:'0100000000'})};
 }}};vm.createContext(context);vm.runInContext(rpcCode,context);let error;
 try{await context.makeEspRpc().request(op);}catch(e){error=e;}
 return{starts,results,error};
}
(async()=>{
 let r=await run('chunk',[409,409,202]);assert(!r.error&&r.starts===3&&r.results===1);
 r=await run('read',[409]);assert(r.error&&r.starts===30&&r.results===0);
 r=await run('read',[500]);assert(r.error&&r.starts===1);
 r=await run('write',[409,202]);assert(r.error&&r.starts===1&&r.results===0);
 r=await run('write',[202],true);assert(r.error.commandAccepted===true&&r.starts===1&&r.results===1);
 console.log('PASS actual browser RPC: bounded pre-ticket busy retry for reads only; no write retry, no replay after accepted/lost response');
})().catch(e=>{console.error(e);process.exitCode=1;});
