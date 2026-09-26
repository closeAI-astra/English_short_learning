/* Exercise browser-independent state transitions using a clock and media doubles. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('study-lab.js','utf8');
const code=source.slice(source.indexOf('async function labFStart()'),source.indexOf('function labFResults()'));
function fixture(){
  let now=1000,tick;
  const nodes={};const $=id=>nodes[id]||(nodes[id]={value:'',checked:false,disabled:false,textContent:''});
  $('#labFTopic').value='My first project';
  const records=[],LF={round:0,durations:[240,180,120],deadline:0,pending:false,token:0,results:[],urls:[],draft:''};
  const c={LF,$,$$:()=>[],Date:{now:()=>now},Math,Error,window:{},navigator:{},
    EEStudy:{remaining:d=>Math.max(0,Math.ceil((d-now)/1000))},
    fmtSec:s=>String(s),setInterval:f=>{tick=f;return 1;},clearInterval:()=>{},
    labHistory:(k,r)=>records.push(r),labFResults:()=>{},URL,Blob};
  vm.createContext(c);vm.runInContext(code,c);
  return {c,LF,$,records,advance:sec=>{now+=sec*1000;tick();}};
}
(async()=>{
  const f=fixture();
  for(let round=0;round<3;round++){
    await f.c.labFStart();assert.ok(f.LF.deadline);f.$('#labFDraft').value='The same story.';
    f.advance(f.LF.durations[round]);assert.equal(f.LF.round,round+1);assert.equal(f.records[round].early,false);
    f.c.labFinish(false);assert.equal(f.records.length,round+1);
  }
  assert.equal(f.$('#labFStart').disabled,true);await f.c.labFStart();assert.equal(f.LF.deadline,0);
  const g=fixture();await g.c.labFStart();g.advance(12);g.c.labFinish(true);assert.equal(g.LF.round,0);assert.equal(g.records[0].interrupted,true);
  const h=fixture();h.$('#labFRecord').checked=true;h.c.window.MediaRecorder=function(){};h.c.navigator.mediaDevices={getUserMedia:async()=>{throw Error('denied');}};
  await h.c.labFStart();assert.equal(h.LF.deadline,0);assert.equal(h.LF.pending,false);assert.equal(h.$('#labFStart').disabled,false);
  const j=fixture();let resolve,stopped=0;j.$('#labFRecord').checked=true;j.c.window.MediaRecorder=function(){};
  j.c.navigator.mediaDevices={getUserMedia:()=>new Promise(r=>resolve=r)};
  const pending=j.c.labFStart();j.LF.token++;j.LF.pending=false;resolve({getTracks:()=>[{stop:()=>stopped++}]});await pending;
  assert.equal(stopped,1);assert.equal(j.LF.deadline,0);
  console.log('PASS: 4/3/2 automatic deadlines, duplicate stop, interruption, permission denial and cancellation');
})().catch(e=>{console.error(e);process.exitCode=1;});
