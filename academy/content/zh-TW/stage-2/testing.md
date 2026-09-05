# 測試與除錯方法論

> 對應 Goal：`G2.6`, `G2.7`, `G2.8` ｜ 練習預估 6 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.21

## 為什麼學這個

測試應能分辨正確行為和看似合理的錯誤修改。

## 概念

先寫 clamp(value,low,high) 的契約：值落在範圍內保持原值，越界截到邊界，low>high 則 ValueError。單元測試查函式；整合測試查 CLI、檔案或元件串接。先看紅燈，再最小修正，最後整理重複程式。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
# academy/submissions/test_numeric.py
import pytest
from numeric import clamp

def test_normal():
    assert clamp(3, 0, 5) == 3

def test_boundary():
    assert clamp(-1, 0, 5) == 0
    assert clamp(5, 0, 5) == 5

def test_error():
    with pytest.raises(ValueError):
        clamp(1, 5, 0)
```

### 預期結果

先在同目錄 numeric.py 定義空函式，此時測試應紅；正確實作後三個測試通過。需要在開發環境安裝 pytest。

## 練習與驗收

執行 `python3 tools/academy.py verify --goal G2.6`；再加入上界越界、上下界相同與負數案例。把例外檢查刪掉，確認 test_error 變紅。記錄一次完整 TDD 迴圈，並畫出你的單元與 CLI 整合測試分工。

## 常見坑

測試檔存在不等於測試有執行；檢查收集數量。過多端到端測試會讓定位與速度變差，但全是 mock 也驗不到真正串接。

## 自測清單

- [ ] `G2.6` 能用 pytest 為一個函式寫正常/邊界/異常三類測試並全綠。證據方式：`checker`。
- [ ] `G2.7` 體驗一次 TDD 迴圈：先寫失敗測試，再讓它變綠。證據方式：`self`。
- [ ] `G2.8` 能解釋單元測試與整合測試的差別及測試金字塔。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.pytest.org/en/stable/getting-started.html)。
