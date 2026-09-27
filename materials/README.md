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

語彙カバー率（NGSL 1.2 + TSL 1.2 のうち教材に出てくる語の割合）は、ビルド後に `node coverage.cjs` で確認できます。`--missing-tsl` を付けると、まだ出てこない TOEIC 語の一覧が出るので、新しい教材の題材選びに使えます。`publish.bat` は、アプリ内のカバー率と TSL のカバー率が50％以下になるとアップロードを止めます。

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
  - 室内・天気など（追加）：office, meeting, cafe, airport, rain, dawn, autumn, spring, library, stage, underwater, warehouse
- 物：bowl, laptop, film, ball, palette, chat, sun, moon, cloud, planet, plane, bird, bee, mountain, tree, palm, flower, rock, volcano, trex, sauropod, raptor, trike, pterosaur, fish, whale, octopus, egg, bone, skyline, building, bridge, train, ship, rocket, pyramid, flag, globe, pin, crown, book, scroll, clock, coin, chart, bulb, atom, magnifier, spiral, fib, pi, sine, primes, dice, infinity, heart, note, wave
  - 仕事・生活（追加）：person, people, speaker, desk, phone, mail, calendar, document, briefcase, cup, truck, bus, car, bicycle, house, store, factory, cart, handshake, mic, headphones, camera, ticket, suitcase, umbrella, key, gear, box, printer, trophy, pencil, clipboard, target, megaphone, bag, badge, map, hourglass, check, wrench, plant, mouth, ear
- 長文とフレーズのスライドは、英文の単語（meeting, invoice, flight など）から絵柄を自動で選びます。場面の指定は「1枚目・該当語がないとき」の絵柄になります

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

## 600点台→850 拡張教材

追加内容・学習順・根拠・限界は `../CONTENT_EXPANSION_850.md` を参照。ショートの任意項目 `explanation` は元の確認問題への日本語解説、長文の `explanations` は `qs` と同順・同数の解説です。解答後に表示されます。既存データは変更不要です。

この拡張分の編集元は `_native.txt`、`_curiosity.txt`、`_bridge850.txt`、`_bridge_readings.txt`。編集後は `python materials/_build_expansion.py` で対応JSONを再生成し、通常の検証・ビルドを実行してください。生成済みJSONだけを直すと再生成時に上書きされます。英文の既存区切りを保ちつつ長い塊を節・前置詞の境界付近で補分割しています。学習順と参照先は `../curriculum.py` で管理し、不明な教材IDがあればビルドは停止します。


動画の場面イラストは `../scene_content.py` で追加110本の各4場面を指定します。図形・背景を増やす場合は `../art-topic.js` にSVGを追加し、このフォルダーの `validate.py` の利用可能名にも追加します。再生成・ビルド後に `node test_art.cjs` を実行してください。長文・フレーズの自動選択は `../video-app.js` の字幕キーワードで管理しています。
