# MiniAcademy —— 從零計算機基礎到 AI 研究員

**這不是又一個課程列表，而是一台「教學工程機器」**：
一個 JSON 清單（`manifest.json`）定義了 6 個階段、38 個模塊、110 條可驗證的
Goal；`tools/academy.py` 在其上提供地圖、規劃、漏洞掃描與多語言覆蓋報告；
pytest 把清單的結構約束固化為 CI 測試。**課程內容會慢慢寫，但地圖、
目標與找漏洞的機制今天就是完備的。**

## 六個階段

| 階段 | 主題 | 產出能力 | 小時 |
| --- | --- | --- | --- |
| 0 | 零基礎起步 | 終端機/檔案/第一支程式不慌張 | 9 |
| 1 | Python 程式核心 | 獨立交付命令行工具 | 36 |
| 2 | 工程與系統基礎 | 測試、打包、協作、呼叫 API | 40 |
| 3 | 數學與機器學習 | 端到端 ML 流水線 | 60 |
| 4 | 深度學習與 LLM | 親手訓練自己的小模型 | 80 |
| 5 | Agent 工程與研究方法 | **MiniHarness 全套 + 復現論文 + 公開作品** | 80 |

設計原則：**每條 Goal 都可驗證**（`know` 能講清 / `do` 能做出 /
`build` 有成品），每階段有明確的 exit 條件；數學按「解釋 ML 現象所需」
裁剪，不做題海；第 5 階段的 Agent Harness 模組直接復用本倉庫的
docs/00-09 與動手營——你正在讀的這個倉庫就是教材本身。

## 五條命令

```bash
python3 tools/academy.py map          # 學習地圖 + 你的進度
python3 tools/academy.py next         # 現在該學什麼（嚴格按階段推進）
python3 tools/academy.py done G0.1    # 達成一條 Goal 就記錄一條
python3 tools/academy.py gaps         # 漏洞掃描（見下）
python3 tools/academy.py i18n         # 多語言覆蓋報告
```

進度存在 `academy/progress.json`（已被 git 忽略）。

## 漏洞掃描：gaps 的四個探測面

`gaps` 是本系統的核心承諾——**隨時一條命令回答「哪裡有洞」**：

1. **結構洞**：manifest 的重複 ID、懸空引用、依賴環、前置階段錯序
   （同一套檢查也被 `tests/test_academy.py` 固化，CI 會跑）；
2. **內容洞**：哪些模塊有 Goal 卻還沒有正文；
3. **翻譯洞**：各語言的標題/正文覆蓋率；
4. **學習洞**：基於你的 `progress.json`——哪些模塊可學、哪些被前置擋住、
   還差幾條前置 Goal。

貢獻內容或翻譯之前先跑 `gaps`：它會告訴你最缺什麼。

## 多語言機制

- `manifest.json` 的 `locales` 聲明支援的語言（當前 `zh-TW` 完整、`en` 骨架）；
- 階段/模組標題要求雙語；正文按
  `academy/content/<locale>/stage-<N>/*.md` 存放；
- `i18n` 命令報告每種語言的覆蓋率；新增語言＝manifest 加代碼 →
  補標題 → 放正文 → 跑 `i18n` 驗證；
- Goal 語句目前以預設語言書寫，逐條翻譯列於 `ROADMAP.md` P2。

## 如何貢獻一課

1. 跑 `gaps`，挑一個「內容洞」模塊（或在 issue 裡提議新模塊）；
2. 以 `academy/content/_TEMPLATE.md` 為範本撰寫：正文必須服務於
   manifest 裡明確列出的 Goal，結尾必須有逐條可勾的自測清單；
3. 在 manifest 對應模組的 `content` 登記路徑；若模塊因此齊備，
   把 `status` 改為 `ready`；
4. 跑 `python3 tools/academy.py validate` 與 `pytest`，全綠後提 PR。

## 與倉庫其他部分的關係

- `miniharness/` 包、`demos/`、`docs/`：第 5 階段「Agent Harness」模組的教材；
- `tutorial/`（動手營）：同一模組的實作線，對應 Goal `G5.3`（有自動檢查器）；
- `tests/`：40 個測試，其中 9 個守護課程結構本身。
