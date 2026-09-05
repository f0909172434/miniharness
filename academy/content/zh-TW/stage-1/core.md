# 變數、型別與控制流

> 對應 Goal：`G1.1`, `G1.2`, `G1.3`, `G1.4` ｜ 練習預估 6 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G0.6

## 為什麼學這個

讓同一份程式依輸入選擇不同動作，並追查狀態如何改變。

## 概念

變數綁定物件。整數與字串不可變；list 可以原地修改，兩個名字可能指向同一個 list。`if` 選分支，`for` 逐一走訪，`while` 持續到條件不成立。`input` 得到的 "3" 與整數 3 不同。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
for value in [-1, 0, 2]:
    if value < 0:
        label = "negative"
    elif value == 0:
        label = "zero"
    else:
        label = "positive"
    print(value, label, value / 2, value > 0)
a = [1]
b = a
b.append(2)
print(a)
```

### 預期結果

三個分支各執行一次，最後 a 是 [1, 2]；不是 [1]。`/` 產生 float，`>` 產生 bool。

## 練習與驗收

將 for 改成 while，列出每次索引、value 與 label。再讓 b = a.copy()，預測並確認 a 的結果。設計 3 個 if 分支測例，加上 "2" 轉 int 後的比較。

## 常見坑

while 忘記更新條件會一直執行。用小範圍測資逐步推演，再放大資料；不要用 break 掩蓋不明的停止條件。

## 自測清單

- [ ] `G1.1` 能用變數與 int/float/str/bool 四種型別寫小程式。證據方式：`self`。
- [ ] `G1.2` 能用 if/elif/else 寫出三分支邏輯並全部分支測試過。證據方式：`self`。
- [ ] `G1.3` 能用 for/while 寫循環並在紙上手動推演循環變數的每一步。證據方式：`self`。
- [ ] `G1.4` 能解釋可變物件與不可變物件的差別並舉例說明副作用。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/tutorial/controlflow.html)。
