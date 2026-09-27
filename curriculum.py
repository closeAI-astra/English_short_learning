"""Explicit learning routes over existing stable lesson ids."""
def short_ids(prefix, start, end):
    return [f'{prefix}-{i:02}' for i in range(start, end + 1)]

def build_curriculum(long_lessons, shorts):
    stages = [
        dict(title='1 · 文の骨格を固める', description='文法の用語は既習でも、文の中で即座に見抜けるかを確認。品詞・一致・時制・態・代名詞・比較・修飾を扱います。',
             target='根拠を説明して解答し、別の例文でも同じ構造を見抜ける。',
             ids=['long-bridgestudyplan'] + short_ids('bridge850', 16, 27) + ['long-bridgegrammar', 'long-internhiring']),
        dict(title='2 · 音から目的・担当・条件をつかむ', description='Part 1〜4 の着眼点、間接応答、否定疑問、聞き直し、担当変更、発言の意図、一覧との照合。',
             target='まず字幕なしで解答。原稿確認後に字幕を隠して、条件と変更を聞き取る。',
             ids=short_ids('bridge850', 1, 15) + ['long-bridgelistening', 'long-bridgeannouncement', 'long-conference', 'long-maintenance']),
        dict(title='3 · 文脈と複数文書を読み切る', description='Part 6〜7。接続・指示語・文挿入・言い換え・推論・NOT・照合・時間配分を順に練習。',
             target='各解答の根拠文を特定し、最も迷った誤答が違う理由も説明する。',
             ids=short_ids('bridge850', 28, 36) + ['long-bridgeinsertion', 'long-bridgeinvoice', 'long-bridgehiring', 'long-bridgereport', 'long-shipment', 'long-quarterlyresults']),
        dict(title='4 · 会話と身近な題材へ広げる', description='自然さは場面・関係・地域で変わります。会話24本と生活題材50本は、下のテーマ別一覧から選べます。',
             target='別の場面を自分で作り、学んだ表現で説明。数日後にもう一度、原文なしで話す。',
             ids=['long-bridgeconversation', 'long-bridgeclarify', 'long-bridgerecycling', 'long-bridgeclothes', 'long-bridgepricing', 'long-bridgetravel', 'long-businesstrip', 'long-defectivegoods']),
    ]
    collections = [
        dict(title='Native or Weird? · NATURAL', description='誤りと決めつけず、意味と会話の役割を比較。', ids=[s['id'] for s in shorts if s['id'].startswith('native-') and s['t'].startswith('NATURAL')]),
        dict(title='Native or Weird? · SITUATION', description='相手・場所・用件から、その場面に合う言い方を選ぶ。', ids=[s['id'] for s in shorts if s['id'].startswith('native-') and s['t'].startswith('SITUATION')]),
        dict(title="Native or Weird? · DON'T SAY IT LIKE THAT", description='意味が変わる誤用と、強く聞こえうる言い方を区別。', ids=[s['id'] for s in shorts if s['id'].startswith('native-') and s['t'].startswith("DON'T")]),
        dict(title='リサイクル・環境 · 10本', description='燃料利用、キャップ、寄付した服、再利用、修理、食品ロス、統計。', ids=short_ids('curiosity', 1, 10)),
        dict(title='日常の「そういうことか」 · 15本', description='横断歩道、エレベーター、待機電力、予約、通知、時差、手続。', ids=short_ids('curiosity', 11, 25)),
        dict(title='お金・お店の仕組み · 15本', description='単価、エンド陳列、チップ、送料、ポイント、契約条件、見積もり。', ids=short_ids('curiosity', 26, 40)),
        dict(title='食・旅行 · 10本', description='映画館、解凍魚、航空券、ホテル、搭乗、乗継、口コミ。', ids=short_ids('curiosity', 41, 50)),
        dict(title='既存の長文でも練習する', description='これまでの仕事・旅行・科学・歴史などの教材も残しています。', ids=[l['id'] for l in long_lessons if not l['id'].startswith('long-bridge')]),
    ]
    known = {x['id'] for x in long_lessons + shorts}
    for group in stages + collections:
        missing = set(group['ids']) - known
        if missing:
            raise ValueError(f'Curriculum has missing lessons: {sorted(missing)}')
    return dict(title='600点台から850を目指す · 学習コース',
                intro='大学受験レベルの文法・語彙を土台に、理解を速さと正確さへ。新作ショート110本＋長文14本を追加しました。',
                routine='1日の例：ショート2〜4本 → 長文1本 → 誤答の根拠確認 → 前に学んだ表現を原文なしで再現。得意な単元は確認問題で点検して先へ進めます。',
                limitation='本数や正答率はTOEICの換算点ではありません。Part 1の実写真、複数話者・アクセントの録音、本番の図表・複数文書レイアウト、通しの時間制限演習は公式教材などで補ってください。',
                stages=stages, collections=collections,
                references=[
                    ['TOEIC公式：形式・構成', 'https://www.iibc-global.org/toeic/test/lr/about/format.html'],
                    ['TOEIC公式：サンプル問題', 'https://www.iibc-global.org/toeic/test/lr/about/format/sample01.html'],
                    ['Cambridge：依頼の表現', 'https://dictionary.cambridge.org/us/grammar/british-grammar/requests'],
                    ['PETボトルリサイクル推進協議会', 'https://www.petbottle-rec.gr.jp/'],
                    ['EPA：リサイクルのよくある質問', 'https://www.epa.gov/recycle/frequent-questions-recycling'],
                    ['British Red Cross：衣類などの寄付', 'https://www.redcross.org.uk/shop/donating-items-to-our-charity-shops'],
                    ['FHWA：信号と歩行者検知', 'https://ops.fhwa.dot.gov/publications/fhwahop08024/chapter4.htm'],
                    ['米国エネルギー省：待機電力', 'https://www.energy.gov/cmei/femp/measuring-standby-power'],
                    ['NIST：単価表示', 'https://www.nist.gov/news-events/news/2024/12/best-practices-uniform-unit-pricing-update-nist-sp-1181-and-nist-handbook'],
                    ['FDA：生鮮・冷凍の魚介類', 'https://www.fda.gov/food/buy-store-serve-safe-food/selecting-and-serving-fresh-and-frozen-seafood-safely'],
                    ['米国運輸省：過剰予約', 'https://www.transportation.gov/individuals/aviation-consumer-protection/bumping-oversales'],
                ])
