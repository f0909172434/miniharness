# 參與 MiniHarness

先在乾淨環境跑測試與 `tools/academy.py gaps`，讓修改對應一個具體缺口。核心執行時維持 Python 標準庫；ML 課程與前端環境分開。

| 修改類型 | 需要一起交付 |
|---|---|
|教材|對應 Goal、可重跑例子、預期結果、故障例、作業驗收、自測清單；在 manifest 登記正文|
|翻譯|保留 Goal ID、數字、程式契約和證據限制；逐課補內容後再更新覆蓋，不能拿英文標題當英文教材|
|程式|問題與行為差異、所屬教材章節、有意義的正常/失敗測試；保留路徑與網路防線|

```bash
python3 -m pytest -q
python3 tools/academy.py validate
python3 tools/academy.py verify --reference
python3 demos/demo_mock.py
python3 demos/demo_from_zero.py
NO_COLOR=1 python3 demos/demo_eval.py --quiet
npm ci --prefix site
npm run build --prefix site
```

ML 範例另依 `academy/requirements-ml.txt` 安裝後執行；不應要求只跑 harness 的使用者安裝 PyTorch。PR 說明使用的環境、實際結果與未測範圍；圖片或資料需保留來源與授權。不要提交學習者的私人作業或虛構外部試用結果。
