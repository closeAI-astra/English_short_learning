const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
vm.runInThisContext(fs.readFileSync('study-engine.js','utf8'));
const E=globalThis.EEStudy;
const lessons=[{id:'a'},{id:'b'},{id:'c'}];
assert.deepEqual(E.dueLessons(lessons,{a:{due:100},b:{due:50},c:{due:201}},200).map(x=>x.id),['b','a']);
assert.equal(E.remaining(5000,1001),4);assert.equal(E.remaining(1000,2000),0);
const samples=['a','b'].flatMap(speaker=>[0,1].map(answer=>({speaker,answer,pair:['light','right'],file:speaker+answer+'.wav',split:'train'})));
samples.push({speaker:'c',answer:0,pair:['lock','rock'],file:'test.wav',split:'test'});
const files=samples.map(s=>({name:s.file,size:100}));
const pack={version:1,samples};assert.equal(E.validatePack(pack,files).speakerCount,2);
for(const mutate of [
  p=>p.samples[4].speaker='a', p=>p.samples[4].pair=['light','rock'],
  p=>p.samples[0].answer=3,p=>p.samples[0].file='missing.wav',
  p=>p.samples[1].file=p.samples[0].file,p=>p.samples=p.samples.filter(s=>s.speaker!=='b'),
  p=>p.samples=p.samples.filter((s,i)=>i!==1)
]){const bad=JSON.parse(JSON.stringify(pack));mutate(bad);assert.throws(()=>E.validatePack(bad,files));}
const html=fs.readFileSync('docs/index.html','utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
scripts.forEach((s,i)=>new vm.Script(s,{filename:'inline-'+i+'.js'}));
const data={window:{}};data.window=data;vm.createContext(data);vm.runInContext(scripts[0],data);
assert.equal(data.EE_MICRO.length,60);assert.equal(new Set(data.EE_SHORTS.map(s=>s.id)).size,data.EE_SHORTS.length);
assert.equal(data.EE_SHORTS.filter(s=>s.microId).length,60);assert.equal(Object.keys(data.EE_GENRES)[0],'daily');
assert.notEqual(Object.keys(data.EE_GENRES)[0],'dino');
const main=scripts.find(s=>s.includes('function schedule('));
const scheduling=main.slice(main.indexOf('const FW='),main.indexOf('function fmtIvl('));
const ctx={MIN:60000,DAY:86400000,Date,Math};vm.createContext(ctx);vm.runInContext(scheduling,ctx);
const now=1800000000000;const p=ctx.schedule(null,3,now);assert.equal(p.due,now+600000);
const again=ctx.schedule(p,3,p.due);assert.ok(again.due>p.due);assert.equal(again.reps,2);
console.log('PASS: due ordering, clock, audio validation/leakage, JS parse, 60 shorts, topic order, persisted scheduler transitions');
