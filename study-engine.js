/* Pure helpers shared by the standalone app and regression tests. */
(function(root){
  'use strict';
  function dueLessons(lessons, progress, now=Date.now()) {
    return lessons.filter(x=>progress[x.id] && progress[x.id].due<=now)
      .sort((a,b)=>progress[a.id].due-progress[b.id].due);
  }
  function remaining(deadline, now=Date.now()) { return Math.max(0,Math.ceil((deadline-now)/1000)); }
  function validatePack(pack, files) {
    if(!pack || pack.version!==1 || !Array.isArray(pack.samples) || pack.samples.length>500) throw Error('version: 1 と samples 配列（最大500件）が必要です。');
    const ids=new Set(), names=new Set();
    files.forEach(f=>{if(names.has(f.name))throw Error('同じ名前の音声ファイルがあります。');names.add(f.name);});
    let size=0; files.forEach(f=>size+=f.size||0);
    if(size>100*1024*1024) throw Error('音声ファイルの合計は100MB以下にしてください。');
    const samples=pack.samples.map(s=>{
      if(!s || typeof s.speaker!=='string' || !s.speaker.trim() || s.speaker.length>80 ||
        !Array.isArray(s.pair) || s.pair.length!==2 || s.pair.some(w=>typeof w!=='string'||! /^[a-z]+(?:[-'][a-z]+)*$/i.test(w)) ||
        s.pair[0].toLowerCase()===s.pair[1].toLowerCase() || ![0,1].includes(s.answer) ||
        !['train','test'].includes(s.split) || typeof s.file!=='string' || !names.has(s.file) || !/\.(wav|mp3|ogg|m4a|webm)$/i.test(s.file)) throw Error('話者・単語ペア・正解・用途・音声ファイルを確認してください。');
      if(ids.has(s.file)) throw Error('同じ録音を複数の問題に使うことはできません。'); ids.add(s.file);
      return {...s,pair:s.pair.map(w=>w.toLowerCase()),speaker:s.speaker.trim()};
    });
    const train=samples.filter(s=>s.split==='train'), test=samples.filter(s=>s.split==='test');
    const speakers=new Set(train.map(s=>s.speaker)), words=new Set(train.flatMap(s=>s.pair));
    if(speakers.size<2) throw Error('練習用には少なくとも2人の自然話者の録音が必要です。');
    const coverage=new Map();
    train.forEach(s=>{const k=s.speaker+'|'+s.pair.slice().sort().join('|');if(!coverage.has(k))coverage.set(k,new Set());coverage.get(k).add(s.pair[s.answer]);});
    if([...coverage.values()].some(s=>s.size!==2)) throw Error('各話者・単語ペアには両方の正解語の録音が必要です。');
    if(test.some(s=>speakers.has(s.speaker)||s.pair.some(w=>words.has(w)))) throw Error('確認テストには、練習と重ならない話者・単語を使ってください。');
    return {samples,train,test,speakerCount:speakers.size};
  }
  root.EEStudy={dueLessons,remaining,validatePack};
})(typeof window==='undefined'?globalThis:window);
