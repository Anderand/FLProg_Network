const fs=require('fs'),vm=require('vm'),assert=require('assert');
const body=fs.readFileSync(process.argv[2],'utf8');
const appended=[],timeouts=[],listeners=[];
const status={textContent:''};
const document={hidden:false,querySelector:()=>status,head:{append(e){appended.push(e)}},
 createElement:tag=>({tag,textContent:''}),addEventListener(...args){listeners.push(args)}};
const context=vm.createContext({document,console,Date,JSON,Error,Promise,AbortController,
 setTimeout(fn,ms){timeouts.push({fn,ms});return timeouts.length},clearTimeout(){},setInterval(){return 1},clearInterval(){}});
context.window=context;
vm.runInContext(body,context);
assert.equal(appended.length,1);assert.equal(appended[0].tag,'style');
assert(appended[0].textContent.includes(':root'));
assert.equal(typeof context.B,'function');assert.equal(typeof context.q,'function');
assert.equal(typeof context.p,'function');assert.equal(typeof context.navSelect,'function');
assert.equal(timeouts.filter(t=>t.fn===context.B).length,1);
assert(status.textContent.includes('100%'));
console.log('PASS: one Flash bundle, stylesheet and complete script order, one bootstrap, polling and command functions');
