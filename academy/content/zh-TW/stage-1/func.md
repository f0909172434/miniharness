# 函式與模組

> 對應 Goal：`G1.8`, `G1.9`, `G1.10`, `G1.11` ｜ 練習預估 6 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.6

## 為什麼學這個

把可重用的計算和輸入輸出拆開，改動時才知道影響範圍。

## 概念

函式把參數轉成回傳值；docstring 說明契約，包括無效輸入。模組是可匯入的 .py 檔。把下例的函式存為 prices.py，另一個 main.py 用 `from prices import total`；用 `if __name__ == "__main__"` 避免匯入時就問使用者問題。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
rate = 0.05

def total(price, rate):
    """回傳含稅金額；price 必須非負。"""
    if price < 0:
        raise ValueError("price must be nonnegative")
    return round(price * (1 + rate), 2)

print(total(100, 0.1))
print(rate)
```

### 預期結果

輸出 110.0 與 0.05。函式參數 rate 遮蔽全域名字，沒有改動全域 rate。

## 練習與驗收

在三個位置各寫一段重複的含稅計算，保存三筆輸入輸出，再提取成 total。比對重構前後相同輸入得到相同輸出；保存 diff、正常與無效案例。把 main.py 和 prices.py 分開後確認匯入不會觸發互動輸入。

## 常見坑

用 print 取代 return 會讓呼叫端得到 None。不要為了重用而把所有變數都改成全域狀態。

## 自測清單

- [ ] `G1.8` 能定義帶參數與返回值的函式並撰寫 docstring。證據方式：`self`。
- [ ] `G1.9` 完成一次真實重構：把重複程式碼提取成函式且行為不變。證據方式：`project`。
- [ ] `G1.10` 能把程式拆成多個模組並用 import 組織。證據方式：`self`。
- [ ] `G1.11` 能預測變數遮蔽（區域/全域作用域）的行為並解釋原因。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/tutorial/modules.html)。
