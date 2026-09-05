# 資料格式

> 對應 Goal：`G2.4`, `G2.5` ｜ 練習預估 4 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.16

## 為什麼學這個

在儲存格式之間轉換時，明確處理型別與資訊損失。

## 概念

JSON 保存數字、布林、陣列與物件；CSV 主要是欄列文字，沒有原生巢狀結構或型別宣告。先定義 schema，再轉换；JSON 的 true/null 會對應 Python 的 True/None。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import csv, io, json
source = "name,count\nKai,2\nLin,3\n"
rows = [{"name": r["name"], "count": int(r["count"])}
        for r in csv.DictReader(io.StringIO(source))]
encoded = json.dumps(rows, ensure_ascii=False)
restored = json.loads(encoded)
assert restored == rows
out = io.StringIO(newline="")
w = csv.DictWriter(out, fieldnames=["name", "count"])
w.writeheader()
w.writerows(restored)
print(out.getvalue())
```

### 預期結果

往返後兩筆資料的意義相同；CSV 的換行風格可能不同，所以不要拿原始 bytes 相等當唯一成功標準。

## 練習與驗收

加入中文名字、逗號與引號。實作 read_rows 與 write_rows，規定 count 必須非負整數。用錯欄位、重複欄名、null 與非整數測試拒絕路徑，寫下哪些輸入會損失資訊。

## 常見坑

不要使用 eval 解析資料。JSON 的物件鍵只能是字串；大型整數跨 JavaScript 時可能失真，識別碼宜保留為字串。

## 自測清單

- [ ] `G2.4` 能用 json.dumps/loads 在物件與字串之間往返轉換。證據方式：`self`。
- [ ] `G2.5` 能把 CSV 轉成 JSON 並反向匯出。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/library/json.html)。
