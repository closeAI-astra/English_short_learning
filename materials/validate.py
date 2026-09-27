"""Check added English Express material before building.

Usage:  python materials/validate.py            (checks every materials/*.json)
        python materials/validate.py file.json  (checks the given files)
build_site.py runs this automatically and stops if anything is wrong.
"""
import json, re, sys
from pathlib import Path

BGS = set(('day,dusk,night,sea,desert,forest,space,paper,snow,city,'
            'office,meeting,cafe,airport,rain,dawn,autumn,spring,library,stage,underwater,warehouse,'
            'street,shop,hotel,kitchen,recycling').split(','))
ITEMS = set(('bowl,laptop,film,ball,palette,chat,sun,moon,cloud,planet,plane,bird,bee,mountain,tree,palm,flower,rock,'
             'volcano,trex,sauropod,raptor,trike,pterosaur,fish,whale,octopus,egg,bone,skyline,building,bridge,train,ship,'
             'rocket,pyramid,flag,globe,pin,crown,book,scroll,clock,coin,chart,bulb,atom,magnifier,spiral,fib,pi,sine,'
             'primes,dice,infinity,heart,note,wave,triceratops,'
             'person,people,speaker,desk,phone,mail,calendar,document,briefcase,cup,truck,bus,car,bicycle,house,store,factory,'
             'cart,handshake,mic,headphones,camera,ticket,suitcase,umbrella,key,gear,box,printer,trophy,pencil,clipboard,target,'
             'megaphone,bag,badge,map,hourglass,check,wrench,plant,mouth,ear,'
             'bottle,cap,recycle,tshirt,bin,signal,elevator,stairs,doorway,price,coupon,receipt,tipjar,popcorn,'
             'passport,seat,boardingpass,menu,chair,battery,plug,bell,projector,speech,question,wordcards,measure,'
             'parcel,thermometer,window').split(','))
GENRES = set('daily,travel,space,science,tech,food,music,math,animal,history,film,sport,environment,work,learning,art,words,nyc,money,dino'.split(','))
HERE = Path(__file__).resolve().parent

def existing_phrases():
    """Phrases already built into the app (read as text, so a broken material file cannot crash this check)."""
    src = (HERE.parent / 'video_content.py').read_text(encoding='utf-8')
    block = src.split("PHRASE_TEXT = '''", 1)[1].split("'''", 1)[0]
    out = {line.split('|')[0].strip().lower() for line in block.strip().splitlines()}
    html = (HERE.parent / 'english-express.html').read_text(encoding='utf-8')
    for m in re.finditer(r'\["b\d+","([^"]+)"', html):
        out.add(m.group(1).lower())
    return out

def check_scene(sc, err, where, allow_big=True):
    parts = sc.split('|')
    if parts[0] not in BGS: err.append(f'{where}: bad background {parts[0]!r}')
    items = [p for p in parts[1:] if not p.startswith('big:')]
    bigs = [p for p in parts[1:] if p.startswith('big:')]
    for p in items:
        if p not in ITEMS: err.append(f'{where}: unknown item {p!r}')
    if len(items) > 3: err.append(f'{where}: more than 3 items')
    if bigs and (not allow_big or len(bigs[0]) - 4 > 14): err.append(f'{where}: big text too long / not allowed')

def en_sents(t): return re.split(r'(?<=[.!?])\s+', t.strip())
def ja_sents(t): return [x for x in re.split(r'(?<=。)', t.strip()) if x]

def v_phrases(data, err, seen):
    if not isinstance(data, dict) or not all(k in data for k in ('deck', 'level', 'phrases')):
        err.append('phrases_*.json must be {"deck": "...", "level": "...", "phrases": [[en, ja, example, example_ja], ...]}'); return
    if 'scene' in data: check_scene(data['scene'], err, 'deck scene', allow_big=False)
    old = existing_phrases()
    for i, row in enumerate(data['phrases']):
        w = f'phrase[{i}]'
        if not (isinstance(row, list) and len(row) == 4 and all(isinstance(x, str) and x.strip() for x in row)):
            err.append(f'{w}: must be [en, ja, example, example_ja]'); continue
        en, ja, ex, exja = row
        k = en.lower().strip()
        slug = re.sub(r'[^a-z0-9]+', '-', k).strip('-')
        if k in old: err.append(f'{w}: already in the app: {en!r}')
        if slug in seen['phrase']: err.append(f'{w}: duplicate {en!r} (also in {seen["phrase"][slug]})')
        seen['phrase'][slug] = seen['file']
        n = len(ex.split())
        if not 7 <= n <= 22: err.append(f'{w}: example has {n} words (7-22)')
        head = re.sub(r'[^a-z ]', '', k).split()
        if head and head[0][:4] not in ex.lower() and head[-1][:4] not in ex.lower():
            err.append(f'{w}: example does not seem to contain the phrase {en!r}')

def v_stories(data, err, seen):
    keys = seen['story']
    for i, s in enumerate(data):
        w = f'story[{i}]'
        for f in ['key', 'g', 'title', 'level', 'scene', 'paras', 'qs']:
            if f not in s: err.append(f'{w}: missing {f}')
        if err: return
        w = f"story {s['key']}"
        if s['key'] in keys or not re.fullmatch(r'[a-z0-9]+', s['key']): err.append(f'{w}: key must be unique lowercase a-z0-9 (already used: {keys.get(s["key"], "")})')
        keys[s['key']] = seen['file']
        if s['g'] not in GENRES: err.append(f'{w}: bad genre')
        sc = s['scene'].split('|')
        if len(sc) < 2: err.append(f'{w}: scene needs background|item')
        check_scene(s['scene'], err, w, allow_big=False)
        if not 6 <= len(s['paras']) <= 8: err.append(f'{w}: needs 6-8 paragraphs')
        total = 0
        for j, (en, ja) in enumerate(s['paras']):
            total += len(en.split())
            a, b = en_sents(en), ja_sents(ja)
            if len(a) != len(b): err.append(f'{w} para {j}: {len(a)} English sentences vs {len(b)} Japanese sentences')
            if re.search(r'\b(Mr|Ms|Mrs|Dr|St|a\.m|p\.m|e\.g|i\.e|etc|vs|No)\.', en): err.append(f'{w} para {j}: abbreviation with period breaks sentence split')
            if re.search(r'[？！]', ja): err.append(f'{w} para {j}: Japanese must end sentences with 。 only')
        if not 330 <= total <= 460: err.append(f'{w}: {total} words (330-460)')
        if len(s['qs']) != 4: err.append(f'{w}: needs 4 questions')
        if 'explanations' in s and (len(s['explanations']) != len(s['qs']) or not all(isinstance(x, str) and x.strip() for x in s['explanations'])):
            err.append(f'{w}: explanations must contain one nonempty explanation per question')
        for q in s['qs']:
            if not (len(q) == 3 and len(q[1]) == 3 and q[2] in (0, 1, 2)): err.append(f'{w}: bad question {q}')
        if len({q[2] for q in s['qs']}) < 2: err.append(f'{w}: vary the answer positions')

def v_shorts(data, err, seen):
    ids = seen['short']
    for i, s in enumerate(data):
        w = f"short {s.get('id', i)}"
        if s.get('id') in ids or not re.fullmatch(r'[a-z][a-z0-9-]{1,40}', s.get('id', '')): err.append(f'{w}: id must be unique lowercase like x063 (already used: {ids.get(s.get("id"), "")})')
        ids[s.get('id')] = seen['file']
        if s.get('g') not in GENRES: err.append(f'{w}: bad genre')
        if not s.get('t'): err.append(f'{w}: missing title')
        if not 4 <= len(s.get('sl', [])) <= 6: err.append(f'{w}: needs 4-6 slides')
        text = ''
        for j, sl in enumerate(s.get('sl', [])):
            if len(sl) != 3: err.append(f'{w} slide {j}: [scene, en, ja]'); continue
            check_scene(sl[0], err, f'{w} slide {j}')
            chunks = [c.strip() for c in sl[1].split(' / ')]
            if len(chunks) < 2: err.append(f'{w} slide {j}: split into sense groups with " / "')
            for c in chunks:
                if not 1 <= len(c.split()) <= 7: err.append(f'{w} slide {j}: chunk {c!r} should be 1-7 words')
            n = len(sl[1].replace(' / ', ' ').split())
            if not 8 <= n <= 26: err.append(f'{w} slide {j}: {n} words (8-26)')
            text += ' ' + sl[1].lower()
        ws = s.get('w', [])
        if len(ws) != 5: err.append(f'{w}: needs 5 vocabulary items')
        for word, ja in ws:
            stem = word.lower().split()[0][:4]
            if stem not in text: err.append(f'{w}: vocab {word!r} not found in the text')
        q = s.get('q')
        if 'explanation' in s and not (isinstance(s['explanation'], str) and s['explanation'].strip()):
            err.append(f'{w}: explanation must be a nonempty string')
        if not (isinstance(q, list) and len(q) == 3 and len(q[1]) == 4 and q[2] in range(4)): err.append(f'{w}: q must be [question, [4 options], index]')

def builtin_ids():
    """Ids that the app already uses, so new files cannot collide with them."""
    html = (HERE.parent / 'english-express.html').read_text(encoding='utf-8')
    shorts = {m.group(1): 'built-in' for m in re.finditer(r'\{id:"([^"]+)",g:"', html)}
    src = (HERE.parent / 'video_content.py').read_text(encoding='utf-8') + (HERE.parent / 'extra_video_content.py').read_text(encoding='utf-8')
    stories = {m.group(1): 'built-in' for m in re.finditer(r"^\('([a-z0-9]+)','[a-z]+','", src, flags=re.M)}
    return shorts, stories

def main(argv):
    files = [Path(f) for f in argv] or sorted(f for f in HERE.glob('*.json') if not f.name.startswith('_'))
    shorts, stories = builtin_ids()
    seen = {'phrase': {}, 'story': stories, 'short': shorts, 'file': ''}
    bad = 0
    for f in files:
        err = []
        seen['file'] = f.name
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            print(f'{f.name}: JSON の書き方が壊れています（{e.lineno}行目 {e.colno}文字目: {e.msg}）。カンマ・引用符・括弧を確認してください。')
            bad += 1; continue
        kind = f.name.split('_')[0]
        if kind not in ('phrases', 'stories', 'shorts'):
            print(f'{f.name}: ファイル名は phrases_ / stories_ / shorts_ で始めてください'); bad += 1; continue
        {'phrases': v_phrases, 'stories': v_stories, 'shorts': v_shorts}[kind](data, err, seen)
        n = len(data['phrases']) if kind == 'phrases' and isinstance(data, dict) and 'phrases' in data else len(data)
        print(f'{f.name}: {n} items, {len(err)} problems')
        for e in err[:80]: print('  -', e)
        bad += len(err)
    return bad

if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1:]) else 0)
