# 資料科學工具鏈

> 對應 Goal：`G3.11`, `G3.12`, `G3.13` ｜ 練習預估 8 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G3.2, G1.17

## 為什麼學這個

在轉換與視覺化之前，先確認資料形狀與缺值規則。

## 概念

NumPy 廣播由尾端維度比較：相等或一方為 1 才能對齊。pandas 依欄名操作並保留索引，缺值政策要明寫；圖表必須有單位、標題與可追溯資料。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
X = np.array([[1., 2.], [3., 6.], [5., 4.]])
print(X - X.mean(axis=0))
df = pd.DataFrame({"topic":["Python","Math","Python"], "minutes":[30,20,15]})
totals = df[df.minutes > 0].groupby("topic").minutes.sum()
ax = totals.plot.bar()
ax.set(title="Study time by topic", xlabel="Topic", ylabel="Minutes")
plt.tight_layout()
plt.savefig("study-time.png")
```

### 預期結果

中心化後每欄平均接近 0；圖上 Python=45、Math=20。執行會在目前目錄產生 study-time.png。

## 練習與驗收

改用 CSV 載入，加入缺值與非數字，先報告清洗掉幾列，再畫圖。對照 axis=0 和 axis=1 的形狀，使用 [:,None] 解釋逐列廣播。標註資料來源與是否為練習 fixture。

## 常見坑

不要先看圖再决定偷偷刪除不喜歡的點；清洗規則必須可重現。pandas 索引對齊可能產生意外 NaN。

## 自測清單

- [ ] `G3.11` 能用 numpy 完成向量化運算與廣播，避免顯式 for 循環。證據方式：`self`。
- [ ] `G3.12` 能用 pandas 完成載入/篩選/分組聚合。證據方式：`self`。
- [ ] `G3.13` 能用 matplotlib 畫出能說明問題的圖（並有軸標籤與標題）。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html)。
