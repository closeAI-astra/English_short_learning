# 教材の追加方法

English Express の教材は、このフォルダーに JSON ファイルを置くだけで追加できます。アプリ本体のコードを触る必要はありません。

## 手順

1. `_templates/` にある見本をこのフォルダーにコピーして、名前を変える
   - フレーズ → `phrases_〇〇.json`
   - ショート動画 → `shorts_〇〇.json`
   - 長文（リスニング・リーディング動画）→ `stories_〇〇.json`
   - 名前の頭が `phrases_` `shorts_` `stories_` なら自動で読み込まれます。頭が `_` のファイルは読み込まれません。
2. 中身を書き換える（書き方は下の表）
3. pron-coach フォルダーの `publish.bat` をダブルクリックする
   - 教材チェック → アプリの作り直し → テスト → GitHub へのアップロードまで自動で行います
   - 問題があれば、ファイル名と場所が表示されて止まります。直してからもう一度実行してください
   - GitHub に上げずに手元で確認したいだけなら、代わりに `uv run python build_site.py` を実行し、`english-express.html` をブラウザーで開きます
4. 更新されるファイル
   - `english-express.html`（手元で開く本体）
   - `docs/index.html`（GitHub Pages 用）
   - `english-express-github-pages.zip`（公開用一式）
   - `materials/EXISTING.md`（既存教材の一覧。重複を避けるために使う）

チェックだけしたいときは `uv run python materials/validate.py` を実行します。

## 書き方

### フレーズ `phrases_〇〇.json`

    {"deck": "会議で使う表現", "level": "TOEIC 730", "scene": "city|building|chat",
     "phrases": [["英語の表現", "日本語の意味", "英語の例文", "例文の日本語訳"], ...]}

- 8個ずつで1セット（動画1本）になり、セット名は「会議で使う表現 · セット1」のようになります
- 例文は7〜22語で、表現そのものを含める
- すでにアプリにある表現と重複するとエラーになります

### ショート `shorts_〇〇.json`

| 項目 | 内容 |
|---|---|
| `id` | 英小文字で始まる重複しない名前（例 `y001`）。既存は `s01`〜、`x001`〜`x062` |
| `g` | 分野。daily, travel, space, science, tech, food, music, math, animal, history, film, sport, environment, work, learning, art, words, nyc, money, dino |
| `t` | 日本語のタイトル |
| `sl` | 4〜6枚のスライド。`["場面", "英語（意味の塊を / で区切る）", "日本語訳"]` |
| `w` | 単語5個。`["単語", "意味"]`。本文に出てくる語にする |
| `q` | 確認問題。`["問題文", [選択肢4つ], 正解の番号(0から)]` |

### 長文 `stories_〇〇.json`

| 項目 | 内容 |
|---|---|
| `key` | 英小文字と数字だけの重複しない名前 |
| `g` `title` `level` | 分野・日本語タイトル・目安レベル（例 `B1–B2`） |
| `scene` | `背景|物|物` |
| `paras` | 6〜8段落、合計330〜440語。`["英語の段落", "日本語訳"]` |
| `qs` | 4問。`["問題文", [選択肢3つ], 正解の番号]` |

- 1段落の中の英語の文の数（. ! ? で区切る）と日本語の文の数（。で区切る）を必ず揃える。1文が1枚のスライドになり、字幕が対応します
- 英語に `Mr.` `Dr.` `a.m.` のようなピリオド付きの省略形を使わない（文の区切りがずれる）。日本語の文末は「。」だけにする

### 場面（イラスト）の書き方

`背景|物|物`（物は3つまで）。ショートでは `big:短い文字`（14文字まで）で大きな文字も出せます。

- 背景：day, dusk, night, sea, desert, forest, space, paper, snow, city
- 物：bowl, laptop, film, ball, palette, chat, sun, moon, cloud, planet, plane, bird, bee, mountain, tree, palm, flower, rock, volcano, trex, sauropod, raptor, trike, pterosaur, fish, whale, octopus, egg, bone, skyline, building, bridge, train, ship, rocket, pyramid, flag, globe, pin, crown, book, scroll, clock, coin, chart, bulb, atom, magnifier, spiral, fib, pi, sine, primes, dice, infinity, heart, note, wave

## AI に作ってもらうとき

ChatGPT・Gemini・Claude など、どの AI でも使えます。

1. pron-coach フォルダーの `AI_CONTENT_GUIDE.md` を丸ごと AI に貼る
2. `materials/EXISTING.md` も貼る（重複を避けるため）
3. ガイド末尾の「依頼」を書き換えて送る
4. 出てきた JSON を `materials/` に保存して、`publish.bat` を実行する

チェックで止まったら、表示された問題をそのまま AI に貼って直してもらいます。

## 注意

- 教材はすべて創作・要約です。歌詞・記事・教材の文章をそのまま貼らないでください（GitHub で公開する場合は特に）。
- 公開済みのフレーズの英語を後から書き換えると、そのフレーズは新しいカードとして扱われ、復習履歴が引き継がれません。
