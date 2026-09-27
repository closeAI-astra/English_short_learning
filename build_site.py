"""Rebuild the self-contained GitHub Pages entry point without private files."""
import json
import re
import zipfile
from pathlib import Path
from content import LESSONS

ROOT = Path(__file__).resolve().parent
source = ROOT / 'english-express.html'
html = source.read_text(encoding='utf-8')

def change(old, new):
    global html
    if new in html:
        return
    if old not in html:
        raise RuntimeError(f'Missing integration point: {old[:100]}')
    html = html.replace(old, new, 1)

change("const TABS=['home','shorts'", "const TABS=['lab','home','shorts'")
change("const NAVOF={home:'home'", "const NAVOF={lab:'home',home:'home'")
change("  stopSpeech();curTab=t;", "  if(curTab==='lab')labLeave();\n  stopSpeech();curTab=t;")
change("  if(t==='home')renderHome();", "  if(t==='lab')labEnter(sub||LAB.mode);\n  if(t==='home')renderHome();")
change("    h+='<div class=\"vgrid\">'+FEATURES.slice(0,2)", "    h+=labHome();\n    h+='<div class=\"vgrid\">'+FEATURES.slice(0,2)")
change("showTab(TABS.indexOf(hash)>=0?hash:'shorts');", "showTab(TABS.indexOf(hash.split(':')[0])>=0?hash:'home');")
change("go:'pron:hvpt'", "go:'lab:hvpt'")
change("go:'pron:fluency'", "go:'lab:fluency'")
change("  const IT={", """  const IT={
    bowl:{l:'mid',d:'<ellipse cy="-8" rx="43" ry="15" fill="#F0B65F"/><path d="M-43-8Q-36 48 0 48T43-8Z" fill="#CE6746"/><path d="M-14-25q-12-10 0-20M8-25q-12-10 0-20" fill="none" stroke="#FFF2D3" stroke-width="4"/>'},
    laptop:{l:'mid',d:'<rect x="-43" y="-40" width="86" height="58" rx="6" fill="#54658B"/><rect x="-35" y="-32" width="70" height="42" rx="2" fill="#ABE2DD"/><path d="M-50 20H50L43 30H-43Z" fill="#BCC5D8"/><path d="m-13-17-8 7 8 7m26-14 8 7-8 7" fill="none" stroke="#38526C" stroke-width="4"/>'},
    film:{l:'mid',d:'<rect x="-40" y="-45" width="80" height="90" rx="8" fill="#343E56"/><path d="M-24-35H24V-5H-24ZM-24 5H24V35H-24Z" fill="#CD9EBC"/><path d="M-34-30v10m0 15V5m0 15v10M34-30v10m0 15V5m0 15v10" stroke="#F6E7D9" stroke-width="5"/>'},
    ball:{l:'mid',d:'<circle r="43" fill="#E8964E"/><circle r="43" fill="none" stroke="#7C4838" stroke-width="3"/><path d="M-43 0H43M0-43V43M-28-32Q18 0-28 32M28-32Q-18 0 28 32" fill="none" stroke="#7C4838" stroke-width="3"/>'},
    palette:{l:'mid',d:'<path d="M0-44C-55-45-64 40-10 44 15 46-2 22 23 20 62 20 52-42 0-44Z" fill="#EDD6AA"/><circle cx="-23" cy="-20" r="8" fill="#D26762"/><circle cx="2" cy="-27" r="8" fill="#5D88BB"/><circle cx="26" cy="-13" r="8" fill="#70A483"/><circle cx="-31" cy="7" r="8" fill="#D8AD42"/><circle cx="-4" cy="14" r="9" fill="#9A7E64"/>'},
    chat:{l:'mid',d:'<path d="M-44-35H24Q36-35 36-23V8Q36 20 24 20H-13L-30 35V20H-44Q-55 20-55 8V-23Q-55-35-44-35Z" fill="#65ADA9"/><path d="M-36-15H17M-36 0H3" stroke="#ECFAF0" stroke-width="6" stroke-linecap="round"/>'},""")
change("  scored.sort((a,b)=>b[1]-a[1]);return scored.slice(0,n).map(x=>x[0]);", "  scored.sort((a,b)=>b[1]-a[1]);const first=scored.findIndex(x=>x[0].g!=='dino');if(first>0){const lead=scored.splice(first,1)[0];scored.unshift(lead);}return scored.slice(0,n).map(x=>x[0]);")
change("all.forEach(s=>{if(s.g==='serial'||recent.indexOf(s.id)>=0)return;", "all.forEach(s=>{if(s.g==='serial'||recent.indexOf(s.id)>=0||(!SH.items.some(x=>x.type==='short')&&s.g==='dino'))return;")
change("恐竜・数学・歴史・科学・生き物・旅行・言葉の小話", "日常・旅行・宇宙・音楽・数学・歴史などの小話")
change("FSRS は忘れかける直前に出題するので、早めの復習はしません。続けたいときはフィードへ。", "記憶モデルが計算した次の復習日まで待てます。続けたいときは想起練習やフィードへ。")
change("忘れかけた頃に自力で思い出すと記憶が最も強くなります（想起練習と分散学習）。出題間隔は、Anki にも採用されている FSRS という記憶モデルで、正答率90%を保つように計算します。", "自力で思い出す練習と、日を空けた復習を組み合わせます。出題間隔はFSRS系の記憶モデルによる推定です。設定上の保持率目標は90%ですが、実際の保持率や最適日を保証しません。")
change("毎回違う声・速さで出すことで、特定の話者でなく音そのものの違いを聞き分けられるようにします（日本人の L/R 習得の研究で効果が確かめられた方法）。", "合成音声の声・速さを変えて練習します。自然話者の録音を使うHVPTとは条件が異なります。ホームの聞き分けから自然音声の教材も読み込めます。")

# Embed reproducibly, leaving the rest of the existing single-file app intact.
def block(name, text, anchor):
    global html
    start, end = f'/* BEGIN {name} */', f'/* END {name} */'
    new = start + '\n' + text + '\n' + end
    if start in html:
        html = re.sub(re.escape(start)+r'.*?'+re.escape(end), lambda _: new, html, count=1, flags=re.S)
    else:
        html = html.replace(anchor, new+'\n'+anchor, 1)

css = (ROOT/'study-lab.css').read_text(encoding='utf-8')
block('STUDY_STYLE', css, '</style>')
if 'id="p-lab"' not in html:
    html=html.replace('<!-- STATS -->', '<section role="tabpanel" id="p-lab" hidden><div class="lab-work stack"><div class="lab-tabs" id="labTabs"></div><div id="labBody"></div></div></section>\n<!-- STATS -->',1)

ordered = sorted(LESSONS, key=lambda x: (x['topic']!='日常生活・人間関係', x['topic']!='旅行・交通'))
genres = {'日常生活・人間関係':('daily','day|chat|sun'), '旅行・交通':('travel','city|train|pin'),
 '宇宙・天文':('space','space|moon'), '自然・動物':('animal','forest|bird|tree'),
 '料理・食文化':('food','paper|bowl'), 'テクノロジー・AI':('tech','night|laptop'),
 '数学・問題解決':('math','paper|chart'), '音楽・音声':('music','dusk|note'),
 '映画・物語':('film','night|film'), 'スポーツ・運動':('sport','day|ball'),
 '歴史・博物館':('history','paper|scroll'), '環境・街づくり':('environment','forest|tree'),
 '仕事・コミュニケーション':('work','city|building'), '心理・学び方':('learning','paper|bulb'),
 'デザイン・美術':('art','paper|palette')}
variants={
 'daily':['day|chat|sun','dusk|cloud|chat','night|heart|moon','paper|chat|clock'],
 'travel':['city|train|pin','city|building|clock','paper|globe|magnifier','day|plane|clock'],
 'space':['night|moon|tree','space|planet|magnifier','space|rocket|building','paper|book|moon'],
 'animal':['day|bird|tree','city|heart|building','forest|tree|cloud','night|heart|moon'],
 'food':['paper|bowl','city|bowl|chat','day|bowl|coin','dusk|bowl|book'],
 'tech':['paper|laptop|magnifier','day|laptop|chat','night|laptop|book','dusk|clock|laptop'],
 'math':['paper|dice|magnifier','night|book|scroll','paper|chart|sine','space|primes'],
 'music':['city|note|skyline','paper|note|book','day|plane|note','night|wave|sine'],
 'film':['night|film|moon','paper|film|heart','city|film|chat','dusk|book|scroll'],
 'sport':['day|ball|crown','paper|note|wave','city|ball|building','dusk|heart|clock'],
 'history':['paper|globe|scroll','dusk|scroll|book','city|building|wave','paper|book|clock'],
 'environment':['day|bowl|flower','forest|tree|sun','paper|flower|book','city|globe|bridge'],
 'work':['city|building|clock','paper|chat|wave','dusk|chat|chart','day|book|heart'],
 'learning':['paper|book|clock','day|mountain|pin','night|chat|bulb','dusk|book|chart'],
 'art':['paper|palette|scroll','night|palette|moon','day|palette|building','paper|palette|book'],
}
shorts=[]
for item in ordered:
    g,scene=genres[item['topic']]
    scene=variants[g][int(item['id'].rsplit('-',1)[1])-1]
    en=re.split(r'(?<=[.!?])\s+',item['english'])
    ja=[x for x in re.split(r'(?<=[。！？])',item['japanese']) if x]
    if len(en)==len(ja):
        slides=[[scene,e,j] for e,j in zip(en,ja)]
    else:
        slides=[[scene,item['english'],item['japanese']]]
    slides.append([scene,'How would you say this in your own words?','今の内容を、自分の言葉で英語で説明してみましょう。'])
    shorts.append({'id':'short-'+item['id'],'g':g,'t':item['title']+'（場面練習）','sl':slides,'w':[],'q':None,'microId':item['id']})

data='window.EE_MICRO='+json.dumps(ordered,ensure_ascii=False)+';\n'
data+='Object.assign(EE_GENRES,'+json.dumps({v[0]:k for k,v in genres.items()},ensure_ascii=False)+');\n'
data+="window.EE_GENRES=Object.fromEntries(['daily','travel','space','science','tech','food','music','math','animal','history','film','sport','environment','work','learning','art','words','nyc','money','dino','serial'].filter(k=>EE_GENRES[k]).map(k=>[k,EE_GENRES[k]]));\n"
data+='EE_SHORTS.push(...'+json.dumps(shorts,ensure_ascii=False)+');\n'
# Data block belongs inside the initial data script, before the main closure.
block('STUDY_DATA', data, 'window.EE_TOPICS = [')
block('SPEECH_PROFILE', (ROOT/'speech-profile.js').read_text(encoding='utf-8'), '/* ================= speech ================= */')
block('STUDY_ENGINE', (ROOT/'study-engine.js').read_text(encoding='utf-8'), '/* ================= boot ================= */')
block('STUDY_LAB', (ROOT/'study-lab.js').read_text(encoding='utf-8'), '/* ================= boot ================= */')
change("const GCOL={dino:", "const GCOL={daily:'#238579',space:'#4253A0',tech:'#5364AA',food:'#C26A35',music:'#AD4074',film:'#76569F',sport:'#308069',environment:'#4A8057',work:'#49738F',learning:'#967A37',art:'#B45D71',dino:")
# Short-to-retrieval navigation, preserving the existing playback/quiz actions.
change("const tail='<div class=\"row\"><button", "const tail=(it.s.microId?'<div class=\"row\"><button class=\"btn primary\" data-labshort=\"'+it.s.microId+'\">この内容を思い出して話す</button></div>':'')+'<div class=\"row\"><button")
change("  ov.hidden=false;", "  ov.hidden=false;\n  const recallBtn=ov.querySelector('[data-labshort]');if(recallBtn)recallBtn.onclick=()=>{LAB.id=it.s.microId;LAB.topic='all';LAB.queue=false;showTab('lab:recall');};")
# Check added material first, so a typo stops the build with a readable message.
import sys
sys.path.insert(0, str(ROOT / 'materials'))
import validate
if validate.main([]):
    raise SystemExit('materials/ に問題があります。上の一覧を直してから、もう一度実行してください。')
from video_content import export, export_decks, NEW_SHORTS
long_lessons, phrase_cards = export()
from curriculum import build_curriculum
block('CURRICULUM_DATA', 'window.EE_CURRICULUM='+json.dumps(build_curriculum(long_lessons, NEW_SHORTS),ensure_ascii=False)+';\n', 'window.EE_TOPICS = [')
block('VIDEO_DATA', 'window.EE_LONG='+json.dumps(long_lessons,ensure_ascii=False)+';\nEE_CARDS.push(...'+json.dumps(phrase_cards,ensure_ascii=False)+');\nEE_SHORTS.push(...'+json.dumps(NEW_SHORTS,ensure_ascii=False)+');\nwindow.EE_DECKS='+json.dumps(export_decks(),ensure_ascii=False)+';\n', 'window.EE_TOPICS = [')
# More backgrounds/items for the illustration kit (art-extra.js runs inside the ART closure).
block('ART_EXTRA', (ROOT/'art-extra.js').read_text(encoding='utf-8'), '  IT.triceratops=IT.trike;')
block('ART_TOPIC', (ROOT/'art-topic.js').read_text(encoding='utf-8'), '  IT.triceratops=IT.trike;')
change("if(b.stars)s+=st;if(b.grid)s+=gr;", "if(b.stars)s+=st;if(b.grid)s+=gr;if(b.x)s+=b.x;")
# Genre avatars reuse the illustration kit's item shapes.
change("  return {draw:draw,names:Object.keys(IT),bgs:Object.keys(BG)};", "  return {draw:draw,names:Object.keys(IT),bgs:Object.keys(BG),shape:k=>IT[k]?IT[k].d:''};")
block('VIDEO_APP', (ROOT/'video-app.js').read_text(encoding='utf-8-sig'), '/* ================= boot ================= */')
block('PHONEME_LAB', (ROOT/'phoneme-lab.js').read_text(encoding='utf-8'), '/* ================= boot ================= */')
css=(ROOT/'video-app.css').read_text(encoding='utf-8-sig')
css_marker='/* BEGIN VIDEO_CSS */'
if css_marker in html:
    html=re.sub(r'/\* BEGIN VIDEO_CSS \*/.*?/\* END VIDEO_CSS \*/',lambda _:css_marker+'\n'+css+'\n/* END VIDEO_CSS */',html,flags=re.S)
else:
    html=html.replace('</style>',css_marker+'\n'+css+'\n/* END VIDEO_CSS */\n</style>',1)
html=html.replace("setTimeout(()=>spPlay(it,SP.it===it?SP.slide:0),50);", "setTimeout(()=>{if(curTab==='shorts')spPlay(it,SP.it===it?SP.slide:0);},50);")
# Do not allow delayed short playback to escape into another page.
html=html.replace("if(SH.active===i)spPlay(it,0);", "if(curTab==='shorts'&&SH.active===i)spPlay(it,0);")
# materials/EXISTING.md: what the app already contains, so people or other AIs adding material can avoid duplicates.
def write_existing():
    builtin = re.findall(r'\{id:"([^"]+)",g:"([a-z]+)",(?:ep:\d+,)?t:"([^"]+)"', html)
    lines = ['# 既存の教材一覧（build_site.py が自動生成。手で編集しない）', '',
             '新しい教材を作るときは、ここにある id・key・題材・フレーズと重ならないようにしてください。', '',
             f'## ショート（{len(builtin) + len(NEW_SHORTS)}本）', '', 'id | 分野 | タイトル', '---|---|---']
    lines += [f'{i} | {g} | {t}' for i, g, t in builtin]
    lines += [f"{s['id']} | {s['g']} | {s['t']}" for s in NEW_SHORTS]
    lines += ['', f'## 長文（{len(long_lessons)}本）', '', 'key | 分野 | タイトル', '---|---|---']
    lines += [f"{l['id'][5:]} | {l['g']} | {l['t']}" for l in long_lessons]
    old = re.findall(r'\["b\d+","([^"]+)"', html)
    lines += ['', f'## フレーズ（{len(old) + len(phrase_cards)}個）', '', ' / '.join(old + [c[1] for c in phrase_cards]), '']
    (ROOT / 'materials' / 'EXISTING.md').write_text('\n'.join(lines), encoding='utf-8')
write_existing()
source.write_text(html,encoding='utf-8')
out=ROOT/'docs'  # GitHub Pages: Settings > Pages > Deploy from a branch > /docs
out.mkdir(exist_ok=True)
(out/'index.html').write_text(html,encoding='utf-8')
(out/'.nojekyll').write_text('',encoding='utf-8')
for name in ['README.md','HVPT_PACK.md','CONTENT_EXPANSION_850.md']:
    origin=ROOT/('GITHUB_PAGES_README.md' if name=='README.md' else name)
    if origin.exists():(out/name).write_bytes(origin.read_bytes())
with zipfile.ZipFile(ROOT/'english-express-github-pages.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['index.html','.nojekyll','README.md','HVPT_PACK.md','CONTENT_EXPANSION_850.md']:
        if (out/name).exists(): z.write(out/name,name)
print(f'Built standalone index.html + {len(long_lessons)} long readings + {len(phrase_cards)} new phrases + {len(NEW_SHORTS)} new shorts + GitHub Pages ZIP')
