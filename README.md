---
title: Pron Coach
sdk: gradio
app_file: app.py
pinned: false
---

# 発音コーチ（音素単位・無料・ローカル実行）

英文を読み上げた録音を、音素（/l/ /ɹ/ /θ/ など）ごとに採点します。

- 別の音に聞こえた箇所（例 /l/ → /ɹ/）、抜けた音、子音のあとの余分な母音を検出します。
- 検出した問題に合わせて、舌と唇の直し方を日本語で表示します。
- ローカル起動時の判定は PC の中で行い、音声は外部に送りません。共有URL（`--share`）や Hugging Face Spaces では、実行しているサーバーに録音を送ります。

## 導入（Windows、uv 使用）

1. このフォルダを好きな場所に展開する（例 `C:\Users\you\pron-coach`）
2. PowerShell でそのフォルダに移動して、動作確認をする

       uv run app.py --check

   初回は PyTorch などのインストールと、モデル（約1.2GB）のダウンロードで数分かかります。
   最後に `CHECK OK` と出れば準備完了です。

3. 起動する

       uv run app.py

   ブラウザで http://127.0.0.1:7860 が開きます。止めるときは PowerShell で Ctrl + C。

## 使い方

1. 練習文を選ぶ（自由に書き換えも可）
2. 「手本を聞く」で音声を確認する
3. マイクボタン → 読む → 停止。自動で判定されます
4. 「Claude に貼って詳しく聞く用のテキスト」をコピーして Claude に貼ると、詳しいコーチングが受けられます

判定の記録は、このフォルダの `results.csv` に保存されます。

## 仕組み

1. 英文を espeak-ng で音素列に変換する
2. 録音を wav2vec2 の音素認識モデル（facebook/wav2vec2-lv-60-espeak-cv-ft）に通し、約20ミリ秒ごとに各音素の確率を出す
3. 手本の音素列を CTC 強制アライメントで時間に割り当てる
4. 各音素の点数を計算する。点数は「手本の音素の確率 ÷ 一番確率の高い音素の確率」の平均（GOP）で、ずれた音素は代わりに何の音に聞こえたかも出す
5. 自由認識した音素列を手本と編集距離で対応付け、置換・脱落・挿入を判定する

注意：点数は「このモデルが学習した話者にどれだけ近いか」を表します。訛りがあっても通じる発音が減点されることもあるので、目安として使ってください。

## スマホで使う

### A. PC を起動している間だけ（手軽）

    uv run app.py --share --auth=自分で決めた名前:パスワード

`https://xxxx.gradio.live` の URL が出るので、スマホで開いて名前とパスワードでログインします（URL は72時間有効、PC で動かしている間だけ使えます）。

### B. いつでも（PC 不要・無料）

Hugging Face の無料アカウントで Space（SDK: Gradio, ハードウェア: CPU basic）を作り、このフォルダの `app.py` `core.py` `requirements.txt` `README.md` をアップロードします。Space の Settings → Variables and secrets に `COACH_USER` と `COACH_PASS` を登録するとパスワード付きになります。初回起動はモデルのダウンロードで数分かかります。

English Express の「記録 → 設定 → 発音コーチの URL」に上の URL を入れると、ショートやフィードの「音素分析」ボタンから文が自動で入った状態で開きます。

## 場面練習（60本の短文）

画面上部の「場面練習」で、15分野・60本のオリジナル短文を使えます（実在動画ではなく創作の場面教材）。
英文を隠して聞き、内容を思い出してから英文・和訳を確認し、自分の状況で話す練習に使います。「発音練習にセット」で下の録音欄に英文が入ります。
練習文一覧には、English Express のフレーズ例文と長文の冒頭文も入っています。

## English Express（同じフォルダ）

- 本体：`english-express.html`（ブラウザーで開く）／GitHub Pages 用：`docs/index.html`
- 公開方法：`GITHUB_PAGES_README.md`
- 教材の追加：`materials/README.md`（ほかの AI に作ってもらうときは `AI_CONTENT_GUIDE.md`）
- まとめて更新・アップロード：`publish.bat` をダブルクリック
- 検証：`node test_video.cjs`、`node test_study.cjs`

**Spacesにアップロードする場合は、`app.py` `core.py` `requirements.txt` `README.md` に加えて `content.py` `learning.py` `video_content.py` `extra_video_content.py` と `materials/` フォルダーも必要です。**
