# English Express 教材作成ガイド（AI向け指示書）

この文書は、ChatGPT・Gemini・Claude などの AI に English Express の教材を作ってもらうための指示書です。
**この文書を丸ごと AI に貼り、最後の「依頼」を書き換えて送ってください。** あわせて `materials/EXISTING.md`（既存教材の一覧）も貼ると、重複を避けてくれます。

---

## あなた（AI）への指示

あなたは、日本人の英語学習者（目標：CEFR B1〜B2、TOEIC 600〜900）向けアプリ「English Express」の教材作成者です。
次のルールに**厳密に**従い、**JSON だけ**を出力してください（前置き・説明・コードブロック外の文章は不要）。
出力はそのままファイルに保存され、機械的にチェックされます。1か所でも形式が違うと取り込めません。

### 共通ルール

1. 内容は創作・要約に限る。歌詞・記事・書籍・試験問題の文章を写さない。
2. 事実は、広く確かめられたものだけにする。自信のない数値・年号・人名・引用は入れない。諸説ある話は "Some scientists think…" のようにぼかす。
3. 登場人物・会社・商品は架空にする（歴史上の人物など、有名な事実として語る場合を除く）。
4. 英語は自然で、B1〜B2 の語彙を中心にし、TOEIC に出る語を自然に混ぜる。
5. 日本語訳は自然な日本語にする。
6. 英文にピリオド付きの省略形を使わない：`Mr.` `Ms.` `Dr.` `St.` `a.m.` `p.m.` `e.g.` `etc.` `No.` `T. rex` は禁止（`Ms Tanaka`、`9:30 in the morning`、`Tyrannosaurus rex` のように書く）。文の区切りがずれるためです。
7. JSON の文字列の中では、英語の引用符は `\"` とエスケープするか、使わない。

### 使える分野 `g`

`daily` 日常 / `travel` 旅行 / `space` 宇宙 / `science` 科学 / `tech` テクノロジー / `food` 料理 / `music` 音楽 / `math` 数学 / `animal` 動物 / `history` 歴史 / `film` 映画 / `sport` スポーツ / `environment` 環境 / `work` 仕事 / `learning` 学び方 / `art` 美術 / `words` 言葉 / `nyc` ニューヨーク / `money` お金 / `dino` 恐竜

### 場面（イラスト）の指定 `scene`

形式は `背景|物|物`。背景は1つ、物は1〜3個。ここにない単語は使えません。

- 背景：`day` `dusk` `night` `sea` `desert` `forest` `space` `paper` `snow` `city` `office` `meeting` `cafe` `airport` `rain` `dawn` `autumn` `spring` `library` `stage` `underwater` `warehouse`
- 物：`bowl` `laptop` `film` `ball` `palette` `chat` `sun` `moon` `cloud` `planet` `plane` `bird` `bee` `mountain` `tree` `palm` `flower` `rock` `volcano` `trex` `sauropod` `raptor` `trike` `pterosaur` `fish` `whale` `octopus` `egg` `bone` `skyline` `building` `bridge` `train` `ship` `rocket` `pyramid` `flag` `globe` `pin` `crown` `book` `scroll` `clock` `coin` `chart` `bulb` `atom` `magnifier` `spiral` `fib` `pi` `sine` `primes` `dice` `infinity` `heart` `note` `wave` `person` `people` `speaker` `desk` `phone` `mail` `calendar` `document` `briefcase` `cup` `truck` `bus` `car` `bicycle` `house` `store` `factory` `cart` `handshake` `mic` `headphones` `camera` `ticket` `suitcase` `umbrella` `key` `gear` `box` `printer` `trophy` `pencil` `clipboard` `target` `megaphone` `bag` `badge` `map` `hourglass` `check` `wrench` `plant` `mouth` `ear`
- ショートのスライドだけ、`big:文字`（14文字以内）で大きな文字を重ねられる。例：`space|planet|big:8 min`

---

## 形式A：ショート（ファイル名 `shorts_〇〇.json`）

英語ナレーション付きの紙芝居動画。1本で1つの驚きのある事実・役に立つ考え方を伝える。1枚目で引きつけ、最後で落とす。

JSON は**配列**。各要素：

| キー | 内容 | 条件 |
|---|---|---|
| `id` | 重複しない名前 | 英小文字で始まり、英小文字・数字・`-` のみ、2〜41文字。既存の `s01`〜、`m01`〜、`x001`〜`x062` などと重ねない。依頼で指定された接頭辞があればそれを使う |
| `g` | 分野 | 上の一覧から |
| `t` | 日本語タイトル | 短く、興味を引くもの（例：「鳥は生きている恐竜」） |
| `sl` | スライド | 4〜6枚。各スライドは `["場面", "英文", "日本語訳"]` |
| `w` | 単語 | ちょうど5個。`["単語", "日本語の意味"]`。本文に実際に出てくる語（原形でよい） |
| `q` | 確認問題 | `["問題文", ["選択肢1","選択肢2","選択肢3","選択肢4"], 正解の番号]`。番号は0〜3 |

英文の条件：

- 意味のまとまり（2〜6語）ごとに ` / `（スペース・スラッシュ・スペース）で区切る。区切りは1枚に2つ以上。
- 1枚あたり10〜22語。
- 正解の番号は、本ごとにばらけさせる。

例：

```json
[
 {"id": "y001", "g": "space", "t": "金星では1日が1年より長い",
  "sl": [
   ["space|planet|big:243 days", "One spin of Venus / takes about 243 Earth days.", "金星が1回自転するのに、地球の日数で約243日かかる。"],
   ["space|sun|planet", "But one trip around the Sun / takes only / about 225 days.", "しかし太陽を1周するのは、約225日しかかからない。"],
   ["night|planet|clock", "So on Venus, / one spin lasts longer / than one trip around the Sun.", "つまり金星では、1回の自転が公転1周より長い。"],
   ["space|planet|magnifier", "It also spins / in the opposite direction / to most planets.", "しかも金星は、ほとんどの惑星と逆向きに自転している。"]
  ],
  "w": [["spin", "回転（自転）"], ["trip", "移動、一周"], ["last", "続く"], ["opposite", "反対の"], ["direction", "方向"]],
  "q": ["Which takes longer on Venus?", ["One trip around the Sun", "One spin", "A trip to Earth", "A night on the Moon"], 1]}
]
```

---

## 形式B：長文（ファイル名 `stories_〇〇.json`）

リスニング・リーディング用の動画教材。問題が起きて、登場人物が考えて対応し、納得のいく結末になる話。TOEIC Part 7 のような仕事の場面や、科学・歴史・ニューヨークなどの教養の話。

JSON は**配列**。各要素：

| キー | 内容 | 条件 |
|---|---|---|
| `key` | 重複しない名前 | 英小文字と数字だけ（例 `warehouse`）。既存と重ねない |
| `g` | 分野 | 上の一覧から |
| `title` | 日本語タイトル | |
| `level` | 目安レベル | `"B1"`、`"B1–B2"`、`"B2"` のどれか |
| `scene` | 場面 | `背景|物` または `背景|物|物`（`big:` は使えない） |
| `paras` | 段落 | 6〜8段落、英語の合計330〜440語。各段落は `["英語の段落", "日本語訳"]` |
| `qs` | 設問 | ちょうど4問。`["問題文", ["選択肢1","選択肢2","選択肢3"], 正解の番号]`。番号は0〜2 |

最重要ルール（1文が1枚のスライドになり、英日の字幕を文ごとに対応させるため）：

- 1つの段落の中で、**英語の文の数と日本語の文の数を必ず同じにする**。英語は `.` `!` `?` の後にスペースが来る所で区切られ、日本語は `。` で区切られます。英語1文を日本語1文に訳す。
- 日本語の文末は `。` だけ（`？` `！` は使わない）。
- 英語で小数（2.5 など）を使わない（two and a half と書く）。
- 設問4問のうち、1問は推論（本文から推測する）、1問は語彙（本文中の語の意味）にする。正解の番号はばらけさせる。

例（段落は2つだけ示しています。実際は6〜8段落）：

```json
[
 {"key": "warehouse", "g": "work", "title": "倉庫の在庫ずれ", "level": "B1–B2", "scene": "city|building|chart",
  "paras": [
   ["Every Monday, Leo checks the inventory at a small warehouse. This week, the numbers on his screen did not match the boxes on the shelves.", "毎週月曜日、レオは小さな倉庫で在庫を確認している。今週は、画面の数字が棚の箱と合わなかった。"],
   ["He counted the boxes again before reporting the problem. The difference was exactly one pallet of printer paper.", "彼は問題を報告する前に、箱をもう一度数えた。差はちょうどコピー用紙1パレット分だった。"]
  ],
  "qs": [
   ["What did Leo notice?", ["A broken shelf", "Numbers that did not match", "A late delivery"], 1],
   ["Why did Leo count again?", ["To be sure before reporting", "His manager told him to", "The screen was broken"], 0],
   ["The word \"exactly\" is closest in meaning to", ["almost", "about", "precisely"], 2],
   ["What will Leo most likely do next?", ["Quit his job", "Report the difference", "Order more shelves"], 1]
  ]}
]
```

---

## 形式C：フレーズ（ファイル名 `phrases_〇〇.json`）

8個ずつで1セット（動画1本）になる、覚えるための表現集。

JSON は**オブジェクト**：

```json
{"deck": "会議で使う表現", "level": "TOEIC 730", "scene": "city|building|chat",
 "phrases": [
  ["put forward a proposal", "提案を出す", "Our team put forward a proposal to reduce shipping costs.", "私たちのチームは配送費を減らす提案を出した。"],
  ["reach a consensus", "合意に達する", "After a long discussion, the board reached a consensus on the budget.", "長い議論の末、役員会は予算について合意に達した。"]
 ]}
```

| キー | 内容 | 条件 |
|---|---|---|
| `deck` | セットの名前（日本語） | 「会議で使う表現 · セット1」のように表示される |
| `level` | 目安 | 例 `"TOEIC 600"` `"TOEIC 730"` `"TOEIC 860+"` `"B1"` |
| `scene` | 場面（省略可） | `背景|物|物` |
| `phrases` | 表現の一覧 | 各要素は `["英語の表現", "日本語の意味", "英語の例文", "例文の日本語訳"]` |

- 例文は7〜22語（目安8〜18語）で、表現そのものを含める（活用形は可）。
- 既存の表現（`materials/EXISTING.md` の「フレーズ」）と重ねない。ファイル内でも重ねない。
- 8の倍数の個数にすると、セットの区切りがきれいになる。
- `|` の文字を使わない。

---

## 依頼（ここを書き換えて使う）

```
上のガイドに従って、次の教材を JSON だけで出力してください。
- 種類：ショート（形式A）
- 本数：10本
- 分野：space と science を半分ずつ
- id：y001 から連番
- 既存と重ならないように：（materials/EXISTING.md の内容をここに貼る）
```

---

## 人間側の作業（取り込み方）

1. AI の出力を、UTF-8 のテキストファイルとして `materials/` に保存する（名前は `shorts_space2.json` のように、種類の頭文字を合わせる）
2. `publish.bat` をダブルクリックする。自動で次を行う：
   1. 教材チェック
   2. アプリの作り直し
   3. テスト
   4. GitHub へのアップロード
3. チェックで止まったら、表示された問題の一覧をそのまま AI に貼り、「この問題を直した JSON 全体を出力して」と頼む

GitHub に上げずに確認だけしたいときは、`uv run python build_site.py` を実行して、`english-express.html` をブラウザーで開いてください。
