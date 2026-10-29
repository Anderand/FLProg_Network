const fs=require('fs'),crypto=require('crypto'),assert=require('assert');
const C=require('../esp32/web/project_codec.js');
(async()=>{for(const n of [0,1,3,55,56,63,64,65,1000,1000000]){const b=Uint8Array.from({length:n},(_,i)=>i%251);assert.equal(C.sha(b),crypto.createHash('sha256').update(b).digest('hex'))}
const w=(process.argv[2]||'E:/SAI/FLProg_Network/_work/esp32_full_web_20261029/')+'/',data=new Uint8Array(fs.readFileSync(w+'fixture.gz')),plain=fs.readFileSync(w+'fixture_package.json');
const m={size:data.length,plain:plain.length,sha:C.sha(data)},p=await C.unpack(data,m),hello={protocol:1,identity:{projectId:p.manifest.projectId,webHash:p.manifest.projectHash,webApi:1}};
const doc=C.verify(p,hello);assert.equal(doc.pages.length,4);
const copy=()=>JSON.parse(JSON.stringify(p));let x=copy();x.files['../escape']='bad';assert.throws(()=>C.verify(x,hello));x=copy();x.files['index.html']+=' ';assert.throws(()=>C.verify(x,hello));x=copy();x.manifest.webApi=2;assert.throws(()=>C.verify(x,hello));assert.throws(()=>C.verify(p,{...hello,identity:{...hello.identity,projectId:'wrong'}}));
await assert.rejects(()=>C.unpack(data,{...m,sha:'0'.repeat(64)}));await assert.rejects(()=>C.unpack(data,{...m,plain:plain.length-1}));const corrupt=data.slice();corrupt[100]^=1;await assert.rejects(()=>C.unpack(corrupt,m));
console.log(JSON.stringify({shaVectors:10,fullProjectVerified:true,pages:doc.pages.length,compressedBytes:data.length,plainBytes:plain.length,negativeCases:7}));})().catch(e=>{console.error(e);process.exit(1)});
