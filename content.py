"""Original micro-lessons, also exported as JSON for English Express.

All scenes are fictional language practice, not news or factual subject lessons.
Levels are editorial estimates, not certified CEFR assessments.
"""
import json
from pathlib import Path

# title | English | Japanese | reusable expression
SEEDS = {
    "宇宙・天文": """
星を見る夜|We planned to watch the stars tonight. Clouds covered the sky, so we checked the weather again. We decided to try tomorrow.|今夜は星を見る予定でした。空が雲に覆われたので、もう一度天気を確認しました。明日また試すことにしました。|decided to
望遠鏡の準備|Please put the telescope near the window. I cannot see anything yet. Could you help me adjust it?|望遠鏡を窓の近くに置いてください。まだ何も見えません。調整を手伝ってもらえますか。|Could you help me
宇宙の展示|The museum has a new space exhibition. I want to learn how people live on a space station. Let's visit it this weekend.|博物館で新しい宇宙展をやっています。宇宙ステーションでの暮らしを知りたいです。今週末に行きましょう。|I want to learn
観測ノート|I drew what I saw through the telescope. My friend took a picture instead. We compared our records after dinner.|望遠鏡で見たものを描きました。友人は代わりに写真を撮りました。夕食後に記録を比べました。|instead
""",
    "自然・動物": """
公園の鳥|I heard a bird near the pond. I stayed quiet and waited for it to appear. Next time, I will bring my notebook.|池の近くで鳥の声を聞きました。静かにして姿を現すのを待ちました。次回はノートを持ってきます。|waited for
動物の保護施設|We visited an animal shelter on Saturday. A volunteer explained the daily routine. I asked how I could help.|土曜日に動物の保護施設を訪ねました。ボランティアが毎日の仕事を説明してくれました。どう手伝えるか尋ねました。|how I could help
森の散歩|The path was wet after the rain. We walked slowly and stayed on the marked trail. We took our rubbish home.|雨の後で道がぬれていました。ゆっくり歩き、印のある道を進みました。ごみは持ち帰りました。|after the rain
猫との暮らし|My cat hid under the sofa when the doorbell rang. I gave her some space. Later, she came out on her own.|呼び鈴が鳴ると猫がソファの下に隠れました。そっとしておきました。後で自分から出てきました。|on her own
""",
    "料理・食文化": """
スープ作り|I'm making soup for dinner. Could you cut the carrots while I wash the beans? We can taste it before adding more salt.|夕食にスープを作っています。私が豆を洗う間にニンジンを切ってもらえますか。塩を足す前に味見しましょう。|before adding
注文の相談|I'd like the vegetable sandwich, please. Does it contain any nuts? Please check with the kitchen before I order.|野菜サンドイッチをお願いします。ナッツは入っていますか。注文する前に厨房に確認してください。|Does it contain
市場で買い物|These tomatoes look good. How much are they per kilo? I'll take a small bag because I'm cooking for one.|このトマトはおいしそうです。1キロいくらですか。一人分を作るので小さな袋を一つ買います。|How much are they
レシピの失敗|My bread did not rise this morning. I read the recipe again and checked each step. Next time, I will write down what I change.|今朝はパンが膨らみませんでした。レシピを読み直して各手順を確認しました。次回は変えた点を書き留めます。|write down
""",
    "旅行・交通": """
乗り換え|Excuse me, does this train stop at Central Station? I need to change trains there. Please let me know when we arrive.|すみません、この電車はセントラル駅に止まりますか。そこで乗り換える必要があります。着いたら教えてください。|change trains
ホテルの到着|I have a reservation under the name Tanaka. Is it possible to leave my bag here before check-in? I'll come back this afternoon.|田中という名前で予約しています。チェックイン前に荷物を預けられますか。午後に戻ります。|Is it possible to
道に迷った|I think we took the wrong turn. Let's stop and look at the map. The library should be near the next bridge.|曲がるところを間違えたと思います。止まって地図を見ましょう。図書館は次の橋の近くのはずです。|look at
旅の予定変更|Our flight was delayed, so we changed our plans. We called the hotel and explained the situation. They said we could arrive later.|飛行機が遅れたので予定を変更しました。ホテルに電話して事情を説明しました。遅く到着してもよいと言われました。|explained the situation
""",
    "テクノロジー・AI": """
回答を確かめる|The chatbot gave me a surprising answer. I checked the original source before using it. One detail needed a correction.|チャットボットの回答は意外でした。使う前に元の資料を確認しました。一か所修正が必要でした。|original source
アプリの改善|This button is difficult to find. Could we move it closer to the search box? Let's ask a new user to try it.|このボタンは見つけにくいです。検索欄の近くに移せますか。初めての利用者に試してもらいましょう。|closer to
データのバックアップ|I saved a copy of my project on another drive. Then I opened the copy to check it. I wanted to make sure it worked.|別のドライブにプロジェクトのコピーを保存しました。その後、コピーを開いて確認しました。動くことを確かめたかったのです。|make sure
通知を減らす|My phone kept interrupting me while I studied. I turned off a few notifications. Now I check messages during my breaks.|勉強中に携帯が何度も邪魔をしました。いくつか通知を切りました。今は休憩中にメッセージを確認しています。|turned off
""",
    "数学・問題解決": """
小さな例から|The problem looked complicated at first. I tried a small example and drew a diagram. That helped me decide what to do next.|最初は複雑な問題に見えました。小さな例を試して図を描きました。それで次に何をするか決めやすくなりました。|at first
証明を説明する|I understand the example, but I cannot explain the proof yet. Could we go through it one step at a time? I want to know where we use this assumption.|例は分かりますが、まだ証明を説明できません。一段階ずつ確認できますか。この仮定をどこで使うか知りたいです。|one step at a time
答えの確認|We got different answers to the same question. Let's compare our calculations from the beginning. I may have missed a minus sign.|同じ問いに違う答えが出ました。初めから計算を比べましょう。マイナス記号を見落としたかもしれません。|may have missed
反例を探す|This claim seems true in the examples we tried. But that does not prove it in every case. Let's look for a counterexample.|試した例ではこの主張は正しそうです。でも、すべての場合の証明にはなりません。反例を探しましょう。|look for
""",
    "音楽・音声": """
ライブの感想|The concert was louder than I expected. My favorite part was the quiet song near the end. What did you think of it?|コンサートは予想より大きな音でした。一番好きだったのは終盤の静かな曲です。どう思いましたか。|than I expected
楽器の練習|I keep making a mistake in this part. I'll play it slowly before trying the whole song. Could you listen and give me feedback?|この部分で何度も間違えます。曲全体に挑む前にゆっくり弾きます。聞いて意見をもらえますか。|give me feedback
プレイリスト|I'm making a playlist for our trip. Do you prefer calm music or something lively? We can take turns choosing songs.|旅行用のプレイリストを作っています。静かな曲と元気な曲のどちらが好きですか。交代で選びましょう。|take turns
録音の確認|There is a strange noise in this recording. Let's listen to the first few seconds again. It might be coming from the fan.|この録音には変な音があります。最初の数秒をもう一度聞きましょう。扇風機からかもしれません。|might be coming from
""",
    "映画・物語": """
ネタバレなしで|Have you seen this film yet? I want to talk about the ending, but I won't spoil it. Tell me when you finish watching it.|この映画はもう見ましたか。結末について話したいけれど、ネタバレはしません。見終わったら教えてください。|Have you seen
登場人物の選択|The main character refused the offer. I thought she would accept it. What would you do in her situation?|主人公は申し出を断りました。受けると思っていました。彼女の立場ならどうしますか。|in her situation
字幕で確認|I missed a line in the scene. I watched it again with English subtitles. Then I tried saying it without looking at the screen.|その場面のせりふを聞き逃しました。英語字幕でもう一度見ました。その後、画面を見ずに言ってみました。|without looking
短い物語を書く|Our story begins in an empty station. Someone finds a letter on a bench. We still need to decide who wrote it.|私たちの物語は誰もいない駅で始まります。誰かがベンチで手紙を見つけます。誰が書いたかはこれから決めます。|need to decide
""",
    "スポーツ・運動": """
試合の振り返り|We lost the match, but our passing improved. Let's watch the recording together. We can choose one thing to work on next time.|試合には負けましたがパスは良くなりました。一緒に録画を見ましょう。次に取り組むことを一つ選べます。|work on
初めてのクラス|This is my first dance class. Could you show me that movement again? I'll try it slowly until I understand the steps.|初めてのダンス教室です。その動きをもう一度見せてもらえますか。手順が分かるまでゆっくり試します。|show me
観戦の約束|Are you free to watch the game tonight? I can bring some snacks. Let's meet outside the station before it gets busy.|今夜、試合を見る時間はありますか。軽食を持っていけます。混む前に駅の外で会いましょう。|Are you free to
無理をしない|My knee feels uncomfortable today. I'm going to stop this exercise and tell the instructor. I don't want to push through the pain.|今日は膝に違和感があります。この運動をやめて指導者に伝えます。痛みを我慢して続けたくありません。|I'm going to
""",
    "歴史・博物館": """
展示の質問|This old map caught my attention. Do we know who made it? I'd like to read more about the person behind it.|この古い地図に目を引かれました。誰が作ったか分かっていますか。作った人についてもっと読みたいです。|caught my attention
資料を比べる|These two letters describe the same event differently. Let's check who wrote them and when. We should not assume that either account is complete.|二通の手紙は同じ出来事を違うように述べています。誰がいつ書いたか確認しましょう。どちらも完全な記録とは決めつけられません。|the same event
音声ガイド|Does the ticket include an audio guide? I'd like to hear the English version. Can I pause it and listen to a section again?|チケットに音声ガイドは含まれますか。英語版を聞きたいです。止めて一部分を聞き直せますか。|Does the ticket include
古い写真|My grandmother showed me a photograph of her old school. I asked her what a normal day was like. She told me a story I had never heard.|祖母が昔の学校の写真を見せてくれました。普段の一日はどうだったか尋ねました。初めて聞く話をしてくれました。|what a normal day was like
""",
    "環境・街づくり": """
容器を持参|I brought my own cup to the cafe. Could you put my drink in this, please? If that is not allowed, I can have it here.|カフェに自分のカップを持ってきました。これに飲み物を入れてもらえますか。できなければ店内で飲みます。|If that is not allowed
公園の提案|Our neighborhood needs more places to sit. I suggested adding benches near the trees. We will discuss the idea at the next meeting.|近所には座る場所がもっと必要です。木の近くにベンチを置こうと提案しました。次の会議で話し合います。|suggested adding
ごみの分別|I'm not sure which bin this goes in. Let's check the local instructions. The rules may be different from those in my hometown.|これをどのごみ箱に入れるか分かりません。地域の案内を確認しましょう。故郷とはルールが違うかもしれません。|different from
自転車の道|I would cycle to work if the route felt safer. There is a busy crossing near my office. Could the city improve it?|道がもっと安全に感じられれば自転車通勤をするのですが。職場の近くに交通量の多い交差点があります。市は改善できるでしょうか。|if the route felt safer
""",
    "仕事・コミュニケーション": """
締め切りの相談|I can finish the draft by Friday. However, I need more time to check the figures. Would Monday work for the final version?|金曜までに草稿は仕上げられます。ただ、数字の確認にもっと時間が必要です。完成版は月曜でもよいですか。|Would Monday work
聞き返す|Sorry, I didn't catch the last part. Could you say it again a little more slowly? I want to make sure I understood the request.|すみません、最後を聞き取れませんでした。もう少しゆっくり繰り返してもらえますか。依頼を理解できたか確認したいです。|I didn't catch
意見の違い|I see your point, but I have a different concern. This plan may take longer than we expect. Could we test a smaller version first?|言いたいことは分かりますが、別の懸念があります。この計画は予想より時間がかかるかもしれません。先に小規模版を試せますか。|I see your point
助けを頼む|I'm having trouble with this task. I've tried two approaches, but neither worked. Could we spend a few minutes looking at it together?|この作業に困っています。二つの方法を試しましたが、どちらもうまくいきませんでした。少し一緒に見てもらえますか。|I'm having trouble with
""",
    "心理・学び方": """
覚えたつもり|The answer looked familiar when I read it. But I couldn't recall it with the book closed. I'll try answering before checking next time.|読んだときは知っている答えに見えました。でも本を閉じると思い出せませんでした。次回は確認前に答えてみます。|before checking
目標を小さく|I planned to study all evening, but I felt overwhelmed. Today, I'll start with one short lesson. After that, I can decide whether to continue.|一晩中勉強する予定でしたが、圧倒されてしまいました。今日は短い一課から始めます。その後、続けるか決めます。|start with
説明してみる|Could I explain this idea to you? Please stop me if anything is unclear. Your questions might show me what I need to review.|この考えを説明してもいいですか。不明なところがあれば止めてください。質問で復習が必要な点が分かるかもしれません。|what I need to review
振り返り|I wrote down what was difficult after the lesson. Tomorrow, I'll try those questions again without my notes. Then I'll compare my answers.|授業後に難しかった点を書き留めました。明日はノートを見ずにその問いを解き直します。それから答えを比べます。|without my notes
""",
    "デザイン・美術": """
ポスターの文字|The poster looks attractive, but the text is hard to read. Could we make the letters larger? Let's check it from across the room.|ポスターは魅力的ですが文字が読みにくいです。文字を大きくできますか。部屋の反対側から確認しましょう。|hard to read
色の選択|I like both versions of the drawing. The blue one feels calmer to me. Which version fits the story better?|絵はどちらの版も好きです。青い方が私には落ち着いて感じられます。どちらが物語に合っていますか。|feels calmer to me
作品の感想|This painting reminds me of my hometown. I can't explain exactly why. Maybe it is the light coming through the window.|この絵は故郷を思い出させます。なぜかはうまく説明できません。窓から入る光のせいかもしれません。|reminds me of
試作品を作る|Before building the final model, we made a paper version. It helped us notice a problem with the shape. We changed the design before buying materials.|完成模型の前に紙の版を作りました。形の問題に気づく助けになりました。材料を買う前に設計を変えました。|helped us notice
""",
    "日常生活・人間関係": """
予定を合わせる|I'd love to join you, but I'm busy on Saturday. Would Sunday afternoon be better? We could meet at the cafe near your house.|ぜひ参加したいのですが土曜は忙しいです。日曜の午後はどうですか。あなたの家の近くのカフェで会えます。|I'd love to
物を借りる|Could I borrow your umbrella for a few hours? I left mine at home. I'll bring it back when I return tonight.|数時間、傘を借りてもいいですか。自分のは家に置いてきました。今夜戻るときに返します。|Could I borrow
丁寧に断る|Thank you for inviting me. I'm afraid I can't make it this time. Please let me know when you plan another gathering.|誘ってくれてありがとう。残念ですが今回は行けません。また集まる予定ができたら教えてください。|I can't make it
誤解を解く|I think there has been a misunderstanding. I meant next Tuesday, not today. I'm sorry I wasn't clear about the date.|誤解があったと思います。今日ではなく次の火曜のつもりでした。日付をはっきり伝えずすみません。|there has been a misunderstanding
""",
}


def build_lessons():
    lessons = []
    for topic_index, (topic, rows) in enumerate(SEEDS.items(), 1):
        for index, row in enumerate(rows.strip().splitlines(), 1):
            title, english, japanese, phrase = row.split("|")
            lessons.append({
                "id": f"micro-{topic_index:02d}-{index:02d}", "topic": topic,
                "title": title, "english": english, "japanese": japanese,
                "phrase": phrase, "level": "A2–B1目安（未認定）",
                "kind": "original_fictional_micro_lesson",
                "recall_prompt": "英文を隠し、起きたこと・話し手の希望を英語で説明してください。次に自分の状況に置き換えて1文話してください。",
                "cloze": english.replace(phrase, "＿＿＿＿", 1),
            })
    return lessons


LESSONS = build_lessons()
BY_ID = {lesson["id"]: lesson for lesson in LESSONS}
TOPICS = list(SEEDS)


if __name__ == "__main__":
    path = Path(__file__).with_name("short_lessons.json")
    path.write_text(json.dumps({"schema_version": 1, "lessons": LESSONS}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(LESSONS)} lessons across {len(TOPICS)} topics to {path.name}")
