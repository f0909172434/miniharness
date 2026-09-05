# AGENTS.md

本倉庫本身是一個 agent harness 教學項目——給 AI 協作者（人類也一樣）的約定：

## 項目公約

- Python 3.9+，**運行時零第三方依賴**（dev 依賴僅 pytest）。新增依賴前先問：
  stdlib 真的做不到嗎？
- 文檔與代碼註釋使用繁體中文；標識符與測試名用英文。
- 每個新功能必須：對應一章文檔（或明確指出歸入哪一章）+ 至少一個測試。
- 代碼風格：模塊頂部 docstring 回答「這層解決什麼問題」；註釋講「為什麼」，
  不講「是什麼」。

## 安全紅線（改 tools.py / llm.py 前必讀）

- 所有文件操作必須經過 `resolve_path` 的越界檢查；
- 子進程一律 `shell=False` + 顯式字面量命令 + `shlex.split` 參數化；
  新增白名單命令要三思（見 docs/06 的「怎麼繞」一節）；
- 對外請求的 URL 必須經 `validate_endpoint` 校驗；
- 一切錯誤降級為可讀文本喂回模型（`run_tool` 永不拋異常）。

## 大腦公約（改 brains.py 前必讀）

- 新大腦必須是 `BaseLLM` 子類，只輸出協議合法文本（toolcall 或最終回答），
  並在 `tests/test_brains.py` 補一條評測斷言；
- `PolicyBrain` 的特徵（`featurize`）必須先剝 `TOOL RESULT` 信封再打標誌，
  否則訓練樣本自相矛盾（踩過的坑，見該函數註釋）；
- `random.Random` 僅用於採樣可復現，禁止用於任何安全相關判斷。

## 驗證

提交前跑：

```bash
python3 -m pytest -q                   # 核心、課程、驗收失敗路徑
python3 tools/academy.py validate      # manifest 結構校驗（改課程必跑）
python3 tools/academy.py verify --reference # 教材自檢，不記錄學習者進度
python3 demos/demo_mock.py             # 離線冒煙測試
python3 demos/demo_from_zero.py        # 三種自製大腦對比（09 章）
python3 demos/demo_eval.py --quiet     # 評測 3/3
```

改動 `academy/manifest.json`（課程唯一事實源）時的紀律：

- 新模塊必須同時給 goals 與 status；標 `ready` 必須先有正文文件；
- 前置 Goal 只能指向同階段或更早階段（測試會攔截跨階段倒序依賴）；
- 新語言：先加 `locales`，再補標題與正文，`academy.py i18n` 查覆蓋；
- 內容與代碼衝突時以 manifest 為準修正另一方。

改動 `tutorial/` 時額外驗證：把 `tutorial/solutions/my_harness_full.py`
複製為 `tutorial/my_harness.py`（用 Write 工具，勿用 shell 複製），
`python3 tutorial/check.py` 必須 8/8 全綠，驗完刪掉該文件——
動手營檢查器與參考實現必須始終互相咬合。

## 倉庫地圖

見 `docs/00-overview.md` 的課程地圖與責任表；改動哪層，就讀對應章節。

## 站點部署（site/ → GitHub Pages）

線上地址：https://f0909172434.github.io/miniharness/。

推送 main 後，由 GitHub Actions 先執行 Python 測試、課程結構驗證、離線示範與網站建置，全部通過才部署 GitHub Pages。PR 只驗證，不部署。不要手動覆寫 gh-pages 分支。

本機建置：`npm ci --prefix site && npm run build --prefix site`（Node 22.12+）。
