# 用 TokenScope 看清楚模型機制

先在瀏覽器改一個條件，預測結果，再核對數值；不需要先訓練模型。這條路線支援第 4 階段的 attention／tokenizer 學習目標，也可獨立使用，不是八步 harness 動手營的先修門檻。

| 實驗 | 操作與要回答的問題 | 對應目標 |
|---|---|---|
| [Attention](https://f0909172434.github.io/tokenscope/?lang=zh-Hant#attention) | 選第三個 token，開啟遮罩並擾動最後一個 V。先預測輸出是否變化，再關閉遮罩比較。寫下 QKᵀ／√d、遮罩與加權和的作用。 | G4.9 |
| [BPE](https://f0909172434.github.io/tokenscope/?lang=zh-Hant#bpe) | 使用「重疊配對」與繁中詞族，手算下一對頻率；合併兩次再復原一步。說明為何配對計數可重疊、實際替換不可重疊。 | G4.12 |
| [Sampling](https://f0909172434.github.io/tokenscope/?lang=zh-Hant#sampling) | 固定 seed，改變 temperature、top-k 與 top-p，觀察候選集合與機率。T=0 同分時會選誰？ | 第 4 階段延伸練習 |

每個實驗匯出一份 JSON；重新整理後匯入，檢查設定與重新計算的輸出是否相同。保留你最初的預測、輸出與修正解釋作為學習記錄。匯入成功不會自動將 MiniAcademy 的任何目標標成完成。

TokenScope 是單頭手工向量、固定 logits 獨立抽樣及逐詞 Unicode BPE 的教學實驗；不是完整 Transformer 訓練或 GPT byte-level tokenizer。[格式與重播範圍](https://github.com/f0909172434/tokenscope/blob/main/docs/REPLAY.md)。

看懂後，可回到 [Transformer 教材](../academy/content/zh-TW/stage-4/transformer.md)、[Tokenizer 教材](../academy/content/zh-TW/stage-4/token.md)，或直接進 [八步動手營](../tutorial/README.md)。
