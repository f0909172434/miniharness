# 錯誤、異常與除錯

> 對應 Goal：`G1.12`, `G1.13`, `G1.14`, `G1.15` ｜ 練習預估 5 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.8

## 為什麼學這個

在程式不符合預期時，用可重現的證據縮小原因。

## 概念

語法錯誤在解析時就中止；執行期異常有 traceback；邏輯錯誤可能正常結束卻算錯。先固定失敗輸入，再讀完整呼叫鏈；記錄函式入口和出口可定位第一個不符預期的位置。finally 用於必要的收尾，檔案通常優先使用 with。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
from pathlib import Path
try:
    text = Path("missing.txt").read_text(encoding="utf-8")
except FileNotFoundError:
    print("找不到檔案，請檢查工作目錄")
finally:
    print("讀取嘗試結束")
```

### 預期結果

當 missing.txt 不存在，印出提示與收尾文字。其他異常不會被這個 except 吞掉。

## 練習與驗收

寫一個 mean(values)，故意用 len(values)+1 當分母。用 [2,4] 發現結果不等於 3，加入 logging，再將流程對半停用或縮小資料定位分母錯誤。保存失敗、假設、最小案例、修正、回歸測試。另寫一個外層呼叫內層 int("x") 的例子，逐行解讀 traceback。

## 常見坑

不要用 `except Exception: pass` 消除線索。二分停用必須保留必要資料依賴；停用後換成另一種錯誤，不能推論原本故障已定位。

## 自測清單

- [ ] `G1.12` 能區分語法錯誤、執行期異常與邏輯錯誤並各舉一例。證據方式：`self`。
- [ ] `G1.13` 能用 try/except/finally 處理可預期異常（如檔案不存在）。證據方式：`self`。
- [ ] `G1.14` 用 print/logging 與二分注釋法定位並修復一個真實 bug。證據方式：`project`。
- [ ] `G1.15` 能讀懂 traceback：指出出錯檔案、行號與完整呼叫鏈。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/library/logging.html)。
