# ROADMAP

> 專案層面的規劃與漏洞清單。課程層面的「洞」用
> `python3 tools/academy.py gaps` 隨時掃描；本文件記錄內容與工程兩條線的計畫。
> 完成一項就把 `[ ]` 改成 `[x]`。

## P0 · 已完成（v0.2 基座）

- [x] MiniHarness 核心：loop / protocol / tools / context / eval（30 測試）
- [x] 動手營：8 步 + 檢查器 + 參考實現（solutions 8/8 咬合）
- [x] 從 0 造腦：RuleBrain / NgramBrain / PolicyBrain 對比 demo
- [x] Academy 基座：manifest（6 階段 / 38 模塊 / 110 Goal）+ academy.py 引擎
- [x] 結構檢查固化為測試（tests/test_academy.py，9 條）

## P1 · 內容主線（按階段解鎖，每課遵循 content/_TEMPLATE.md）

- [ ] Stage 0 全部正文（3 課，s0-terminal 已完成）
- [ ] Stage 1 全部正文（7 模塊）
- [ ] Stage 2 全部正文（8 模塊）
- [ ] Stage 3 全部正文（6 模塊，數學按「解釋 ML 現象」裁剪）
- [ ] Stage 4 全部正文（7 模塊，含迷你 Transformer 實作課）
- [ ] Stage 5 補齊除 harness 外的正文（harness 已 ready）
- [ ] 每個 `build` 類 Goal 配一份「驗收清單」或自動檢查器

## P2 · 多語言

- [ ] en：階段/模組正文翻譯（當前 en 覆蓋 0/2 ready，見 `academy.py i18n`）
- [ ] en：Goal 語句逐條翻譯（機制：goal 增加 `statement_en` 欄位 + i18n 報告）
- [ ] 評估第三語言（zh-CN 或 ja）需求後再擴 `locales`

## P3 · 工具與工程

- [x] 學習地圖網頁版 → 已以 `site/`（React + Vite 單頁）落地：循環機器 + 目標星圖 + 工序單
- [ ] `academy.py quiz`：為 `know` 類 Goal 提供自測題庫（JSON 格式）
- [ ] `academy.py verify`：聚合所有 `evidence=checker` 的 Goal，一鍵跑驗收
- [ ] 進度文件可選雲同步（導出/導入 JSON 即可，不引入服務依賴）

## P4 · 社群

- [ ] 貢獻指南（內容/翻譯/代碼三條 PR 路徑）
- [ ] 學習者案例收集（完成的 G3.19/G4.14/G5.12 作品展示）
- [ ] 導師手冊（如何用 gaps/exit 給學員做階段評審）

## 維護紀律

- 改 `manifest.json` 必跑 `validate` + `pytest`（結構測試會攔住壞引用與依賴環）；
- 新增模塊必須同時給出 goals 與 status；標 `ready` 必須先有正文；
- 內容與代碼衝突時，以 manifest 為準修正另一方——它是唯一事實源。
