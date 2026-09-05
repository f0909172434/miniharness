# 作業與驗收契約

先寫自己的版本，再看 `academy/examples/reference/`。本目錄的 `.py` 作業由 Git 忽略。檢查會執行你自己提供的 Python，請勿把不明來源程式當作業執行。

| Goal | 檔案與介面 | 自動驗收範圍 |
|---|---|---|
|G1.6|`wordcount.py`: `word_counts(text)` → list of `(word,count)`|小寫、空白切詞、不去標點；次數遞減、同分字典序；空輸入與空白|
|G1.21|`test_cli.py`: 至少 5 個 `unittest.TestCase` 測例|收集數至少 5，全部執行通過；測試內容仍需人工審閱|
|G2.6|`numeric.py`: `clamp(value,low,high)`；`test_numeric.py` 的 `test_normal/test_boundary/test_error`|實際執行三類 pytest；題目契約與故障注入另按教材核對|
|G3.17|`metrics.py`: `binary_metrics(truth,pred)` → precision/recall/f1 dict；`split_folds(n,k)` → `(train_indices,test_indices)` 列表|二元指標、零分母採 0、長度錯誤、每個樣本驗證一次、折間無洩漏；不自動判定真實任務的指標是否合適|
|G5.3|`tutorial/my_harness.py`|既有八步完整行為檢查；失敗回傳非零退出碼|

`split_folds` 限 `2 <= k <= n`，每折訓練與驗證都非空、互斥且聯集是 `range(n)`。這個基本索引練習不是 stratification 實作；實際分類資料請用教材中的 StratifiedKFold。

```bash
python3 tools/academy.py verify --goal G1.6
python3 tools/academy.py verify
python3 tools/academy.py verify --reference
```

最後一條只檢查教學參考版本是否仍正確，**不會使用、建立或標記你的作業**。缺少作業或檢查失敗都會讓整體驗收回傳非零退出碼。通過後仍需人工確認能解釋程式，再自行 `done G...`。
