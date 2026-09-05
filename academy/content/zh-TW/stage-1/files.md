# 文字檔案處理

> 對應 Goal：`G1.16`, `G1.17` ｜ 練習預估 5 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.13

## 為什麼學這個

將檔案內容轉成有規則的資料，而不是靠畫面猜測。

## 概念

以 UTF-8 明確指定文字編碼。CSV 可能有引號、逗號和換行，不能用 split(",") 當通用解析器；數值讀進來是字串，轉型後才能相加。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import csv
import io
from collections import defaultdict
rows = csv.DictReader(io.StringIO("team,score\nA,2\nB,3\nA,4\n"))
totals = defaultdict(int)
counts = defaultdict(int)
for row in rows:
    totals[row["team"]] += int(row["score"])
    counts[row["team"]] += 1
print(dict(totals), dict(counts))
```

### 預期結果

得到 {'A': 6, 'B': 3} 與 {'A': 2, 'B': 1}。

## 練習與驗收

把輸入存成 scores.csv，改用 `open(..., encoding="utf-8", newline="")`。輸出分組 CSV。加入含逗號的群組名、空檔、壞分數；明定報錯或略過政策。另用 b"\xff".decode("utf-8") 觸發 UnicodeDecodeError，再比較 errors="strict" 與 "replace"，保存差異。

## 常見坑

errors="ignore" 可能默默丟掉資料；只有能接受損失時才使用。CSV 轉型失敗時要留下列號，不能把錯誤值當成 0。

## 自測清單

- [ ] `G1.16` 能讀寫 UTF-8 文字檔並處理編碼錯誤（errors 參數）。證據方式：`self`。
- [ ] `G1.17` 能解析 CSV 並輸出簡單統計（計數、求和、分組）。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/library/csv.html)。
