const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('docs/index.html','utf8');
const data=html.match(/<script[^>]*>([\s\S]*?)<\/script>/)[1];
const source=fs.readFileSync('video-app.js','utf8');
const nodes=new Map(),calls=[],timers=new Map();let timerId=0;
function node(key=''){if(nodes.has(key))return nodes.get(key);const n={innerHTML:'',textContent:'',hidden:false,disabled:false,value:'',dataset:{},style:{},childNodes:[],classList:{add(){},toggle(){}},setAttribute(){},addEventListener(){},append(){},appendChild(){},replaceChildren(){},insertAdjacentHTML(){},parentNode:{appendChild(){}},querySelector(s){return node(key+s);},querySelectorAll(){return[];}};nodes.set(key,n);return n;}
function findAll(sel,root){const key=sel.match(/^\[data-([^\]]+)\]$/)?.[1];if(!key)return[];const h=(root||node('#vActivity')).innerHTML;return [...h.matchAll(new RegExp('data-'+key+'="([^"]+)"','g'))].map(m=>{const n=node(sel+m[1]);n.dataset[key.replace(/-([a-z])/g,(_,x)=>x.toUpperCase())]=m[1];return n;});}
const ctx={console,Math,Date,Map,Set,Promise,URL,innerWidth:1200,window:{addEventListener(){}},document:{createElement:()=>node('section'),addEventListener(){},querySelector:()=>null},$:node,$$:findAll,esc:String,TABS:[],NAVOF:{},ICON:{book:'book'},S:{meta:{},progress:{}},W:{queue:[],cur:null,revealed:false},SH:{since:0,items:[],active:0},SP:{tok:0},LF:{},LP:{},LAB:{},curTab:'watch',ART:{draw:()=>'<svg/>'},lsGet:(k,d)=>d,lsSet(){},stopSpeech(){},speak:async()=>{},SPEAKERR:null,randVoice:()=>null,toast(){},shuffle:a=>[...a],shortsAll(){return ctx.EE_SHORTS;},put:(col,id,obj)=>{ctx.S[col][id]=obj;},bump(){},reviewCard:(c,g)=>{calls.push([c.id,g]);return {due:Date.now()+60000};},nextCard:()=>{ctx.W.cur=ctx.W.queue.shift()||null;ctx.W.revealed=false;},setTimeout:(fn,ms)=>{const id=++timerId;timers.set(id,{fn,ms});return id;},clearTimeout:id=>timers.delete(id),setInterval(){},PCH:{},sentText:s=>s.en,genPractice:()=>({type:'cloze'}),makeWQ:()=>({type:'wq'})};
ctx.window=Object.assign(ctx.window,ctx); // Data globals point to the VM global below.
for(const m of source.matchAll(/const old\w+=(\w+);/g))ctx[m[1]]=()=>{};
ctx.buildQueue=()=>{ctx.W.queue=Array.from({length:30},(_,i)=>({id:'c'+(i%25)}));};
ctx.shGo=i=>calls.push(['go',i]);ctx.shAppend=n=>calls.push(['append',n]);
vm.createContext(ctx);vm.runInContext('window=globalThis;window.addEventListener=()=>{};',ctx);vm.runInContext(data,ctx);vm.runInContext(source,ctx);
const get=s=>vm.runInContext(s,ctx);
const catalog=get('VC');assert.equal(ctx.EE_LONG.length,28);assert.equal(get('VWORDS.length'),405);assert.ok(ctx.EE_LONG.filter(l=>get('vWords')(l)>=330).length>=16,'long readings');assert.equal(catalog.filter(l=>/^toeic\d+-/.test(l.id)).length,36);
assert.equal(new Set(catalog.map(x=>x.id)).size,catalog.length);
assert.equal(new Set(ctx.EE_SHORTS.map(x=>x.id)).size,ctx.EE_SHORTS.length);
for(const l of ctx.EE_LONG){assert.ok(get('vWords')(l)>=230,l.id);assert.ok(l.sl.length>=15,l.id);assert.ok([3,4].includes(l.qs.length),l.id);assert.ok(l.sl.every(s=>s[1]&&s[2]));for(const q of l.qs)assert.ok(q[2]>=0&&q[2]<q[1].length);}
assert.ok(catalog.filter(l=>l.pairs).every(l=>l.pairs.length>=4));
ctx.buildQueue();assert.equal(ctx.W.queue.length,20);assert.equal(new Set(ctx.W.queue.map(c=>c.id)).size,20);
ctx.W.cur=ctx.W.queue.shift();while(ctx.W.cur){ctx.W.revealed=true;ctx.grade(1);}assert.equal(calls.length,20);assert.match(node('#wStage').innerHTML,/完了/);ctx.grade(1);assert.equal(calls.length,20);
// A finite selected deck, including repeated Again ratings, ends after 8 unique cards.
get("V.lesson=VC.find(x=>x.id==='deck-0');V.mode='phrases';V.phrase=0;vPhrase()");
for(let i=0;i<8;i++){get('V.revealed=true;vPhrase()');findAll('[data-vgrade]',node('#vActivity'))[0].onclick();}
assert.equal(get('V.phrase'),8);assert.match(node('#vActivity').innerHTML,/完了/);assert.equal(new Set(calls.slice(20).map(c=>c[0])).size,8);
assert.equal(Object.values(ctx.S.meta.videoMistakes.rows).filter(r=>!r.resolved).length,28);
const first=Object.keys(ctx.S.meta.videoMistakes.rows)[0];ctx.videoMistake(first,'a','b','','',true);assert.equal(ctx.S.meta.videoMistakes.rows[first].resolved,true);
// Shorts mix real feed practice cards (every 3rd), word checks (every 7th) and fixed practice episodes (every 5th).
const practice=[];let feed=0,wq=0;for(let i=1;i<=150;i++){const it=ctx.nextItem();if(i%7===0){assert.equal(it.type,'wq');wq++;continue;}if(i%3===0){assert.equal(it.type,'practice');feed++;continue;}assert.equal(it.type,'short');if(i%5===0){assert.ok(it.s.videoId);practice.push(catalog.find(l=>l.id===it.s.videoId).defaultMode);}}
assert.ok(feed>=40&&wq>=20);assert.equal(new Set(practice).size,10);
// Auto next is cancelled on page departure / playback cancellation.
const it={i:0,el:node('short'),s:{id:'test'}};ctx.curTab='shorts';ctx.SH.items=[it,{}];ctx.shortEnd(it);let t=[...timers.values()].at(-1);assert.equal(t.ms,1800);t.fn();assert.deepEqual(calls.at(-1),['go',1]);ctx.shortEnd(it);ctx.spStop();assert.equal(timers.size,1); // the fired fake timer remains in this test map
ctx.shortEnd(it);t=[...timers.values()].at(-1);ctx.curTab='watch';const count=calls.length;t.fn();assert.equal(calls.length,count);
// Grade cannot be submitted before the playback promise finishes.
get("V.lesson=VC.find(x=>x.pairs);V.mode='hvpt';V.hp=0;V.hpOrder=V.lesson.pairs.map(()=>0);V.hpHeard=false;V.hpDone=false;vHVPT()");const before=Object.keys(ctx.S.meta.videoMistakes.rows).length;findAll('[data-vhp]',node('#vActivity'))[1].onclick();assert.equal(Object.keys(ctx.S.meta.videoMistakes.rows).length,before);
console.log('PASS: '+catalog.length+' fixed videos, 28 long readings, 405 phrases, 36 TOEIC decks; finite sessions, saved mistakes, mixed shorts, cancel-safe auto next, listening answer gate');
