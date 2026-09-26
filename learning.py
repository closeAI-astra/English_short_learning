"""Presentation helpers for the original short lesson library."""
from content import BY_ID, LESSONS, TOPICS

ALL = "すべての分野"


def lesson_choices(topic=ALL):
    return [(f"{x['topic']}｜{x['title']}", x["id"]) for x in LESSONS if topic == ALL or x["topic"] == topic]


def lesson_parts(lesson_id):
    lesson = BY_ID[lesson_id]
    card = (f"### {lesson['title']}\n\n{lesson['topic']} ・ {lesson['level']}\n\n"
            "創作の場面教材です。ニュース・専門知識の解説・実在動画ではありません。\n\n"
            "1. 英文を見ずに音声を聞く。難しければ先に英文を確認する。\n"
            "2. 誰が何をしたか、何をしたいかを思い出して話す。\n"
            "3. 英文・和訳を確認し、自分の状況に置き換えて1文話す。\n\n"
            f"**話すお題：** {lesson['recall_prompt']}")
    answer = (f"**英文**\n\n{lesson['english']}\n\n**和訳**\n\n{lesson['japanese']}\n\n"
              f"**使い回せる表現：** {lesson['phrase']}\n\n"
              "⚠️ 内容を自分の言葉で言えれば十分です。暗唱や発音点数だけで理解度を判断しません。")
    return card, lesson["english"], answer, lesson["cloze"]


def next_lesson(topic, lesson_id):
    ids = [value for _, value in lesson_choices(topic)]
    return ids[(ids.index(lesson_id) + 1) % len(ids)] if lesson_id in ids else ids[0]


METHODS = """
### 研究から考える練習方法

**思い出してから確認する（retrieval practice）**：読んですぐ終えず、英文を隠して意味や表現を取り出す。
外国語の語彙を使った実験に裏付けがありますが、自由会話全体の上達を保証するものではありません。
[Karpicke & Roediger, 2008](https://doi.org/10.1126/science.1152408)

**日を空けて戻る（spaced practice）**：今日できた教材を後日もう一度。
第二言語学習のメタ分析に裏付けがあります。まず翌日・数日後・翌週を目安にし、難しければ短く調整します。
この日程自体が最適と証明されているわけではありません。この版には自動の復習通知・予約機能はありません。
[Kim & Webb, 2022](https://doi.org/10.1111/lang.12479)

**同じ話を繰り返す（4/3/2）**：知っている題材について4分、3分、2分と同じ内容を話す練習。
小規模な教室実験では、同じ話を反復した群で事後テストの流暢さの改善が維持されました。
短い教材ではまず30秒の言い換えで構いませんが、それは研究と同じ課題ではありません。
[de Jong & Perfetti, 2011](https://doi.org/10.1111/j.1467-9922.2010.00620.x)

**複数話者の聞き分け（HVPT）**：複数の人の声・いろいろな単語で /r/ と /l/ などを聞き分け、正誤を確認する。
日本語話者を対象とした研究があります。このアプリの合成音声だけでは、その研究条件は再現できません。
[Bradlow et al., 1999](https://pmc.ncbi.nlm.nih.gov/articles/PMC3472521/)

**学習の偏りを防ぐ（Four Strands）**：理解する入力、意味を伝える出力、語彙・発音等の学習、既知の内容を滑らかに使う練習を組み合わせる設計原則。
全員に最適な時間配分を証明した法則ではありません。
[Nation, 2007](https://www.wgtn.ac.nz/lals/resources/paul-nations-resources/paul-nations-publications/publications/documents/2007-Four-strands.pdf)

⚠️ 研究上の効果は対象者・課題・期間に依存します。このアプリ自体の学習効果は未検証です。
「海外で有名・日本で無名」という普及度の比較は確認できていません。
"""
