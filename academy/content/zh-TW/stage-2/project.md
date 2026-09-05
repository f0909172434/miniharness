# 專案：資料看板

> 對應 Goal：`G2.20` ｜ 練習預估 3 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G2.11, G2.18, G2.19

## 為什麼學這個

串起網路、資料與展示，讓別人能看到可追溯的結果。

## 概念

做一個 GitHub 公開儲存庫資料看板：由指定 repo API 取得名稱、開放 issue 數與 updated_at，驗證 schema，將擷取時間和來源 URL 一起存入 SQLite，再輸出 Markdown 表格。先實作離線 fixture 模式，再加入公開 HTTP；不需要帳號、金鑰或額外網頁框架。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```bash
# 你要交付的 CLI 契約
python3 repoboard.py --fixture fixtures/repo.json --db report.sqlite
python3 repoboard.py --repo python/cpython --db report.sqlite
python3 repoboard.py --db report.sqlite --report report.md
```

### 預期結果

fixture 固定有 3 個 open issues 時，表格應显示 3 並標示 fixture。真實請求必須標示實際擷取時間；離線數據不可假稱即時。

## 練習與驗收

交付來源模組、純清洗函式、參數化 SQL、報告產生器、fixture 和至少 5 個測試。涵蓋缺欄、非 JSON、HTTP 失敗、重複擷取策略與空資料庫。README 用一個成功和一個失敗例子說明完整路徑，附離線可重現命令。

## 常見坑

open_issues_count 包含 GitHub PR，不能直接稱作「未修 bug 數」。HTML 展示需 escape 外部文字；資料值本身也需要定義，漂亮圖表無法修正錯誤語意。

## 自測清單

- [ ] `G2.20` 完成「呼叫公開 API → 清洗 → 儲存 → 呈現」的小專案（含測試）。證據方式：`project`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.github.com/en/rest/repos/repos#get-a-repository)。
