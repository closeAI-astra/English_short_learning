"""Phoneme-level pronunciation scoring (no torch needed in this module).

Pipeline
  1. text  -> expected phonemes (espeak-ng via phonemizer)
  2. audio -> frame-wise phoneme log-probabilities (wav2vec2 CTC, done in app.py)
  3. CTC forced alignment of the expected phonemes  -> frames of each phoneme
  4. GOP per phoneme: mean over its frames of  log P(expected) - max_q log P(q)
  5. free phoneme recognition + edit-distance alignment -> substitution / deletion / insertion
  6. map each problem to Japanese articulation tips
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

import numpy as np

# ---------------------------------------------------------------- G2P
_PHONEMIZER_READY = False


def _init_phonemizer():
    global _PHONEMIZER_READY
    if _PHONEMIZER_READY:
        return
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    import espeakng_loader

    EspeakWrapper.set_library(espeakng_loader.get_library_path())
    EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
    _PHONEMIZER_READY = True


def words_of(text: str) -> list[str]:
    text = text.replace("’", "'").replace("‘", "'")
    return [w for w in re.findall(r"[A-Za-z0-9']+(?:[-'][A-Za-z0-9]+)*", text) if re.search(r"[A-Za-z0-9]", w)]


def expected_phones(text: str) -> list[tuple[str, list[str]]]:
    """[(word, [espeak phones])]"""
    _init_phonemizer()
    from phonemizer import phonemize
    from phonemizer.separator import Separator

    ws = words_of(text)
    if not ws:
        return []
    out = phonemize(ws, language="en-us", backend="espeak",
                    separator=Separator(phone=" ", word="", syllable=""),
                    strip=True, with_stress=False, preserve_punctuation=False, njobs=1)
    return [(w, [p for p in ph.split() if p]) for w, ph in zip(ws, out)]


# ---------------------------------------------------------------- vocab mapping
_LENGTH = "ː"


def to_tokens(phone: str, vocab: dict[str, int]) -> list[str]:
    """Map one espeak phone onto model vocab tokens (greedy longest match)."""
    if phone in vocab:
        return [phone]
    if phone.replace(_LENGTH, "") in vocab:
        return [phone.replace(_LENGTH, "")]
    toks, i = [], 0
    while i < len(phone):
        for j in range(len(phone), i, -1):
            piece = phone[i:j]
            cand = piece if piece in vocab else piece.replace(_LENGTH, "")
            if cand and cand in vocab:
                toks.append(cand)
                i = j
                break
        else:
            i += 1  # unknown symbol: skip
    return toks


@dataclass
class Target:
    word_idx: int
    word: str
    phone: str   # model token
    tid: int


def build_targets(words: list[tuple[str, list[str]]], vocab: dict[str, int]) -> list[Target]:
    ts = []
    for wi, (w, phones) in enumerate(words):
        for ph in phones:
            for tok in to_tokens(ph, vocab):
                ts.append(Target(wi, w, tok, vocab[tok]))
    return ts


# ---------------------------------------------------------------- CTC tools
def greedy_decode(logp: np.ndarray, blank: int) -> list[int]:
    ids = logp.argmax(axis=1)
    out, prev = [], -1
    for i in ids:
        if i != prev and i != blank:
            out.append(int(i))
        prev = i
    return out


def ctc_force_align(logp: np.ndarray, tids: list[int], blank: int) -> list[list[int]] | None:
    """Viterbi CTC alignment. Returns frames assigned to each target token."""
    T, L = logp.shape[0], len(tids)
    if L == 0:
        return []
    S = 2 * L + 1
    lab = np.full(S, blank, dtype=np.int64)
    lab[1::2] = tids
    neg = -1e30
    dp = np.full((T, S), neg)
    bp = np.zeros((T, S), dtype=np.int8)  # 0 stay, 1 from s-1, 2 from s-2
    dp[0, 0] = logp[0, blank]
    dp[0, 1] = logp[0, lab[1]]
    skip_ok = np.zeros(S, dtype=bool)
    for s in range(2, S):
        skip_ok[s] = lab[s] != blank and lab[s] != lab[s - 2]
    for t in range(1, T):
        prev = dp[t - 1]
        c0 = prev
        c1 = np.concatenate(([neg], prev[:-1]))
        c2 = np.concatenate(([neg, neg], prev[:-2]))
        c2 = np.where(skip_ok, c2, neg)
        stack = np.stack([c0, c1, c2])
        arg = stack.argmax(axis=0)
        dp[t] = stack[arg, np.arange(S)] + logp[t, lab]
        bp[t] = arg
    ends = [S - 1, S - 2] if S >= 2 else [S - 1]
    s = max(ends, key=lambda k: dp[T - 1, k])
    if dp[T - 1, s] <= neg / 2:
        return None  # audio too short for the sentence
    frames: list[list[int]] = [[] for _ in range(L)]
    for t in range(T - 1, -1, -1):
        if s % 2 == 1:
            frames[s // 2].append(t)
        s -= int(bp[t, s])
    for f in frames:
        f.reverse()
    return frames


def edit_align(a: list[int], b: list[int]):
    """Levenshtein alignment. ops: ('eq'|'sub', i, j), ('del', i, None), ('ins', None, j)."""
    n, m = len(a), len(b)
    D = np.zeros((n + 1, m + 1), dtype=np.int32)
    D[:, 0] = np.arange(n + 1)
    D[0, :] = np.arange(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = min(D[i - 1, j] + 1, D[i, j - 1] + 1, D[i - 1, j - 1] + (a[i - 1] != b[j - 1]))
    ops, i, j = [], n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and D[i, j] == D[i - 1, j - 1] + (a[i - 1] != b[j - 1]):
            ops.append(("eq" if a[i - 1] == b[j - 1] else "sub", i - 1, j - 1))
            i, j = i - 1, j - 1
        elif i > 0 and D[i, j] == D[i - 1, j] + 1:
            ops.append(("del", i - 1, None))
            i -= 1
        else:
            ops.append(("ins", None, j - 1))
            j -= 1
    ops.reverse()
    return ops


# ---------------------------------------------------------------- scoring
VOWELS = set("aeiouæɑɒɔəɛɜɪʊʌɐᵻɚɝyøœɯɤɨʉ")


def is_vowel(tok: str) -> bool:
    return bool(tok) and tok[0] in VOWELS


@dataclass
class PhoneResult:
    word_idx: int
    phone: str
    score: float          # posterior ratio in (0, 1]
    status: str           # ok | weak | sub | del
    heard: str = ""       # competitor / recognized phone


@dataclass
class Report:
    words: list[str]
    phones: list[PhoneResult]
    inserts: list[tuple[int, str]]   # (after target index, inserted phone)
    recognized: list[str]
    overall: float
    completeness: float
    issues: list[dict] = field(default_factory=list)
    speech_sec: float = 0.0
    phone_rate: float = 0.0
    long_pauses: list = field(default_factory=list)


WEAK = 0.5   # posterior ratio below this -> flagged
FRAME_SEC = 0.02
PAUSE_SEC = 0.35


def score(words: list[tuple[str, list[str]]], logp: np.ndarray, vocab: dict[str, int], blank: int) -> Report:
    inv = {v: k for k, v in vocab.items()}
    targets = build_targets(words, vocab)
    if not targets:
        raise ValueError("英文から音素を作れませんでした。")
    tids = [t.tid for t in targets]
    frames = ctc_force_align(logp, tids, blank)
    if frames is None:
        raise ValueError("録音が短すぎます。文を最後まで読んでから止めてください。")

    special = {i for tok, i in vocab.items() if tok.startswith("<") or tok in ("|", " ")} | {blank}
    mask = np.ones(logp.shape[1], dtype=bool)
    mask[list(special)] = False
    masked = np.where(mask[None, :], logp, -1e30)
    best = masked.max(axis=1)

    phones: list[PhoneResult] = []
    for t, fr in zip(targets, frames):
        fr = np.array(fr, dtype=int)
        gop = float(np.mean(logp[fr, t.tid] - best[fr]))
        comp = masked[fr].mean(axis=0)
        comp[t.tid] = -1e30
        phones.append(PhoneResult(t.word_idx, t.phone, float(np.exp(gop)), "ok", inv.get(int(comp.argmax()), "")))

    rec = greedy_decode(logp, blank)
    rec = [r for r in rec if r not in special]
    ops = edit_align(tids, rec)
    inserts: list[tuple[int, str]] = []
    last_i = -1
    for op, i, j in ops:
        if op == "sub":
            phones[i].status = "sub"
            phones[i].heard = inv.get(rec[j], "?")
            last_i = i
        elif op == "del":
            phones[i].status = "del"
            phones[i].heard = ""
            last_i = i
        elif op == "ins":
            inserts.append((last_i, inv.get(rec[j], "?")))
        else:
            last_i = i
    for p in phones:
        if p.status == "ok" and p.score < WEAK:
            p.status = "weak"

    overall = float(np.mean([p.score for p in phones])) * 100
    completeness = 100.0 * sum(p.status != "del" for p in phones) / len(phones)
    rep = Report([w for w, _ in words], phones, inserts, [inv.get(r, "?") for r in rec], overall, completeness)

    # fluency: wav2vec2 emits one frame per 20 ms
    spans: dict[int, list[int]] = {}
    for t, fr in zip(targets, frames):
        if fr:
            s = spans.setdefault(t.word_idx, [fr[0], fr[-1]])
            s[0], s[1] = min(s[0], fr[0]), max(s[1], fr[-1])
    order = [spans[k] for k in sorted(spans)]
    if order:
        dur = (order[-1][1] - order[0][0] + 1) * FRAME_SEC
        rep.speech_sec = dur
        rep.phone_rate = len(targets) / dur if dur > 0 else 0.0
        rep.long_pauses = [(rep.words[a], rep.words[b]) for (a, b), (sa, sb) in
                           zip(zip(sorted(spans)[:-1], sorted(spans)[1:]), zip(order[:-1], order[1:]))
                           if (sb[0] - sa[1]) * FRAME_SEC >= PAUSE_SEC]
    rep.issues = diagnose(rep)
    return rep


# ---------------------------------------------------------------- Japanese tips
TIPS = {
    "L": ("L", "/l/", "舌先を上の前歯のすぐ裏の歯ぐきに押し当て、当てたまま声を出す。語末の L は舌の奥も持ち上げ「ウ」寄りに。",
          "日本語のラ行（舌先で一瞬はじく音）になりがち。舌を当てたまま保つ。", "light / right"),
    "R": ("R", "/ɹ/", "舌先はどこにも触れない。舌先を少し奥に引き、唇を丸めて突き出す。「ゥラ」と唇から入る。",
          "舌先が歯ぐきに当たるとラ行か L になる。", "right / light"),
    "ER": ("R の響きの母音", "/ɚ/ /ɜː/", "R の舌の形（舌先を引いて浮かせる）を保ったまま母音を出す。口はあまり開けない。",
           "「アー」と口を開けてしまう（bird が bud に聞こえる）。", "bird / bud"),
    "TH": ("TH", "/θ/ /ð/", "舌先を上の前歯の先に軽く当て、そのすき間から息（θ）か声（ð）を出す。",
           "s・z・d に置き換わる（think が sink、they が day）。", "think / sink"),
    "FV": ("F と V", "/f/ /v/", "上の前歯を下唇の内側に軽く乗せ、すき間から息（f）か声（v）を出す。",
           "v が b に、f が両唇の「フ」になる。", "very / berry"),
    "AE": ("æ（cat の a）", "/æ/", "「エ」の口の形のまま、あごを下げて「ア」と言う。口角を横に引く。",
           "日本語の「ア」になり cat が cut に聞こえる。", "cat / cut"),
    "W": ("W", "/w/", "唇を小さく丸めて突き出してから一気に開く。", "唇の丸めが弱く、ただの「ウ」になる。", "wood / hood"),
    "SH": ("S と SH", "/s/ /ʃ/", "s は舌先を歯ぐきに近づけて細く鋭い息。sh は舌を少し奥へ引き唇を丸める。",
           "日本語の「シ」は sh 寄りで、see が she に聞こえる。", "see / she"),
    "NG": ("NG", "/ŋ/", "舌の奥を上あごの奥に付けたまま鼻から声を出して終える。", "最後に「グ」を付けてしまう。", "sing / sin"),
    "EPEN": ("子音のあとの余分な母音", "", "子音の形を作ったらそこで止める。語末の t・d・k は息を止めるくらい弱くてよい。",
             "日本語の癖で子音のあとに u・o を足す（stop が「ストップ」、pick が picky に近づく）。", "pick / picky"),
    "IH": ("短い i と長い i", "/ɪ/ /iː/", "ɪ は力を抜いて短く、口の開きはやや広め（エに寄る）。iː は口角を横に引いて長く。",
           "ɪ と iː が同じ「イ」になる（sit と seat が区別されない）。", "sit / seat"),
    "VOWEL": ("母音の響き", "", "手本を聞いて、口の開き（あごの高さ）と唇の丸めを真似る。日本語の5母音に当てはめない。",
              "英語の母音は日本語より種類が多く、「ア」「オ」にまとめてしまいがち。", ""),
    "CONS": ("子音", "", "手本を聞いて、息が出る位置（唇・歯・歯ぐき・のど）を意識する。", "日本語にない子音は近い日本語の音に置き換わりがち。", ""),
}


def tip_key(expected: str, heard: str, status: str) -> str:
    e, h = expected, heard
    if e == "l":
        return "L"
    if e in ("ɹ", "r"):
        return "R"
    if e in ("ɚ", "ɝ", "ɜ", "ɜː"):
        return "ER"
    if e in ("θ", "ð"):
        return "TH"
    if e in ("f", "v"):
        return "FV"
    if e == "æ":
        return "AE"
    if e == "w":
        return "W"
    if e in ("s", "ʃ") and h in ("s", "ʃ", "ɕ"):
        return "SH"
    if e == "ŋ":
        return "NG"
    if e in ("ɪ", "i", "iː", "ᵻ"):
        return "IH"
    return "VOWEL" if is_vowel(e) else "CONS"


def diagnose(rep: Report) -> list[dict]:
    groups: dict[str, dict] = {}

    def add(key, word, detail):
        g = groups.setdefault(key, {"key": key, "items": []})
        g["items"].append((word, detail))

    for p in rep.phones:
        if p.status == "ok":
            continue
        w = rep.words[p.word_idx]
        if p.status == "sub":
            d = f"/{p.phone}/ が /{p.heard}/ に聞こえる"
        elif p.status == "del":
            d = f"/{p.phone}/ が聞こえない"
        else:
            d = f"/{p.phone}/ が弱い（{p.score * 100:.0f}点・/{p.heard}/ に近い）"
        add(tip_key(p.phone, p.heard, p.status), w, d)
    for after, ph in rep.inserts:
        if is_vowel(ph) and after >= 0 and not is_vowel(rep.phones[after].phone):
            add("EPEN", rep.words[rep.phones[after].word_idx], f"/{rep.phones[after].phone}/ のあとに /{ph}/ が入った")
    order = sorted(groups.values(), key=lambda g: -len(g["items"]))
    return order


# ---------------------------------------------------------------- rendering
def _chip(p: PhoneResult) -> str:
    colors = {"ok": ("#1f7a45", "#e3f3e9"), "weak": ("#8a5a00", "#fff1c9"), "sub": ("#b3261e", "#fde4e1"), "del": ("#6b6f73", "#ececec")}
    fg, bg = colors[p.status]
    title = {"ok": f"{p.score * 100:.0f}点", "weak": f"{p.score * 100:.0f}点・/{p.heard}/ に近い",
             "sub": f"/{p.heard}/ に聞こえる", "del": "聞こえない"}[p.status]
    body = html.escape(p.phone)
    if p.status == "sub":
        body += f'<span style="font-size:11px">→{html.escape(p.heard)}</span>'
    deco = "line-through" if p.status == "del" else "none"
    return (f'<span title="{html.escape(title)}" style="display:inline-block;margin:1px;padding:1px 6px;border-radius:6px;'
            f'font-family:monospace;font-size:15px;color:{fg};background:{bg};text-decoration:{deco}">{body}</span>')


def render_html(rep: Report) -> str:
    ov = rep.overall
    col = "#1f7a45" if ov >= 80 else ("#8a5a00" if ov >= 60 else "#b3261e")
    h = [f'<div style="display:flex;gap:24px;flex-wrap:wrap;align-items:baseline;margin-bottom:10px">'
         f'<div><div style="font-size:12px;opacity:.7">発音スコア（音素ごとの確からしさの平均）</div>'
         f'<div style="font-size:40px;font-weight:700;color:{col};font-family:monospace">{ov:.0f}</div></div>'
         f'<div><div style="font-size:12px;opacity:.7">網羅度（抜けなかった音素）</div>'
         f'<div style="font-size:24px;font-family:monospace">{rep.completeness:.0f}%</div></div>'
         f'<div><div style="font-size:12px;opacity:.7">話す速さ（音素/秒）</div>'
         f'<div style="font-size:24px;font-family:monospace">{rep.phone_rate:.1f}</div></div>'
         f'<div><div style="font-size:12px;opacity:.7">語の間の長い間（0.35秒以上）</div>'
         f'<div style="font-size:24px;font-family:monospace">{len(rep.long_pauses)}</div></div></div>']
    if rep.long_pauses:
        h.append('<div style="font-size:12px;opacity:.8;margin-bottom:8px">間が空いた所: ' + "、".join(html.escape(f"{a} / {b}") for a, b in rep.long_pauses[:6])
                 + '（塊の切れ目なら自然。塊の途中なら、つなげて読む練習を）</div>')
    h.append('<div style="display:flex;flex-wrap:wrap;gap:10px 14px;margin-bottom:6px">')
    for wi, w in enumerate(rep.words):
        ps = [p for p in rep.phones if p.word_idx == wi]
        bad = any(p.status != "ok" for p in ps)
        h.append(f'<div style="border:1px solid {"#e0a9a3" if bad else "#cfd6d1"};border-radius:8px;padding:4px 6px">'
                 f'<div style="font-weight:700;font-size:15px">{html.escape(w)}</div><div>{"".join(_chip(p) for p in ps)}</div></div>')
    h.append("</div>")
    h.append('<div style="font-size:12px;opacity:.75;margin-bottom:12px">緑=良い／黄=弱い／赤=別の音に聞こえる／灰色の取り消し線=聞こえない。音素にカーソルを乗せると点数が出ます。'
             f'<br>認識された音素列: <span style="font-family:monospace">{html.escape(" ".join(rep.recognized))}</span></div>')
    if not rep.issues:
        h.append('<div style="padding:10px 12px;border-radius:8px;background:#e3f3e9;color:#1f4d33">大きな問題は見つかりませんでした。次は手本と同じ速さ・リズムで読んでみてください。</div>')
    for g in rep.issues[:5]:
        name, ipa, how, trap, pair = TIPS[g["key"]]
        items = "".join(f"<li><b>{html.escape(w)}</b>: {html.escape(d)}</li>" for w, d in g["items"][:6])
        h.append(f'<div style="border:1px solid #cfd6d1;border-left:5px solid #fccc0a;border-radius:8px;padding:10px 12px;margin-bottom:10px">'
                 f'<div style="font-weight:700;font-size:16px">{html.escape(name)} <span style="font-family:monospace;opacity:.7;font-weight:400">{html.escape(ipa)}</span></div>'
                 f'<ul style="margin:6px 0 6px 18px;padding:0">{items}</ul>'
                 f'<div><b>舌・唇</b>: {html.escape(how)}</div><div><b>罠</b>: {html.escape(trap)}</div>'
                 + (f'<div><b>聞き比べ</b>: {html.escape(pair)}</div>' if pair else "") + "</div>")
    return "".join(h)


def summary_text(sentence: str, rep: Report) -> str:
    lines = [f"手本: {sentence}", f"発音スコア: {rep.overall:.0f} / 網羅度: {rep.completeness:.0f}%",
             f"話す速さ: {rep.phone_rate:.1f} 音素/秒 / 長い間: " + ("、".join(f"{a}/{b}" for a, b in rep.long_pauses) or "なし"),
             "音素ごとの結果（手本の音素→判定）:"]
    for wi, w in enumerate(rep.words):
        parts = []
        for p in rep.phones:
            if p.word_idx != wi:
                continue
            if p.status == "ok":
                parts.append(f"{p.phone}")
            elif p.status == "sub":
                parts.append(f"{p.phone}→{p.heard}")
            elif p.status == "del":
                parts.append(f"{p.phone}→(脱落)")
            else:
                parts.append(f"{p.phone}(弱{p.score * 100:.0f})")
        lines.append(f"  {w}: {' '.join(parts)}")
    if rep.inserts:
        lines.append("挿入された音素: " + ", ".join(ph for _, ph in rep.inserts))
    lines.append("")
    lines.append("上は wav2vec2 の音素認識による自動判定です。日本人学習者として、問題のある音ごとに舌・唇・あごの具体的な直し方と、30秒でできる練習を日本語で教えてください。")
    return "\n".join(lines)
