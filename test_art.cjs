const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('docs/index.html','utf8');
const start=html.indexOf('const ART=(function(){'),end=html.indexOf('\n})();',html.indexOf('return {draw:draw',start))+7;
assert.ok(start>=0&&end>start,'embedded ART closure');
const ctx=vm.createContext({esc:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')});
vm.runInContext(html.slice(start,end),ctx);const art=vm.runInContext('ART',ctx);
const items='bottle cap recycle tshirt bin signal elevator stairs doorway price coupon receipt tipjar popcorn passport seat boardingpass menu chair battery plug bell projector speech question wordcards measure parcel thermometer window'.split(' ');
const bgs='street shop hotel kitchen recycling'.split(' ');
const lessons=['native','curiosity','bridge850'].flatMap(k=>JSON.parse(fs.readFileSync('materials/shorts_'+k+'.json','utf8')));
const used=new Set(),backgrounds=new Set();let scenes=0;
for(const l of lessons){
 assert.ok(new Set(l.sl.map(s=>s[0])).size>=3,l.id+' visual variation');
 for(const s of l.sl){const [bg,...keys]=s[0].split('|');assert.ok(art.bgs.includes(bg),l.id+': '+bg);backgrounds.add(bg);
  for(const k of keys){assert.ok(art.names.includes(k),l.id+': '+k);used.add(k);assert.ok(art.draw(s[0]).includes(art.shape(k)),l.id+': invisible '+k);}
  scenes++;
 }
}
for(const k of items){assert.ok(art.shape(k),k);assert.ok(used.has(k),'unused '+k);}
for(const bg of bgs)assert.ok(backgrounds.has(bg),'unused '+bg);
// Verify that subtitles select the new shapes and that an unknown word keeps a valid fallback.
const app=fs.readFileSync('video-app.js','utf8');
vm.runInContext(app.slice(app.indexOf('const VKEYS='),app.indexOf('EE_LONG.forEach')),ctx);
for(const [text,key,bg] of [['Please keep the bottle caps.','cap','paper'],['The pedestrian signal changed.','signal','street'],['Check the unit price at checkout.','price','shop'],['Show your boarding pass.','boardingpass','airport'],['The frozen fish is thawing.','thermometer','kitchen']]){
 const scene=vm.runInContext(`vAutoScene('paper|book',${JSON.stringify(text)},0,true)`,ctx);
 assert.ok(scene.split('|').includes(key),text);assert.equal(scene.split('|')[0],bg,text);
}
assert.match(vm.runInContext("vAutoScene('paper|book','Unmatched text.',0,true)",ctx),/^paper\|book/);
if(process.argv.includes('--preview')){
 const tile=(spec,label,x,y)=>art.draw(spec).replace('<svg ',`<svg x="${x}" y="${y}" width="200" height="240" `)+`<text x="${x+100}" y="${y+256}" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#314253">${label}</text>`;
 const shapes=items.map((k,i)=>tile('paper|'+k,k,i%6*200,Math.floor(i/6)*275)).join('');
 const backgrounds=bgs.map((k,i)=>tile(k+'|speech',k,i*200,1375)).join('');
 fs.mkdirSync('output',{recursive:true});fs.writeFileSync('output/video-art-preview.svg','<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1650"><rect width="1200" height="1650" fill="#FAFAF7"/>'+shapes+backgrounds+'</svg>');
}
console.log(`PASS: 30 new shapes, 5 backgrounds, ${lessons.length} shorts / ${scenes} scenes, SVG scene composition and subtitle selection`);
