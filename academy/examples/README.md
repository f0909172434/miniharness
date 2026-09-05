# 可執行參考例

以 Python 3.12 的獨立 venv 安裝 `academy/requirements-ml.txt`；不需下載模型或使用 API。

- `ml_pipeline.py`：資料切分、training 內交叉驗證、單變因 C 比較及一次 test 評估。
- `tiny_lm.py`：手寫多頭因果注意力、位置 embedding、殘差/LayerNorm、訓練、生成與全量微調。
- `reference/`：五個作業檢查器的教學參考，由 `verify --reference` 自檢。

## 2026-09-05 本機紀錄

核心測試仍不安裝 ML 套件。安裝本目錄的選用環境後，可另執行 `python -m pytest academy/tests -q`，驗證因果遮罩、梯度、短訓練與 context 上限；這組檢查不屬於一般網站 CI。

JSON 原始結果與程式同目錄。環境 Python 3.12.14、scikit-learn 1.9.0、PyTorch 2.14.0、CPU；套件列在 requirements-ml.txt。

ML 範例在 455 筆 training 中選 C=0.1，114 筆 test 的 macro F1 約 0.9716。這是內建小型資料集的一次切分，不是醫療工具或通用模型優越性證據。

TinyLM 有 14,676 個參數、20 個字元。240 步後生成 `read the test.`，training perplexity 從 20.36 降到 1.09；31 個保留 token 的 perplexity 為 2.14。80 步微調後，兩個開發提示的指定句型分數由 0/2 變 1/2，但原保留句 perplexity 惡化到 16.47。此例同時保留任務遷移與遺忘，不能只報改善的一面。詞表包含全部 fixture 的字元；這不是未知詞彙或獨立 benchmark。

先讀逐課作業契約，再自行實作；執行參考程式並不代表完成自己的課程目標。
