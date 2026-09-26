# 自然話者の音声パック

ホーム → 聞き分け →「自然話者の音声教材を読み込む」で、`manifest.json` と音声を同時に選びます。音声は外部送信しません。再読み込み後は選び直してください。

以下は形式の例です。**音声ファイルは同梱していません。** 実際の話者が単語を発話した、利用権のある録音を用意してください。同じ合成音声を異なる話者名で登録しても自然話者教材にはなりません。

```json
{
  "version": 1,
  "samples": [
    {"speaker":"speaker-a","pair":["light","right"],"answer":0,"file":"a-light.wav","split":"train"},
    {"speaker":"speaker-a","pair":["light","right"],"answer":1,"file":"a-right.wav","split":"train"},
    {"speaker":"speaker-b","pair":["light","right"],"answer":0,"file":"b-light.wav","split":"train"},
    {"speaker":"speaker-b","pair":["light","right"],"answer":1,"file":"b-right.wav","split":"train"},
    {"speaker":"speaker-c","pair":["lock","rock"],"answer":0,"file":"c-lock.wav","split":"test"},
    {"speaker":"speaker-c","pair":["lock","rock"],"answer":1,"file":"c-rock.wav","split":"test"}
  ]
}
```

- `answer`: 0はpairの左、1は右。
- `speaker`: 実際の同一話者には同じ識別子。個人名は不要。
- `train`: 少なくとも2人。各話者・各ペアの両方の単語の録音を用意。
- `test`: 任意。練習と話者・単語が重ならないこと。確認でも回答後には正誤を示すため、繰り返し解いた結果は初見の成績ではありません。
- ファイル名は一意で、各録音を使う問題は1件。音声はwav/mp3/ogg/m4a/webm。端末で再生できる形式を選択。
- 上限は500件、音声合計100MB、manifest.jsonは1MB。

実際には複数の音環境・単語、十分な話者数の教材を用意する必要があります。この最小例と読み込み機能だけで、研究と同じ訓練量や効果を保証しません。
