import re
"""Original editorial teaching material, not official examination questions."""
# Each paragraph has a complete Japanese translation. Scenarios are fictional.
STORIES = [
('station','travel','乗り換え駅で起きたこと','B1','city|train|clock',[
('Mina arrived at the station forty minutes before her train was due to leave. She had planned to buy a sandwich, find her platform, and read a few pages of her book. However, a notice near the entrance said that several platforms were closed for maintenance.','ミナは列車の出発予定時刻の40分前に駅に着いた。サンドイッチを買い、ホームを探し、本を数ページ読む予定だった。ところが入口付近の掲示には、整備のためいくつかのホームを閉鎖していると書かれていた。'),
('The departure board still showed her original platform, so she walked to the information desk. The employee checked the train number rather than just the destination. Two trains were going to the same city, but only one would stop at the smaller station where Mina needed to change.','出発案内板にはまだ元のホームが表示されていたので、案内所に向かった。係員は行き先だけでなく列車番号を確認した。同じ都市に行く列車は2本あったが、ミナが乗り換える小さな駅に停車するのは1本だけだった。'),
('Her train would now leave from platform eight on the other side of the building. The employee suggested using the lift because the footbridge had several flights of stairs. Mina was carrying a heavy suitcase, and she was grateful for advice that considered her luggage as well as the departure time.','列車は建物の反対側の8番ホームから出発することになった。跨線橋には階段が何か所もあるため、係員はエレベーターを勧めた。重いスーツケースを持つミナは、出発時刻だけでなく荷物にも配慮した助言に感謝した。'),
('At the new platform, she met a visitor studying the same confusing notice. Instead of simply telling him to follow her, she showed him the train number on her ticket. They compared it with his reservation and discovered that he needed the other train. He returned to the information desk.','新しいホームで、同じ分かりにくい掲示を読んでいる旅行者に会った。ただついてくるように言う代わりに、ミナは切符の列車番号を見せた。彼の予約と比べると、彼が必要なのはもう一方の列車だった。彼は案内所に戻った。'),
('Mina reached her seat with ten minutes to spare. She had no sandwich, but she had avoided a much longer delay. Later, she saved a photograph of the updated departure board and sent her host a short message explaining when she expected to arrive.','ミナは10分の余裕を残して座席に着いた。サンドイッチはなかったが、はるかに長い遅れは避けられた。その後、更新された案内板の写真を保存し、到着見込みを宿泊先の相手に短いメッセージで伝えた。')],
[('Why did Mina ask for help?',['Her ticket was missing.','Some platforms were closed.','Her train had already left.'],1),('Why was the train number important?',['The trains had different stopping patterns.','It determined the price of lunch.','All trains were cancelled.'],0),('What did she give up?',['Her reservation','Her suitcase','Buying a sandwich'],2)]),
('delivery','work','納品が遅れた日の判断','B1–B2','city|building|clock',[
('A small design studio was preparing an exhibition for a local client. The printed display boards were expected on Thursday morning, leaving a full day for installation. At nine, the supplier called to explain that a machine had broken down and the delivery would probably arrive on Friday afternoon.','小さなデザイン事務所が地元の顧客の展示会を準備していた。印刷した展示パネルは木曜の朝に届く予定で、設置に丸一日使えるはずだった。9時に仕入先から電話があり、機械が故障し、納品はおそらく金曜の午後になると説明された。'),
('The project manager, Leo, asked which items were already finished. Half of the boards were ready, but the supplier had planned to send everything together. Leo requested a written list of the completed items before promising the client a solution. He wanted to avoid replacing one uncertain promise with another.','担当のレオは、どの品がすでに完成しているか尋ねた。半分はできていたが、仕入先はすべてまとめて送るつもりだった。レオは顧客に解決を約束する前に、完成品の一覧を書面で求めた。不確かな約束を別の不確かな約束で置き換えたくなかった。'),
('His team considered renting temporary screens, printing smaller versions nearby, or installing the finished boards first. The screens would cost more than the remaining budget. Smaller prints were affordable, but visitors might struggle to read them from a distance. A split delivery seemed the most practical option.','チームは仮設スクリーンのレンタル、近所で小さい版を印刷すること、完成済みのパネルを先に設置することを検討した。スクリーンは残りの予算を超える。小さい印刷物は安いが、遠くから読みにくいかもしれない。分割納品が最も現実的に思われた。'),
('Leo explained the delay to the client and described both the benefit and the risk of the revised plan. The main entrance could be completed on Thursday, while the smaller room would remain closed until Friday evening. The client agreed, provided that the public announcement clearly identified the temporary closure.','レオは遅延と、変更案の利点とリスクの両方を顧客に説明した。正面入口は木曜に完成できるが、小さい部屋は金曜の夕方まで閉鎖する。顧客は、一時閉鎖を一般向けの案内に明示することを条件に同意した。'),
('Before leaving the office, Leo assigned one person to confirm delivery times and another to update the signs. He also recorded the additional transport cost. The exhibition opened with a smaller display than planned, but the team could explain exactly what was available and when the remaining section would open.','退社前にレオは納品時刻の確認係と掲示の更新係を決めた。追加の輸送費も記録した。展示は予定より小規模に始まったが、何が見られ、残りの区画がいつ開くかを正確に説明できた。')],
[('What did Leo request first?',['A list of completed items','A public apology','A larger exhibition room'],0),('Why were screens rejected?',['They were too small.','They exceeded the budget.','They arrived on Thursday.'],1),('What condition did the client set?',['Cancel all deliveries','Keep the delay secret','Announce the temporary closure clearly'],2)]),
('library','daily','図書館の静かな場所を守る','B1','paper|book|chat',[
('The neighborhood library had recently added a group study area beside the windows. Students liked the large tables, and parents used them to help children with homework. After a few weeks, however, other visitors began to complain that conversations carried across the room into the quiet reading area.','近所の図書館は最近、窓際にグループ学習スペースを設けた。学生は大きい机を気に入り、親は子どもの宿題を手伝っていた。しかし数週間後、会話が静かな読書スペースまで響くという苦情が出始めた。'),
('The librarian did not want to remove a service that many people valued. She spent three afternoons observing when the noise was greatest. The busiest period was just after school, not throughout the day. She also noticed that the existing sign asked people to be considerate without explaining what that meant.','司書は多くの人が大切にしているサービスをなくしたくなかった。午後に3日間、いつ最もうるさくなるか観察した。混雑するのは一日中ではなく放課後だった。また既存の掲示は、具体的な説明なしに配慮を求めていた。'),
('At a short meeting, regular visitors suggested several changes. One wanted complete silence everywhere, while another proposed moving all group work upstairs. The upstairs room was accessible only by stairs, so that option would exclude some visitors. The librarian asked the group to consider access as well as comfort.','短い会合で常連利用者が変更案を出した。全館で完全な静寂を求める人も、グループ作業をすべて上階に移す人もいた。しかし上の部屋は階段でしか行けず、一部の利用者が使えなくなる。司書は快適さに加え利用のしやすさも考えるよう求めた。'),
('For the next month, the library tried a different arrangement. Low shelves separated the two areas, and group tables were available for conversation between three and five. Signs showed examples of a quiet discussion and a phone call that should take place outside. Staff explained the trial to new visitors.','翌月、図書館は別の配置を試した。低い棚で二つのエリアを分け、3時から5時までグループの机で会話を認めた。掲示には小声の話し合いと、外ですべき電話の例を示した。職員は新しい利用者に試行を説明した。'),
('At the end of the trial, complaints had become less frequent, although not everyone was satisfied. The librarian collected comments before making the arrangement permanent. She wanted to know whether people who had stopped visiting were willing to return, rather than listening only to those who were already comfortable with the change.','試行の終わりには苦情が減ったが、全員が満足したわけではなかった。司書は恒久的に採用する前に意見を集めた。変更を快適に感じる人だけでなく、来なくなった人が戻る気になるかを知りたかった。')],
[('When was the noise greatest?',['Early morning','After school','Late at night'],1),('Why was the upstairs room unsuitable?',['It had no tables.','It was too bright.','Some people could not access it.'],2),('What happened before a permanent decision?',['Comments were collected.','The library closed.','All group work ended.'],0)]),
('museum','history','博物館のラベルを読み直す','B1–B2','paper|scroll|magnifier',[
('During a visit to a small museum, Hana stopped beside an old wooden box. Its label gave a date and a place but did not explain what the box had been used for. She imagined that it had held valuable jewelry. Her younger brother thought it might have carried tools instead.','小さな博物館で、ハナは古い木箱の前に立ち止まった。ラベルには年代と場所はあったが、用途の説明はなかった。彼女は宝石箱だと想像した。弟は工具を運ぶ箱かもしれないと考えた。'),
('A volunteer explained that the museum had received the box from a local family. The family remembered seeing it in a shop, but no document described its original contents. Marks inside the lid suggested that small objects had been attached there. That clue was interesting, but it did not prove either visitor correct.','ボランティアは、箱は地元の家族から寄贈されたと説明した。家族には店で見た記憶があったが、元の中身を記した資料はなかった。蓋の内側の跡から小さな物が取り付けられていたらしい。それは興味深い手がかりだが、二人のどちらが正しいかは証明しなかった。'),
('Hana asked why the museum displayed an object with such an uncertain history. The volunteer replied that uncertainty was part of the story. Everyday objects often survived without written records. Comparing materials, repairs, and wear could still help people ask useful questions about work and life in the town.','ハナは、由来がそれほど不確かな物をなぜ展示するのか尋ねた。不確かさも物語の一部だと説明された。日用品は記録なしで残ることが多い。材料、修理、摩耗を比べれば町の仕事や生活について有益な問いを立てられる。'),
('At the next display, a photograph showed a crowded street. Rather than assuming that everyone in the picture was shopping, Hana looked for other evidence. Some people carried packages, while others appeared to be waiting near a vehicle. She wrote down two possible explanations and a question she could not answer.','次の展示の写真には混雑した通りが写っていた。ハナは全員が買い物中だと決めつけず、別の証拠を探した。包みを持つ人も、乗り物の近くで待つように見える人もいた。彼女は二つの説明の可能性と、答えられない問いを書いた。'),
('On the way home, her brother said that museums should always give definite answers. Hana disagreed. She enjoyed learning which details were known, which were reasonable guesses, and which remained open. They decided to return for a workshop where visitors could compare objects and discuss how evidence supports an interpretation.','帰り道、弟は博物館はいつも確かな答えを示すべきだと言った。ハナは同意しなかった。何が既知で、何が妥当な推測で、何が未解決かを知るのが楽しかった。二人は、物を比較し証拠が解釈をどう支えるか話し合う催しにまた来ることにした。')],
[('What was unknown about the box?',['Its current location','Its original contents','Its material'],1),('What did the marks prove?',['It held jewelry.','It belonged to Hana.','Neither visitor’s explanation was proven.'],2),('What did Hana write?',['Possible explanations and a question','The price of the box','A shopping list'],0)]),
('cafe','food','カフェのメニューを小さくする','B1','day|bowl|chat',[
('A neighborhood cafe offered more than forty dishes, but its owner noticed that the kitchen often ran out of space. Ingredients for unpopular dishes occupied shelves for days. Meanwhile, customers ordering the most popular lunch sometimes had to wait while staff searched for a particular sauce or container.','近所のカフェは40種類以上の料理を出していたが、店主は厨房の場所が足りなくなりがちなことに気づいた。人気のない料理の材料が何日も棚を占めていた。一方、人気のランチを頼んだ客が、スタッフがソースや容器を探す間待つこともあった。'),
('The owner, Sara, decided to review the menu with her team. She brought a list of orders from the previous month, but she did not want to judge each dish by sales alone. A meal that sold only a few times might still be important for customers with particular dietary needs.','店主のサラはチームでメニューを見直した。前月の注文一覧を用意したが、販売数だけで評価したくはなかった。注文が少なくても、食事に特別な配慮が必要な客には大切な料理かもしれない。'),
('One cook suggested building several dishes around the same roasted vegetables. Another recommended keeping a simple option without dairy products. They checked which ingredients could be shared without making every meal taste alike. Sara also asked the serving staff which questions customers most often asked before placing an order.','ある料理人は同じ焼き野菜を使う料理をいくつか作る案を出した。別の人は乳製品を使わない簡単な選択肢を残すよう勧めた。すべてが同じ味にならない範囲で材料を共有できるか確認した。サラは接客係に、注文前によく聞かれることも尋ねた。'),
('The revised menu had fewer dishes and clearer descriptions. For two weeks, the cafe displayed a notice explaining that the changes were a trial. Customers could leave comments on a small card. Some missed an old favorite, while others said that choosing lunch had become easier and less confusing.','改訂版は料理の数を減らし、説明を分かりやすくした。2週間、変更は試行だと知らせる掲示を出した。小さなカードで意見を受け付けた。昔のお気に入りを惜しむ人も、ランチを選びやすくなったと言う人もいた。'),
('Sara compared waiting times, unused ingredients, and customer comments before deciding what to keep. She did not assume that a smaller menu was automatically better. Her goal was to make the kitchen easier to operate while preserving enough choice for the people who actually used the cafe each week.','サラは待ち時間、余った材料、客の意見を比較して残すものを決めた。小さいメニューが自動的によいとは考えなかった。目的は厨房を運営しやすくしながら、毎週来る客に十分な選択肢を保つことだった。')],
[('What caused a problem?',['Unused ingredients occupied space.','The cafe had no staff.','Customers never ordered lunch.'],0),('What did Sara consider besides sales?',['The color of the walls','Dietary needs','Parking fees'],1),('How were the changes introduced?',['Without explanation','As a permanent rule immediately','As a two-week trial'],2)]),
('software','tech','新しい予約システムの試運転','B1–B2','night|laptop|clock',[
('A community center planned to replace its paper reservation book with an online system. The new service would let residents check room availability from home. Staff hoped that this would reduce telephone calls, but they were concerned about people who did not own a computer or feel comfortable using one.','公民館は紙の予約帳をオンラインシステムに置き換える計画を立てた。住民は自宅で空室を確認できる。職員は電話を減らせると期待したが、パソコンがない人や操作に慣れない人を心配していた。'),
('Before launching the service, the center invited a small group to test it. Participants were asked to book a room for a fictional meeting, change the time, and cancel the booking. The organizer watched where they hesitated instead of explaining every button as soon as someone looked uncertain.','公開前に少人数を招き試してもらった。架空の会議室を予約し、時刻を変更し、予約を取り消すよう依頼した。担当者は迷うたびにすぐボタンを説明するのでなく、どこで立ち止まるか観察した。'),
('Several people completed the first step but could not tell whether their reservation had been confirmed. A green symbol appeared on the screen, yet there was no plain-language message. One participant clicked the button twice and created two requests. The team realized that color alone was not enough to communicate success.','最初の手順を終えても予約の確定が分からない人が何人かいた。緑の印は出るが、分かりやすい文章がなかった。一人はボタンを2回押して申請を二つ作った。色だけでは成功を伝えられないと分かった。'),
('The developers added a confirmation message with the date, room, and time. They also prevented repeated clicks from creating duplicate requests. A second test included people who had not seen the earlier version. This helped the team check whether the improvements were understandable without relying on instructions remembered from the first session.','開発者は日付、部屋、時刻を含む確認文を加えた。連打で重複申請ができないようにもした。2回目のテストには以前の版を見ていない人を含めた。最初の説明を覚えているからではなく、改良自体が分かりやすいかを確認するためだった。'),
('When the service opened, telephone and in-person reservations remained available. Staff entered those bookings into the same calendar so that everyone saw consistent information. The center planned to review support requests after one month. A successful launch meant reliable access for residents, rather than simply replacing every sheet of paper.','公開後も電話と窓口の予約を残した。職員はそれらも同じカレンダーに入力し、全員に一貫した情報を示した。1か月後に問い合わせを見直す予定だった。成功とは紙を全部なくすことではなく、住民が確実に利用できることだった。')],
[('What confused the testers?',['Whether a booking was confirmed','Where the center was','The meeting topic'],0),('Who joined the second test?',['Only developers','Some new participants','Only the same group'],1),('What remained available?',['Duplicate requests','The confusing symbol alone','Telephone reservations'],2)]),
('garden','environment','屋上の庭に必要な計画','B1','forest|tree|sun',[
('Residents of an apartment building wanted to turn part of their shared roof into a garden. They imagined flowers, vegetables, and a place to talk on summer evenings. At their first meeting, many people brought pictures of attractive gardens, but few had considered who would water the plants during holidays.','集合住宅の住民は共用の屋上の一部を庭にしたかった。花や野菜、夏の夕方に話せる場所を思い描いた。最初の会合では美しい庭の写真が集まったが、休暇中に誰が水やりするかを考えた人は少なかった。'),
('The building manager asked them to begin with practical questions. They needed professional advice about the roof before adding heavy containers. They also had to keep emergency routes clear and agree on opening hours. These requirements made the project less simple, but ignoring them would not make the problems disappear.','管理者は実務的な問いから始めるよう頼んだ。重い容器を置く前に屋上について専門家の助言が必要だった。避難経路を空け、利用時間にも合意しなければならない。複雑にはなるが、無視しても問題は消えない。'),
('Instead of filling the entire roof, the residents proposed a small trial in an approved area. Volunteers would share a weekly schedule, and each person would have a partner who could help when plans changed. The group chose plants after considering sunlight and water needs, not just the photographs on seed packets.','屋上全体を使わず、許可された区域で小さく試す案にした。ボランティアは週ごとの担当表を共有し、予定変更時に助ける相手を各自決めた。種袋の写真だけでなく、日光と水の必要量を考えて植物を選んだ。'),
('A resident who could not carry heavy pots offered to keep the schedule and record expenses. Another translated the instructions for neighbors who preferred a different language. The project became more inclusive when the group recognized that gardening involved organizing and communication as well as physical work on the roof.','重い鉢を運べない住民は担当表の管理と経費の記録を申し出た。別の人は他の言語を好む隣人のために説明を翻訳した。庭づくりには屋上の肉体労働だけでなく、調整と連絡もあると認めて参加しやすくなった。'),
('After the first season, not every plant had survived. The residents discussed missed watering days and containers that dried too quickly. They decided to improve the existing area before expanding it. Their most useful result was a workable way to cooperate, even though the garden looked less impressive than their original pictures.','最初の季節の後、すべての植物が生き残ったわけではなかった。水やりを忘れた日や乾きやすい容器を話し合った。広げる前に今の場所を改善することにした。写真ほど見栄えはしなくても、協力する実行可能な方法が最も役立つ成果だった。')],
[('What was often overlooked initially?',['Holiday watering','Flower colors','Garden photographs'],0),('Why start with a trial?',['To avoid all planning','To test a manageable arrangement','To block emergency routes'],1),('What did they decide after the season?',['Expand immediately','Stop communicating','Improve the current area first'],2)]),
('concert','music','小さな演奏会の舞台裏','B1–B2','night|note|film',[
('A student music group was preparing its first public concert in a small hall. The musicians had practiced the pieces for weeks, but their first rehearsal in the venue sounded different. Notes that were clear in the practice room seemed to blend together, and quiet passages were difficult to hear near the back.','学生の音楽グループが小さなホールで初めての公開演奏会を準備していた。何週間も練習した曲だが、会場での初リハーサルは違って聞こえた。練習室では明瞭な音が混ざり、後方では弱音が聞き取りにくかった。'),
('The conductor asked two members to walk around while the others played a short section. They listened from several seats rather than judging the sound from the stage alone. Their comments did not agree completely, which reminded the group that the audience would not all have exactly the same listening experience.','指揮者は他のメンバーが短い部分を演奏する間、二人に歩き回ってもらった。舞台上だけで判断せず複数の席で聞いた。意見は完全には一致せず、聴衆全員がまったく同じ聞こえ方をするわけではないと分かった。'),
('Moving a few chairs and leaving more space between sections improved the balance. The group also adjusted how strongly they played certain entrances. They recorded a short passage to compare versions, but used the recording as one source of feedback rather than assuming that a phone captured everything listeners would hear.','椅子を少し動かし、パート間を広げるとバランスが改善した。入りの強さも調整した。比較用に短く録音したが、スマートフォンが聴衆の聞くすべてを捉えると決めつけず、一つの評価材料にした。'),
('Meanwhile, another team prepared the program and checked the doors. One member noticed that the printed schedule did not mention an interval. They added a clear notice so visitors could plan when to leave their seats. A volunteer was assigned to help late arrivals enter between pieces without interrupting the performance.','別のチームはプログラムを用意し出入口を確認した。印刷した予定に休憩が書かれていないことに一人が気づいた。席を離れる時刻が分かるよう掲示を加えた。遅れて来た人を曲間に案内する係も決めた。'),
('On concert night, a few small mistakes occurred, but the musicians recovered and kept listening to one another. Afterward, they asked both performers and visitors for comments. Their next rehearsal plan included transitions and communication, not only difficult notes. They had learned that a concert is a shared event, supported by many decisions beyond playing the music.','本番では小さなミスもあったが、互いに聞き続けて立て直した。後で出演者と来場者の両方に意見を求めた。次の練習計画には難しい音だけでなく切り替えや意思疎通も含めた。演奏会は音を出す以外の多くの判断に支えられる共同の出来事だと学んだ。')],
[('Why did members walk around?',['To compare sound in different seats','To sell tickets','To find a lost phone'],0),('What was missing from the schedule?',['The performers’ names','An interval','The venue address'],1),('What was added to the next rehearsal plan?',['Only louder playing','More ticket sales','Transitions and communication'],2)])
]
# Phrase | Japanese | complete example | Japanese example. Unique, practical chunks.
PHRASE_TEXT = '''
in advance|前もって|Please book your seat in advance.|席は前もって予約してください。
on arrival|到着時に|You will receive a map on arrival.|到着時に地図を受け取ります。
be due to|～する予定である|The train is due to leave at noon.|列車は正午に出発する予定です。
with time to spare|余裕を持って|We arrived with time to spare.|余裕を持って到着しました。
change platforms|ホームを変える|We need to change platforms.|ホームを変える必要があります。
a connecting flight|乗り継ぎ便|I missed a connecting flight.|乗り継ぎ便に乗り遅れました。
keep the receipt|領収書を保管する|Please keep the receipt for your records.|記録のため領収書を保管してください。
subject to change|変更される場合がある|The schedule is subject to change.|予定は変更される場合があります。
at no extra charge|追加料金なしで|Breakfast is included at no extra charge.|朝食は追加料金なしで含まれています。
within walking distance|歩いて行ける距離に|The museum is within walking distance.|博物館は歩いて行ける距離にあります。
confirm a reservation|予約を確認する|I would like to confirm a reservation.|予約を確認したいです。
in the event of|～の場合には|In the event of a delay, we will call you.|遅れる場合には電話します。
meet a deadline|締め切りを守る|We worked together to meet a deadline.|締め切りを守るため協力しました。
ahead of schedule|予定より早く|The installation finished ahead of schedule.|設置は予定より早く終わりました。
behind schedule|予定より遅れて|The project is behind schedule.|プロジェクトは予定より遅れています。
place an order|注文する|You can place an order online.|オンラインで注文できます。
request a refund|返金を求める|Customers can request a refund within a week.|客は1週間以内なら返金を求められます。
in writing|書面で|Please confirm the revised date in writing.|変更した日付を書面で確認してください。
provided that|～という条件で|We can proceed provided that the client agrees.|顧客が同意すれば進められます。
prior to|～に先立って|Check the room prior to the meeting.|会議に先立って部屋を確認してください。
as scheduled|予定どおりに|The exhibition opened as scheduled.|展示会は予定どおり開幕しました。
on behalf of|～を代表して|I am calling on behalf of the manager.|部長に代わって電話しています。
follow up on|～のその後を確認する|I will follow up on your request tomorrow.|明日ご依頼のその後を確認します。
take into account|～を考慮に入れる|We should take into account the transport cost.|輸送費を考慮に入れるべきです。
run out of|～を使い果たす|We may run out of paper today.|今日紙がなくなるかもしれません。
be responsible for|～を担当している|Maya will be responsible for the signs.|マヤが掲示を担当します。
make arrangements|手配する|I will make arrangements for the delivery.|納品の手配をします。
get in touch with|～に連絡する|Please get in touch with the supplier.|仕入先に連絡してください。
within the budget|予算内で|We need a solution within the budget.|予算内の解決策が必要です。
out of stock|在庫切れで|That size is currently out of stock.|そのサイズは現在在庫切れです。
for the time being|当分の間|Use the side entrance for the time being.|当分の間は脇の入口を使ってください。
in response to|～に応えて|We changed the sign in response to feedback.|意見に応えて掲示を変えました。
under maintenance|整備中で|The lift is under maintenance.|エレベーターは整備中です。
make sure|確かめる|Make sure the door is locked.|ドアに鍵がかかっているか確かめてください。
get used to|～に慣れる|It takes time to get used to a new routine.|新しい習慣に慣れるには時間がかかります。
would rather|むしろ～したい|I would rather walk than wait.|待つより歩きたいです。
come up with|～を考え出す|Can you come up with another example?|別の例を考えられますか。
look into|～を調べる|The team will look into the problem.|チームが問題を調べます。
figure out|～を理解する|We need to figure out what went wrong.|何がうまくいかなかったのか理解する必要があります。
point out|～を指摘する|She pointed out a missing date.|彼女は日付が抜けていると指摘しました。
put off|～を延期する|We had to put off the meeting.|会議を延期しなければなりませんでした。
turn down|～を断る|They decided to turn down the offer.|彼らは申し出を断ることにしました。
bring up|話題に出す|Please bring up the issue at the meeting.|会議でその問題を話題にしてください。
carry out|～を実行する|The team will carry out a second test.|チームは2回目のテストを行います。
set aside|～を確保する|Set aside ten minutes for questions.|質問のために10分確保してください。
leave out|～を省く|Do not leave out the delivery address.|配送先の住所を省かないでください。
keep track of|～を把握しておく|This list helps us keep track of expenses.|この一覧で経費を把握できます。
in charge of|～を担当して|Who is in charge of reservations?|予約の担当は誰ですか。
depend on|～次第である|The opening date will depend on the weather.|開園日は天気次第です。
instead of|～の代わりに|Try asking a question instead of guessing.|推測する代わりに質問してみてください。
as long as|～である限り|You can use the room as long as you book it.|予約すれば部屋を使えます。
even though|～だけれども|We went ahead even though it was raining.|雨だったけれど実施しました。
unless otherwise stated|特に記載のない限り|Prices include tax unless otherwise stated.|特に記載のない限り価格は税込みです。
in accordance with|～に従って|Please act in accordance with the guidelines.|ガイドラインに従って行動してください。
be eligible for|～の対象となる|Members may be eligible for a discount.|会員は割引の対象となる場合があります。
be entitled to|～の権利がある|Ticket holders are entitled to one free drink.|チケットを持つ人は飲み物を1杯無料でもらえます。
be required to|～することを求められる|Visitors are required to sign in.|来訪者は受付で記名する必要があります。
be expected to|～すると予想される|The repair is expected to take two hours.|修理には2時間かかる見込みです。
on a regular basis|定期的に|We review the schedule on a regular basis.|予定を定期的に見直します。
at your convenience|ご都合のよいときに|Please reply at your convenience.|ご都合のよいときに返信してください。
for further information|詳しい情報については|For further information, contact the library.|詳しくは図書館にお問い合わせください。
as a result|その結果|The bus was late, and as a result we walked.|バスが遅れ、その結果私たちは歩きました。
on the other hand|一方で|The room is small; on the other hand, it is quiet.|部屋は小さいですが、一方で静かです。
to some extent|ある程度は|I agree to some extent.|ある程度は賛成です。
from my perspective|私の立場から見ると|From my perspective, access is the main issue.|私の立場から見ると利用のしやすさが主な問題です。
to put it another way|別の言い方をすれば|To put it another way, we need more time.|別の言い方をすれば、もっと時間が必要です。
for instance|例えば|Some tools, for instance a ruler, are reusable.|定規など再利用できる道具もあります。
in contrast|対照的に|The first room was noisy; in contrast, the second was quiet.|最初の部屋は騒がしく、対照的に次の部屋は静かでした。
in particular|特に|I liked the final piece in particular.|特に最後の曲が気に入りました。
in addition to|～に加えて|In addition to music, the event includes talks.|音楽に加えて講演もあります。
rather than|～よりもむしろ|Focus on the evidence rather than the label.|ラベルよりも証拠に注目してください。
not necessarily|必ずしも～ではない|A longer explanation is not necessarily clearer.|長い説明が必ずしも分かりやすいとは限りません。
a range of|さまざまな|The shop offers a range of local products.|店ではさまざまな地元商品を売っています。
be available|利用できる|A quiet room will be available after lunch.|昼食後は静かな部屋を使えます。
a temporary closure|一時閉鎖|The notice announced a temporary closure.|掲示は一時閉鎖を知らせていました。
a revised schedule|変更後の予定|Please check the revised schedule.|変更後の予定を確認してください。
a written estimate|書面の見積もり|Ask for a written estimate before agreeing.|同意する前に書面の見積もりを求めてください。
a confirmation message|確認メッセージ|You should receive a confirmation message.|確認メッセージが届くはずです。
an alternative option|別の選択肢|The staff suggested an alternative option.|職員は別の選択肢を提案しました。
a practical solution|現実的な解決策|We are looking for a practical solution.|現実的な解決策を探しています。
customer feedback|顧客の意見|Customer feedback helped us improve the menu.|顧客の意見でメニューを改善できました。
opening hours|営業時間|The opening hours are printed on the door.|営業時間はドアに表示されています。
remaining balance|残額|Please pay the remaining balance by Friday.|残額を金曜までにお支払いください。
additional charges|追加料金|There may be additional charges for transport.|輸送には追加料金がかかる場合があります。
proof of purchase|購入証明|Please bring proof of purchase.|購入証明をお持ちください。
annual membership|年間会員資格|An annual membership includes free admission.|年間会員資格には無料入場が含まれます。
a refund policy|返金方針|Read the refund policy before booking.|予約前に返金方針を読んでください。
a job vacancy|求人|The company advertised a job vacancy.|会社は求人広告を出しました。
relevant experience|関連する経験|Describe your relevant experience briefly.|関連する経験を簡潔に説明してください。
a performance review|業績評価|My performance review is scheduled for Monday.|私の業績評価は月曜の予定です。
a training session|研修|New staff will attend a training session.|新しい職員は研修に参加します。
a purchase order|発注書|We received the purchase order yesterday.|昨日発注書を受け取りました。
a shipping address|配送先住所|Please enter your shipping address.|配送先住所を入力してください。
an estimated arrival time|到着予定時刻|The driver gave us an estimated arrival time.|運転手は到着予定時刻を教えてくれました。
a maintenance request|修理依頼|I submitted a maintenance request for the lift.|エレベーターの修理依頼を出しました。
an attached document|添付書類|Please read the attached document.|添付書類を読んでください。
a brief summary|短い要約|Send me a brief summary of the meeting.|会議の短い要約を送ってください。
a reliable source|信頼できる情報源|Check the claim against a reliable source.|信頼できる情報源でその主張を確認してください。
a reasonable explanation|妥当な説明|That seems like a reasonable explanation.|それは妥当な説明のようです。
reach an agreement|合意に達する|We hope to reach an agreement today.|今日合意に達したいと思います。
raise a concern|懸念を示す|One resident raised a concern about noise.|ある住民が騒音の懸念を示しました。
clarify the purpose|目的を明確にする|First, clarify the purpose of the meeting.|まず会議の目的を明確にしてください。
compare the options|選択肢を比べる|Let us compare the options before deciding.|決める前に選択肢を比べましょう。
avoid confusion|混乱を避ける|Use clear labels to avoid confusion.|混乱を避けるため明確なラベルを使ってください。
provide evidence|証拠を示す|The report should provide evidence for its conclusion.|報告書は結論の証拠を示すべきです。
make a distinction|区別する|We need to make a distinction between fact and opinion.|事実と意見を区別する必要があります。
consider the consequences|結果を考える|Consider the consequences before changing the rule.|規則を変える前に結果を考えてください。
review the results|結果を見直す|We will review the results next week.|来週結果を見直します。
address the issue|問題に対処する|The team needs to address the issue today.|チームは今日その問題に対処する必要があります。
share the workload|作業を分担する|Two volunteers will share the workload.|二人のボランティアが作業を分担します。
keep someone informed|人に状況を知らせておく|We will keep you informed of any changes.|変更があればお知らせします。
take turns|交代する|We take turns checking the equipment.|交代で設備を確認します。
ask for clarification|説明を求める|Do not hesitate to ask for clarification.|遠慮せず説明を求めてください。
check for errors|誤りを確認する|Please check for errors before printing.|印刷前に誤りを確認してください。
make an adjustment|調整する|We need to make an adjustment to the timetable.|時刻表を調整する必要があります。
keep an open mind|決めつけずに考える|Try to keep an open mind during the discussion.|話し合いでは決めつけずに考えてください。
weigh the benefits|利点を比較検討する|We should weigh the benefits against the cost.|利点と費用を比較検討するべきです。
test an assumption|前提を確かめる|The trial will help us test an assumption.|試行で前提を確かめられます。
in the long run|長い目で見ると|Clear instructions save time in the long run.|明確な説明は長い目で見ると時間の節約になります。
as far as I know|私の知る限りでは|As far as I know, the room is still available.|私の知る限り部屋はまだ空いています。
'''

from extra_video_content import EXTRA_STORIES
STORIES.extend(EXTRA_STORIES)

# Added material lives in materials/*.json (see materials/README.md).
# Every file whose name starts with stories_, phrases_ or shorts_ is picked up automatically;
# files starting with "_" (templates) are ignored.
import json
from pathlib import Path
MATERIALS = Path(__file__).resolve().parent / 'materials'
def material_files(prefix):
    return sorted(f for f in MATERIALS.glob(prefix + '_*.json') if not f.name.startswith('_'))
def _read(f):
    return json.loads(f.read_text(encoding='utf-8'))
def phrase_id(en):
    """Stable id from the English phrase, so reordering or adding files never breaks review history."""
    return 'phrase-v3-' + re.sub(r'[^a-z0-9]+', '-', en.lower()).strip('-')
BUILTIN_STORY_KEYS = {s[0] for s in STORIES}
for _f in material_files('stories'):
    STORIES.extend((d['key'], d['g'], d['title'], d['level'], d['scene'], [tuple(x) for x in d['paras']], [tuple(q) for q in d['qs']]) for d in _read(_f))
PHRASE_FILES = [(f.stem[len('phrases_'):], _read(f)) for f in material_files('phrases')]
NEW_SHORTS = [s for f in material_files('shorts') for s in _read(f)]

def export_decks():
    """8-card phrase decks, one run of decks per phrases_*.json file."""
    decks = []
    for stem, d in PHRASE_FILES:
        rows = d['phrases']
        for k in range(0, len(rows), 8):
            cards = [phrase_id(r[0]) for r in rows[k:k+8]]
            decks.append(dict(id=f'{stem}-{k//8}', t=f"{d['deck']} · セット{k//8+1}", level=d['level'], sc=d.get('scene', 'paper|book|chat'), cards=cards))
    return decks

def export():
    lessons=[]
    for key,g,title,level,scene,paras,qs in STORIES:
        slides=[]
        for n,(en,ja) in enumerate(paras):
            english=re.split(r'(?<=[.!?])\s+',en)
            japanese=[x for x in re.split(r'(?<=。)',ja) if x]
            # Keep an unmatched paragraph intact instead of inventing alignment.
            scene_n=scene.split('|')[0]+'|'+scene.split('|')[1]+'|'+['clock','magnifier','chat','book','sun'][n%5]
            slides.extend([[scene_n,e,j] for e,j in zip(english,japanese)] if len(english)==len(japanese) else [[scene_n,en,ja]])
        lessons.append(dict(id='long-'+key,g=g,t=title,level=level,sl=slides, paragraphs=[[scene,en,ja] for en,ja in paras],qs=qs,kind='listen'))
    phrases=[]
    for i,line in enumerate(PHRASE_TEXT.strip().splitlines()):
        en,ja,ex,exja=line.split('|')
        phrases.append([f'phrase-v2-{i+1:03}',en,ja,ex,exja])
    for _stem, d in PHRASE_FILES:
        for en,ja,ex,exja in d['phrases']:
            phrases.append([phrase_id(en),en,ja,ex,exja])
    return lessons,phrases
