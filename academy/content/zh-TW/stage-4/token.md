# Tokenizer 與資料

> 對應 Goal：`G4.12`, `G4.13` ｜ 練習預估 6 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G2.18

## 為什麼學這個

理解模型看到的是 token 序列，以及詞表如何改變成本。

## 概念

BPE 從小單位開始，每次合併最常見的相鄰 pair。詞表大通常縮短序列，但 embedding 與輸出層增大；字元模型詞表小，序列較長。訓練、驗證、測試應先按來源切開再去重，不能讓同一文件的副本分散到不同集合。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
from collections import Counter
words = [list(w) for w in ["low", "low", "lower", "lowest"]]
pairs = Counter(pair for w in words for pair in zip(w,w[1:]))
best = sorted(pairs, key=lambda p: (-pairs[p], p))[0]
print(best, pairs[best])
merged = []
for w in words:
    out, i = [], 0
    while i < len(w):
        if i+1 < len(w) and (w[i],w[i+1]) == best:
            out.append(w[i]+w[i+1]); i += 2
        else:
            out.append(w[i]); i += 1
    merged.append(out)
print(merged)
```

### 預期結果

最常見同分 pair 按字典序決定；這一輪合併 l,o。這是字元級 BPE 教學，不是 byte-level、Unicode 完整 tokenizer。

## 練習與驗收

再做三輪，保存 merge 順序。實作 encode/decode 並驗證已見字元往返；明定未知字元政策。對同樣文本比較字元與 BPE 的長度，再加入大小寫、中文、空白邊界案例。用文件雜湊找完全重複，另外人工查近似重複。

## 常見坑

不能只保存詞表而丟掉 merge 順序；不同規則會產生不同編碼。去重與清洗也可能刪掉少數語言內容，需記錄規則與比例。

## 自測清單

- [ ] `G4.12` 能訓練或使用一個 BPE tokenizer 並解釋詞表大小的取捨。證據方式：`self`。
- [ ] `G4.13` 能解釋資料清洗與去重對模型品質的影響。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://huggingface.co/learn/llm-course/chapter6/5)。

## 互動實驗

用 [TokenScope 實驗路線](../../../../docs/tokenscope-labs.md)先預測、再操作與核對數值，匯出後重載重播。這是補充練習，不會自動標記本課學習目標完成。
