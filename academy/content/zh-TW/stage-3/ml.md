# 機器學習核心概念

> 對應 Goal：`G3.14`, `G3.15`, `G3.16`, `G3.17`, `G3.18` ｜ 練習預估 12 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G3.7, G3.10, G3.11

## 為什麼學這個

把模型選擇與最終測試分開，避免數字好看卻不能泛化。

## 概念

監督學習使用標籤（垃圾郵件分類），非監督學習找結構（顧客分群），強化學習透過回饋學策略（控制）。損失定義訓練目標，梯度決定更新方向，學習率決定步長。過擬合常見於訓練好、驗證差；欠擬合則兩者都差。資料洩漏包括在切分前用所有資料學標準化參數。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
X, y = load_iris(return_X_y=True)
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=300))
result = cross_validate(model, X, y, cv=cv, scoring=["precision_macro","recall_macro","f1_macro"])
print(result["test_f1_macro"])
```

### 預期結果

輸出三個折的 macro F1。標準化在每個訓練折內擬合，沒有提前看驗證折。此小資料演示不是模型的通用能力證明。

## 練習與驗收

手算 TP=2、FP=1、FN=2 時 precision=2/3、recall=1/2、F1=4/7。按 academy/submissions/README.md 實作 binary_metrics 與 split_folds，跑 `verify --goal G3.17`。再對不平衡資料比較 accuracy 與 F1；提出正則化/減少複雜度或增加有效訓練資料兩項對策。

## 常見坑

交叉驗證用於開發；若用它反覆挑模型，仍需一次保留測試集。時間序列要按時間切分，不能直接套隨機折。

## 自測清單

- [ ] `G3.14` 能區分監督/非監督/強化學習並各舉一個真實應用。證據方式：`self`。
- [ ] `G3.15` 能解釋損失函數、梯度下降、學習率三者的關係。證據方式：`self`。
- [ ] `G3.16` 能診斷過擬合/欠擬合並提出至少兩種對策。證據方式：`self`。
- [ ] `G3.17` 能用交叉驗證與恰當指標（precision/recall/F1）評估模型。證據方式：`checker`。
- [ ] `G3.18` 能解釋「資料洩漏」並在一個案例中識別它。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://scikit-learn.org/stable/modules/cross_validation.html)。
