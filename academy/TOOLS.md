# 自測、驗收與可攜進度

課程引擎的執行依賴仍是 Python 標準庫；pytest 只供開發與 G2.6 驗收。ML 範例依賴另列，不會被核心工具匯入。

```bash
python3 tools/academy.py quiz --stage 0
python3 tools/academy.py quiz --list
python3 tools/academy.py verify --goal G1.6
python3 tools/academy.py verify
python3 tools/academy.py verify --reference
```

Quiz 有 32 題，覆蓋所有 `know` 目標，答題後顯示原因。可用 `--answers answers.json` 提供 `{ "G0.4": 1, ... }` 的選項檔；缺答或答錯回傳非零。Quiz、verify 都不寫入完成進度。

Verify 只執行五個固定檢查器，不會執行 manifest 任意指令。契約見 [作業說明](submissions/README.md)。預設檢查學習者的檔案；`--reference` 清楚分開參考解。每項超過時間或失敗都影響總退出碼。通過自動檢查後仍要人工評估解釋與測試品質。

## 進度匯出／匯入

```bash
python3 tools/academy.py export my-progress-2026-09.json
python3 tools/academy.py import my-progress-2026-09.json
python3 tools/academy.py show
```

匯出檔包含格式版本、課程版本與 `done` ID；不含程式、成績或個資。你可自行放入雲端資料夾再在另一台匯入。工具不連線、不建帳號。匯入先驗證版本、Goal、重複值與 256 KiB 上限，再與既有標記合併；不會清除原進度。匯出不覆寫既存檔案。

網站勾選與 CLI 進度目前各自保存在瀏覽器及本機檔案。此版本的匯入／匯出用於 CLI，沒有宣稱網站同步或完成驗證。
