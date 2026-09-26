// Vocabulary coverage of the built app against NGSL 1.2 + TSL 1.2 (same matching as the in-app 語彙カバー).
// Usage: node coverage.cjs [--missing N]   (run build_site.py first)
const fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('docs/index.html','utf8');
const data=html.match(/<script[^>]*>([\s\S]*?)<\/script>/)[1];
const ctx={console};ctx.window=ctx;vm.createContext(ctx);vm.runInContext(data,ctx);
const block=(name)=>{const m=html.match(new RegExp('/\\* BEGIN '+name+' \\*/([\\s\\S]*?)/\\* END '+name+' \\*/'));return m?m[1]:'';};
try{vm.runInContext(block('VIDEO_DATA'),ctx);}catch(e){}
const W=ctx.EE_WORDS,NG=ctx.EE_NGSL_N,IR=ctx.EE_IRREG||{},SET=new Set(W);
const words=t=>String(t).toLowerCase().match(/[a-z]+(?:'[a-z]+)?/g)||[];
function forms(w){const o=[w];if(/ies$/.test(w))o.push(w.slice(0,-3)+'y');if(/ied$/.test(w))o.push(w.slice(0,-3)+'y');if(/es$/.test(w))o.push(w.slice(0,-2));if(/s$/.test(w))o.push(w.slice(0,-1));if(/ed$/.test(w)){o.push(w.slice(0,-2));o.push(w.slice(0,-1));}if(/ing$/.test(w)){o.push(w.slice(0,-3));o.push(w.slice(0,-3)+'e');}if(/ly$/.test(w))o.push(w.slice(0,-2));return o;}
const head=w=>IR[w]&&SET.has(IR[w])?IR[w]:(forms(w).find(f=>SET.has(f))||null);
function cover(texts){const got=new Set();texts.forEach(t=>words(t).forEach(w=>{const h=head(w);if(h)got.add(h);}));return got;}
const slides=l=>(l.sl||[]).map(s=>s[1]);
const shorts=(ctx.EE_SHORTS||[]).flatMap(slides);
const long=(ctx.EE_LONG||[]).flatMap(slides);
const phrases=(ctx.EE_CARDS||[]).flatMap(c=>[c[1],c[3]].filter(x=>typeof x==='string'));
const micro=(ctx.EE_MICRO||[]).map(m=>m.english||'');
const passages=(ctx.EE_PASSAGES||[]).map(p=>JSON.stringify(p));
const phon=(ctx.EE_PHONEMES||[]).flatMap(p=>[...(p.words||[]),...(p.pairs||[]).flat(),p.sentence||'']);
// Long readings are also shown as short episodes, so the in-app counter reaches them too.
const inApp=cover([...shorts,...long,...micro]);
const all=cover([...shorts,...long,...phrases,...micro,...passages,...phon]);
const pct=(s,list)=>{const n=list.filter(w=>s.has(w)).length;return n+' / '+list.length+' ('+(100*n/list.length).toFixed(1)+'%)';};
const ngsl=W.slice(0,NG),tsl=W.slice(NG);
console.log('Word list: NGSL '+ngsl.length+' + TSL '+tsl.length+' = '+W.length);
console.log('Shorts + long readings (in-app 語彙カバー can reach): '+pct(inApp,W)+'  NGSL '+pct(inApp,ngsl)+'  TSL '+pct(inApp,tsl));
console.log('All material incl. phrase cards:               '+pct(all,W)+'  NGSL '+pct(all,ngsl)+'  TSL '+pct(all,tsl));
const i=process.argv.indexOf('--missing');if(i>0){const n=+process.argv[i+1]||200;const miss=W.filter(w=>!all.has(w));console.log('\nMissing ('+miss.length+'), first '+n+':\n'+miss.slice(0,n).join(' '));}
if(process.argv.includes('--missing-tsl')){console.log(tsl.filter(w=>!all.has(w)).join(' '));}
if(process.argv.includes('--missing-ngsl')){console.log(ngsl.filter(w=>!all.has(w)).join(' '));}
if(process.argv.includes('--check')){const a=W.filter(w=>inApp.has(w)).length/W.length,t=tsl.filter(w=>all.has(w)).length/tsl.length;if(a<=.5||t<=.5){console.error('FAIL: coverage must stay above 50% (in-app '+(a*100).toFixed(1)+'%, TSL '+(t*100).toFixed(1)+'%)');process.exit(1);}console.log('PASS: coverage above 50%');}
