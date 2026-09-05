# SQL 入門

> 對應 Goal：`G2.15`, `G2.16` ｜ 練習預估 4 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.17

## 為什麼學這個

讓資料可依條件查詢，並明確表示唯一性。

## 概念

主鍵保證一列的識別，不應重複。索引是為查找付出額外儲存和寫入成本的結構；主鍵常有索引支援，但概念不相同。SQL 的 GROUP BY 會把多列聚合成群組。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import sqlite3
with sqlite3.connect(":memory:") as db:
    db.execute("CREATE TABLE log(id INTEGER PRIMARY KEY, topic TEXT, minutes INTEGER)")
    db.executemany("INSERT INTO log VALUES(?,?,?)", [(1,"Python",30),(2,"Math",20),(3,"Python",15)])
    rows = db.execute("SELECT topic, SUM(minutes) FROM log WHERE minutes > ? GROUP BY topic ORDER BY topic", (0,)).fetchall()
    db.execute("CREATE INDEX by_topic ON log(topic)")
    print(rows)
```

### 預期結果

得到 [('Math', 20), ('Python', 45)]。

## 練習與驗收

把 :memory: 換成練習用 log.sqlite，關閉後重開確認資料仍在。插入重複主鍵觀察 IntegrityError；用 EXPLAIN QUERY PLAN 比較新增索引前後的 topic 查詢。測帶單引號的 topic，確認參數化查詢仍正常。

## 常見坑

不要用 f-string 拼入使用者輸入。刪除或更新前先用相同條件 SELECT；本課只使用自己的練習資料庫。

## 自測清單

- [ ] `G2.15` 能建表、插入資料並用 SELECT/WHERE/ORDER BY/GROUP BY 查詢。證據方式：`self`。
- [ ] `G2.16` 能解釋主鍵與索引各自的作用。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/library/sqlite3.html)。
