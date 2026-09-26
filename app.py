"""発音コーチ: 音素単位の発音評価（無料・ローカル実行）

起動:  uv run app.py
初回はモデル（約1.2GB）を自動ダウンロードします。2回目以降はオフラインでも動きます。
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import json
import os
import threading
from collections import Counter
from math import gcd
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

import numpy as np
import gradio as gr
from scipy.signal import resample_poly

import core
import learning
from video_content import export as video_materials

MODEL_ID = "facebook/wav2vec2-lv-60-espeak-cv-ft"
HERE = Path(__file__).resolve().parent
LOG = HERE / "results.csv"

DRILLS = [
    "The light on the right side is really bright.",
    "Laura drove a rental car along the river road.",
    "Please collect the correct files from the library.",
    "I think these three things are worth it.",
    "They thanked the other team on Thursday.",
    "We have a very good view of the valley.",
    "Five of my favorite berries are in the bowl.",
    "The first bird heard the word early.",
    "Her work at the firm starts on Thursday.",
    "I think it's a good idea to stop at the park.",
    "Would you walk with the woman to the wood shop?",
    "Can the manager handle that plan?",
    "She sells seashells by the seashore.",
    "Please sit in the seat next to the shelf.",
    "Passengers may now board the train on track four.",
    "Revenue rose eight percent compared with the same period last year.",
]

# ------------------------------------------------------------------ model
_lock = threading.Lock()
_model = None
_status = {"text": "モデルを準備中…"}


def load():
    global _model
    with _lock:
        if _model is not None:
            return _model
        import torch
        from huggingface_hub import hf_hub_download
        from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC

        def fetch(fn):
            try:  # use the local cache first so later runs work offline and skip update checks
                return hf_hub_download(MODEL_ID, fn, local_files_only=True)
            except Exception:
                return hf_hub_download(MODEL_ID, fn)

        with open(fetch("vocab.json"), encoding="utf-8") as f:
            vocab = json.load(f)
        if vocab and all(isinstance(v, dict) for v in vocab.values()):
            vocab = next(iter(vocab.values()))
        try:
            fe = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_ID, local_files_only=True)
        except Exception:
            fe = Wav2Vec2FeatureExtractor(feature_size=1, sampling_rate=16000, padding_value=0.0,
                                          do_normalize=True, return_attention_mask=True)
        try:
            model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID, local_files_only=True)
        except Exception:
            model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)
        model.eval()
        blank = model.config.pad_token_id
        if blank is None:
            blank = vocab.get("<pad>", 0)
        torch.set_num_threads(max(1, (os.cpu_count() or 2) - 1))
        _model = (torch, fe, model, vocab, int(blank))
        _status["text"] = "準備完了"
        return _model


def _preload():
    try:
        print("[pron-coach] loading model (first time downloads about 1.2 GB)...", flush=True)
        load()
        print("[pron-coach] model ready.", flush=True)
    except Exception as e:  # shown in the UI when judging
        _status["text"] = f"モデルの読み込みに失敗: {e}"
        print("[pron-coach] model load failed:", repr(e), flush=True)


def emissions(y16k: np.ndarray) -> np.ndarray:
    torch, fe, model, _, _ = load()
    x = fe(y16k, sampling_rate=16000, return_tensors="pt")
    with torch.inference_mode():
        logits = model(x.input_values).logits[0]
    return torch.log_softmax(logits.float(), dim=-1).cpu().numpy()


# ------------------------------------------------------------------ audio
def prep(audio) -> np.ndarray:
    if audio is None:
        raise gr.Error("先に録音してください。")
    sr, y = audio
    y = np.asarray(y)
    raw_dtype = y.dtype
    if y.ndim > 1:
        y = y.mean(axis=1)
    if np.issubdtype(raw_dtype, np.integer):
        y = y.astype(np.float32) / float(np.iinfo(raw_dtype).max)
    else:
        y = y.astype(np.float32)
    if int(sr) != 16000:
        g = gcd(int(sr), 16000)
        y = resample_poly(y, 16000 // g, int(sr) // g).astype(np.float32)
    peak = float(np.abs(y).max()) if y.size else 0.0
    print(f"[pron-coach] audio: sr={sr} dtype={raw_dtype} seconds={len(y) / 16000:.2f} peak={peak:.5f}", flush=True)
    if peak < 1e-5:
        raise gr.Error("音が入っていません（無音）。ブラウザのマイク許可と、録音欄で選んでいる入力デバイスを確認してください。")
    y = y / peak * 0.9  # small microphone levels are fine: normalize to a fixed peak
    idx = np.where(np.abs(y) > 0.05)[0]
    y = y[max(0, idx[0] - 3200): idx[-1] + 3200]
    if len(y) < 16000 * 0.4:
        raise gr.Error("録音が短すぎます。")
    return y


# ------------------------------------------------------------------ history
def log_result(sentence: str, rep: core.Report):
    new = not LOG.exists()
    with open(LOG, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["datetime", "sentence", "score", "completeness", "issues"])
        w.writerow([dt.datetime.now().strftime("%Y-%m-%d %H:%M"), sentence, f"{rep.overall:.0f}",
                    f"{rep.completeness:.0f}", " ".join(g["key"] for g in rep.issues)])


def history_html() -> str:
    if not LOG.exists():
        return "<p style='opacity:.7'>まだ記録がありません。</p>"
    with open(LOG, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return "<p style='opacity:.7'>まだ記録がありません。</p>"
    cnt = Counter(k for r in rows for k in (r.get("issues") or "").split() if k)
    top = "、".join(f"{core.TIPS[k][0]}（{n}回）" for k, n in cnt.most_common(5) if k in core.TIPS) or "なし"
    today = dt.date.today().isoformat()
    n_today = sum(1 for r in rows if r["datetime"].startswith(today))
    body = "".join(
        f"<tr><td>{html.escape(r['datetime'])}</td><td style='font-family:monospace;text-align:right'>{html.escape(r['score'])}</td>"
        f"<td>{html.escape(r['sentence'])}</td></tr>" for r in rows[-12:][::-1])
    return (f"<p>今日の判定回数: <b>{n_today}</b>　累計: <b>{len(rows)}</b></p>"
            f"<p>よく引っかかる音: <b>{html.escape(top)}</b></p>"
            f"<table style='width:100%;border-collapse:collapse;font-size:13px'><tr><th align='left'>日時</th><th>点</th><th align='left'>英文</th></tr>{body}</table>")


# ------------------------------------------------------------------ main action
def judge(sentence, audio):
    sentence = (sentence or "").strip()
    if not sentence:
        raise gr.Error("読む英文を入力してください。")
    y = prep(audio)
    try:
        _, _, _, vocab, blank = load()
    except Exception as e:
        raise gr.Error(f"モデルを読み込めませんでした（初回はネット接続が必要です）: {e}")
    words = core.expected_phones(sentence)
    logp = emissions(y)
    try:
        rep = core.score(words, logp, vocab, blank)
    except ValueError as e:
        raise gr.Error(str(e))
    log_result(sentence, rep)
    return core.render_html(rep), core.summary_text(sentence, rep), history_html()


SPEAK_JS = """(t, r) => {
  try { speechSynthesis.cancel(); } catch (e) {}
  const u = new SpeechSynthesisUtterance(t || '');
  const vs = speechSynthesis.getVoices().filter(v => /^en-US/i.test(v.lang));
  const v = vs.find(v => /(natural|neural|online)/i.test(v.name)) || vs.find(v => /(Aria|Jenny|Google US English|Samantha|Zira)/i.test(v.name)) || vs[0];
  if (v) { u.voice = v; u.lang = v.lang; } else { u.lang = 'en-US'; }
  u.rate = r;
  speechSynthesis.speak(u);
  return [];
}"""

_video_lessons, _video_phrases = video_materials()
DRILLS = list(dict.fromkeys(DRILLS + [c[3] for c in _video_phrases] + [l["sl"][0][1] for l in _video_lessons]))

INTRO = """## 発音コーチ（音素単位の判定）
1. 練習文を選ぶか書き換える → 2.「手本を聞く」→ 3. マイクで録音して停止すると自動で判定します。

English Expressの動画下にある「発音チェック」から、このコーチへ教材の英文を引き継げます。
練習文一覧には、English Express のフレーズ例文と長文の冒頭文も入っています。

判定は wav2vec2 の音素認識モデルで、手本の音素ごとに「その音らしさ」を点数化し、別の音に聞こえた・抜けた・余分な母音が入った箇所を示します。すべてこの PC の中で処理し、音声は外部に送りません。"""

with gr.Blocks(title="発音コーチ") as demo:
    gr.Markdown(INTRO)
    with gr.Accordion("場面練習（15分野・60本の短文）", open=False):
        first = learning.lesson_choices()[0][1]
        l_card0, _, l_ans0, l_cloze0 = learning.lesson_parts(first)
        with gr.Row():
            l_topic = gr.Dropdown(choices=[learning.ALL] + list(learning.TOPICS), value=learning.ALL, label="分野")
            l_pick = gr.Dropdown(choices=learning.lesson_choices(), value=first, label="教材")
        l_card = gr.Markdown(l_card0)
        l_cloze = gr.Textbox(value=l_cloze0, label="穴埋め（聞いたあとに空所を思い出す）", lines=2, interactive=False)
        l_text = gr.Textbox(value=learning.lesson_parts(first)[1], visible=False)
        with gr.Row():
            l_play = gr.Button("音声を聞く")
            l_set = gr.Button("発音練習にセット")
            l_next = gr.Button("次の教材")
        with gr.Accordion("英文・和訳を確認する", open=False):
            l_ans = gr.Markdown(l_ans0)
        with gr.Accordion("研究から考える練習方法", open=False):
            gr.Markdown(learning.METHODS)
    drill = gr.Dropdown(choices=DRILLS, value=DRILLS[0], label="練習文（一覧から選ぶと下の英文が変わる）", allow_custom_value=True)
    sentence = gr.Textbox(value=DRILLS[0], label="読む英文（自由に書き換えられます）", lines=2)
    # One sentence at a time: picking from the list sets the text, and any new text (typed, from a lesson,
    # or handed over from English Express) is shown in the list box too. Runs in the browser, no round trip.
    drill.input(None, drill, sentence, js="(s) => s")
    sentence.change(None, sentence, drill, js="(s) => s")
    with gr.Row():
        b_play = gr.Button("手本を聞く")
        b_slow = gr.Button("ゆっくり聞く")
    r1 = gr.Number(value=1.0, visible=False)
    r2 = gr.Number(value=0.7, visible=False)
    b_play.click(None, [sentence, r1], None, js=SPEAK_JS)
    def _show_lesson(lesson_id):
        card, english, answer, cloze = learning.lesson_parts(lesson_id)
        return card, english, answer, cloze
    l_topic.change(lambda t: gr.update(choices=learning.lesson_choices(t), value=learning.lesson_choices(t)[0][1]), l_topic, l_pick)
    l_pick.change(_show_lesson, l_pick, [l_card, l_text, l_ans, l_cloze])
    l_next.click(learning.next_lesson, [l_topic, l_pick], l_pick)
    l_play.click(None, [l_text, r1], None, js=SPEAK_JS)
    l_set.click(lambda t: (t, t), l_text, [sentence, drill])
    b_slow.click(None, [sentence, r2], None, js=SPEAK_JS)
    audio = gr.Audio(sources=["microphone", "upload"], type="numpy", label="録音（マイクボタン → 読む → 停止）")
    go = gr.Button("もう一度判定する", variant="primary")
    out = gr.HTML()
    with gr.Accordion("Claude に貼って詳しく聞く用のテキスト", open=False):
        summ = gr.Textbox(lines=12, label="コピーして Claude のチャットに貼る", buttons=["copy"])
    with gr.Accordion("これまでの記録", open=False):
        hist = gr.HTML(history_html())
    def _prefill(request: gr.Request):
        try:
            t = (request.query_params.get("text") or "").strip()
        except Exception:
            t = ""
        return t[:300] if t else (gr.skip() if hasattr(gr, "skip") else gr.update())

    demo.load(_prefill, None, [sentence])
    demo.load(None, sentence, drill, js="(s) => s")
    audio.stop_recording(judge, [sentence, audio], [out, summ, hist])
    audio.upload(judge, [sentence, audio], [out, summ, hist])
    go.click(judge, [sentence, audio], [out, summ, hist])

EE_URL = "https://closeai-astra.github.io/English_short_learning/"


def phone_link(share_url: str) -> str:
    """English Express link that saves this coach URL on the phone when opened."""
    from urllib.parse import quote
    base = os.environ.get("EE_URL", EE_URL)
    return base + ("&" if "?" in base else "?") + "coach=" + quote(share_url.rstrip("/"), safe="")


def show_phone_link(share_url: str) -> None:
    """Print the phone link, show it as a QR code in the console and open it as an image."""
    link = phone_link(share_url)
    print("\n[pron-coach] スマホのカメラで下の QR コードを読み取ると、English Express が開き、", flush=True)
    print("[pron-coach] この発音コーチの URL が自動で保存されます（URL の入力は不要）。", flush=True)
    print("[pron-coach] リンク: " + link + "\n", flush=True)
    try:
        import qrcode
    except ImportError:
        print("[pron-coach] （QR コードの表示には qrcode が必要です: uv sync）", flush=True)
        return
    qr = qrcode.QRCode(border=2)
    qr.add_data(link)
    qr.make(fit=True)
    try:
        qr.print_ascii(invert=True)
    except Exception:
        pass
    try:
        img_path = HERE / "phone_link.png"
        qr.make_image(fill_color="black", back_color="white").save(img_path)
        if hasattr(os, "startfile"):
            os.startfile(img_path)  # Windows: opens the QR code in the photo viewer
        print(f"[pron-coach] QR コードの画像: {img_path}", flush=True)
    except Exception as e:
        print(f"[pron-coach] QR 画像を作れませんでした: {e}", flush=True)


def self_check():
    """uv run app.py --check : download the model and verify the phoneme mapping."""
    _, _, model, vocab, blank = load()
    print("vocab size:", len(vocab), "/ blank id:", blank, repr({v: k for k, v in vocab.items()}.get(blank)))
    words = core.expected_phones(DRILLS[0])
    print("expected:", words)
    lost = [(w, p) for w, ps in words for p in ps if not core.to_tokens(p, vocab)]
    print("unmapped phones:", lost or "none")
    print("targets:", " ".join(t.phone for t in core.build_targets(words, vocab)))
    lp = emissions(np.zeros(16000, dtype=np.float32))
    print("emission shape for 1 s:", lp.shape, "(frames, vocab)")
    print("CHECK OK")


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if "--check" in sys.argv:
        self_check()
        raise SystemExit(0)
    threading.Thread(target=_preload, daemon=True).start()
    kw = {}
    auth = None
    for a in sys.argv[1:]:
        if a.startswith("--auth="):
            u, _, pw = a[len("--auth="):].partition(":")
            if u and pw:
                auth = (u, pw)
    if os.environ.get("SPACE_ID"):  # Hugging Face Spaces
        user, pw = os.environ.get("COACH_USER"), os.environ.get("COACH_PASS")
        demo.queue().launch(server_name="0.0.0.0", auth=(user, pw) if user and pw else None)
    elif "--share" in sys.argv:
        if not auth:
            print("[pron-coach] --share では --auth=ユーザー名:パスワード を付けてください（公開URLを他人に使われないため）", flush=True)
            raise SystemExit(1)
        print("[pron-coach] スマホ用の公開URLを作成しています（PC を起動している間だけ有効・最長72時間）", flush=True)
        demo.queue().launch(share=True, auth=auth, inbrowser=True, prevent_thread_lock=True)
        if getattr(demo, "share_url", None):
            show_phone_link(demo.share_url)
        else:
            print("[pron-coach] 公開URLを作れませんでした。ネット接続を確認してください。", flush=True)
        demo.block_thread()
    else:
        demo.queue().launch(inbrowser=True, server_name="127.0.0.1", auth=auth)
