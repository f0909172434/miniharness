# 資料結構

> 對應 Goal：`G1.5`, `G1.6`, `G1.7` ｜ 練習預估 6 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.2, G1.3

## 為什麼學這個

選對容器讓統計規則簡單，也讓輸出可重現。

## 概念

list 保留順序且可變；tuple 適合固定記錄；dict 表達鍵到值；set 表達唯一成員。本課以空白切詞、轉小寫，先按次數遞減，再按字母排序處理同分。這是指定規則，尚不處理中文斷詞或標點。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
def word_counts(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return sorted(counts.items(), key=lambda row: (-row[1], row[0]))

print(word_counts("Bee ant bee CAT ant"))
```

### 預期結果

得到 [('ant', 2), ('bee', 2), ('cat', 1)]；空字串得到 []。

## 練習與驗收

關閉範例，重新在 academy/submissions/wordcount.py 實作 word_counts(text)。測空字串、大小寫、多個空白與同次數排序，再執行 `python3 tools/academy.py verify --goal G1.6`。用自己的文字說明為何先用 dict，回傳卻用 list of tuple。

## 常見坑

set 不保證你想要的展示順序；只按次數排序也不能定義所有同分情況。明寫規則，再設計能區分錯誤實作的測例。

## 自測清單

- [ ] `G1.5` 能針對問題選用 list/tuple/dict/set 並說明理由。證據方式：`self`。
- [ ] `G1.6` 能用 dict 統計一段文字的詞頻並按次數排序輸出。證據方式：`checker`。
- [ ] `G1.7` 能說出 list 與 tuple、dict 與 set 的選型理由與典型場景。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/tutorial/datastructures.html)。
