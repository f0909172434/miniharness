# MiniHarness 🔧

**用 Python 理解並實作 agent harness：離線示範、概念文檔與八步動手營。**

先從 [互動循環機器](https://f0909172434.github.io/miniharness/#machine)、[終端機入門](academy/content/zh-TW/stage-0/terminal-first-steps.md) 或 [八步動手營](tutorial/README.md) 開始。

**內容狀態（2026-09）：** MiniAcademy 規劃了 6 階段、38 個模組、110 個學習目標；目前 2 個模組標為 ready、36 個為 draft。現有 ready 教材為繁體中文，英文正文尚未提供。Python harness 執行時僅使用標準庫；測試與網站另有開發依賴。

> 上層是 **MiniAcademy**：6 階段 / 38 模塊 / 110 條可驗證 Goal 的課程地圖
> （[academy/](academy/README.md)），配 `tools/academy.py` 提供規劃、
> 進度與漏洞掃描，多語言覆蓋一條命令可查；
> 下層是 **MiniHarness**：其中第 5 階段的核心教材——用 9 個模塊、約 1600 行
> 手搓一個 Agent Harness，配 10 章概念文檔、8 步動手營與 4 個 demo。
> 倉庫定位：**智能在模型，工程在 harness，路線在 academy。**

本項目受 [minimind](https://github.com/jingyaogong/minimind)（造大腦）啟發，
教的是它的對偶問題：**造馬具**。章節組織參考了微軟
[AI for Beginners](https://github.com/microsoft/AI-For-Beginners) 的課程化風格；
設計思想上向 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)
（"the 100-line agent"）與 Anthropic
[Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) 致敬。

---

## 學院：六階段地圖（academy/）

以下為課程規劃與估計時數，完整路線仍在編寫。

| 階段 | 主題 | 規劃目標 | 預估小時 |
| --- | --- | --- | --- |
| 0 | 零基礎起步 | 終端機/檔案/第一支程式不慌張 | 9 |
| 1 | Python 程式核心 | 獨立交付命令行工具 | 36 |
| 2 | 工程與系統基礎 | 測試、打包、協作、呼叫 API | 40 |
| 3 | 數學與機器學習 | 端到端 ML 流水線 | 60 |
| 4 | 深度學習與 LLM | 親手訓練自己的小模型 | 80 |
| 5 | Agent 工程與研究方法 | MiniHarness 全套 + 復現論文 + 公開作品 | 80 |

```bash
python3 tools/academy.py map      # 地圖 + 進度
python3 tools/academy.py next     # 現在該學什麼（嚴格按階段推進）
python3 tools/academy.py gaps     # 四面漏洞掃描：結構/內容/翻譯/學習
python3 tools/academy.py i18n     # 多語言覆蓋報告
```

每條 Goal 都標注層級（know/do/build）與驗證方式；manifest 結構由測試守護，
**「哪裡有洞」永遠是一條命令的事**（詳見 [academy/README.md](academy/README.md)
與 [ROADMAP.md](ROADMAP.md)）。

## 前端 · 手稿成機（site/）

> 在線體驗：**https://f0909172434.github.io/miniharness/**

一個 React + Vite 的單頁站點，把課程做成一件可玩的東西：

- **首屏**：一頁幾乎空白的手稿，命題自己書寫——「智能在模型，工程在 harness。」；
- **章貳 · 循環機器（核心裝置）**：教程算法的 JS 移植真實運行——單步/自動/重置、
  「看模型 / 看工程」視角切換、故障注入拉桿（壞 JSON 進來，看循環自我修復）；
- **章叁 · 目標星圖**：110 條 Goal 按 manifest 的前置依賴結成螺旋星圖，
  懸停/釘選/雙擊標記達成（存本機）；
- **章肆 · 工序單**：動手營八步逐項打勾，勾滿即 G5.3 的形。

```bash
cd site && npm install && npm run build && npm run preview   # 本地查看生產構建
```

無障礙與降級：鍵盤可駕駛機器（Space 單步 / R 重置 / F 故障），星圖支援方向鍵巡覽，
`prefers-reduced-motion` 下全部繪製與運轉動畫靜止為終態。

## 30 秒上手（不需要任何 API Key）

```bash
git clone https://github.com/f0909172434/miniharness.git && cd miniharness

# 路線 A（推薦入口）：動手營——8 步親手寫出自己的 harness
cat tutorial/README.md
python3 tutorial/check.py          # 建議先看看你現在的進度（0/8）

# 路線 B：先跑現成的，再回頭拆
python3 demos/demo_mock.py        # 離線 demo：MockLLM 扮演大腦，完整跑一遍 harness
python3 demos/demo_from_zero.py   # 從 0 造腦：自訓語言模型 0%、手寫規則 100%、模仿學習 100%
python3 -m pytest                 # 30 個測試釘住每個模塊的行為
```

想被帶著一步一步做？直接進 [tutorial/](tutorial/README.md)：
從空文件開始，8 個步驟（循環 → 協議 → 工具 → 安全閘 → 自愈 → 上下文 →
評測 → 🎓畢業考）寫出你自己的 `my_harness.py`，每步都有檢查器驗收。

要求：Python 3.9+，**零第三方依賴**（stdlib 就夠；`pytest` 僅開發時需要）。

真實 demo 的實際輸出（`NO_COLOR=1 python3 demos/demo_mock.py`）：

```text
工作區：/var/folders/.../miniharness-demo-fge77uvn
大腦：MockLLM（腳本化，離線）

┌─ Step 1 / 10
│ 模型：Thought: 收到任務。先把計劃寫進 todo，防止漏步驟。
│ ⚙ todo {'action': 'write', 'content': '[ ] 查看目錄結構\n[ ] 搜索 TODO 標記\n[ ] 統計並寫入 REPORT.md'}
│ ↳ OK：todo 已更新。當前內容：……
┌─ Step 2 / 10
│ 模型：Thought: 先遞歸看一下工作區裡有什麼。
│ ⚙ list_dir {'path': '.', 'recursive': True}
│ ↳ .todo.md / README.md / app/core.py / app/utils.py / notes.txt / scripts/pipeline.py
┌─ Step 3 / 10
│ 模型：Thought: 結構清楚了。用 grep 在所有 .py 文件裡搜 TODO 標記。
│ ⚙ run_bash {'command': 'grep -rn "TODO" --include=*.py .'}
│ ↳ ./app/core.py:5:    # TODO: 加入邊界值校驗 …（共 4 處）
┌─ Step 4 / 10
│ ⚙ write_file {'path': 'REPORT.md', 'content': '# TODO 報告\n\n- app/core.py（2 處）：…'}
│ ↳ OK：已寫入 REPORT.md（115 字符）
┌─ Step 5 / 10  ⚙ todo {'action': 'show'}
┌─ Step 6 / 10
│ 模型：Thought: 三步計劃全部完成，可以收尾了。
└─ ✓ 完成（6 步，5 次工具調用）

── 產物 REPORT.md ──
# TODO 報告
- app/core.py（2 處）：加入邊界值校驗；參數順序容易搞混，改成關鍵字參數
- app/utils.py（1 處）：處理中文與空格
- scripts/pipeline.py（1 處）：接入日誌
```

（完整未刪節輸出見 `demos/`，誘餌文件 `notes.txt` 被正確排除。）

## 四個 Demo

| Demo | 命令 | 說明 |
| --- | --- | --- |
| 離線循環 | `python3 demos/demo_mock.py` | MockLLM 扮演大腦，看 harness 機制本身 |
| 從 0 造腦 | `python3 demos/demo_from_zero.py` | 沒有模型也能有 agent：三種自製大腦同場對比（[09 章](docs/09-from-zero.md)） |
| 真模型 REPL | `python3 demos/demo_cli.py` | 交互式命令行 agent，把它當工具用 |
| 迷你評測 | `python3 demos/demo_eval.py [--real]` | 3 個任務的評測集，看通過率與步數 |

接真實模型（任意 OpenAI 兼容端點均可——OpenAI / DeepSeek / 智譜 / Moonshot / Ollama）：

```bash
export OPENAI_API_KEY=sk-...
# 可選：export MINIHARNESS_BASE_URL=https://api.deepseek.com/v1
# 可選：export MINIHARNESS_MODEL=deepseek-chat
python3 demos/demo_cli.py
```

## 網站互動驗證

循環機器的自動與單步操作共用播放控制。暫停會在目前一拍結束後停止；重置會取消舊的演出，故障開關則從新的一輪開始。系統設定減少動態時，首次進入畫面不會自動播放。

2026-09 的瀏覽器回歸檢查涵蓋：開始後暫停、等待後步數不變、故障第一拍顯示解析錯誤、自動恢復完成報告，以及390px版面的教材連結與自行記錄。

## 課程地圖（docs/）

| 章 | 主題 | 對應代碼 | 核心問題 |
| --- | --- | --- | --- |
| [00 總覽](docs/00-overview.md) | harness 是什麼 | —— | 智能在模型，工程在 harness |
| [01 Agent 循環](docs/01-agent-loop.md) | while 循環 | `loop.py`（149 行） | agent 的心臟為什麼這麼小？ |
| [02 協議](docs/02-protocol.md) | 工具調用格式 | `protocol.py` | 模型怎麼「說」它要調工具？ |
| [03 工具](docs/03-tools.md) | 工具設計 | `tools.py` | 什麼是好工具？ |
| [04 上下文工程](docs/04-context.md) | 歷史裁剪 | `context.py` | 歷史越滾越長怎麼辦？ |
| [05 記憶與計劃](docs/05-memory.md) | todo 模式 | `todo` 工具 | 為什麼都在寫 todo 文件？ |
| [06 安全與沙箱](docs/06-sandbox.md) | 攻與防 | 安全閘 | agent 亂來怎麼辦？ |
| [07 迷你評測](docs/07-eval.md) | 評測集 | `eval.py` | 怎麼證明 harness 有用？ |
| [08 路線圖](docs/08-roadmap.md) | 生產化 | —— | 從這裡到真實系統差什麼？ |
| [09 從 0 造腦](docs/09-from-zero.md) | 自製大腦 | `brains.py` | 沒有模型，也能有 agent 嗎？ |

建議路徑：先跑 demo → 讀 01/02 章 + 對照源碼 → 讀完其餘章節 →
做 [07 章](docs/07-eval.md)的「畢業作業」（給評測集加一個自己的任務）。

## 目錄結構

```
miniharness/
├── academy/              # ★ MiniAcademy：6 階段課程地圖（manifest + 引擎 + 正文）
│   ├── manifest.json     #   唯一事實源：38 模塊 / 110 條 Goal / 前置依賴圖
│   ├── content/          #   各語言正文（zh-TW 完整，en 骨架）
│   └── README.md         #   目標體系 / 漏洞掃描 / 貢獻流程
├── tools/academy.py      # map / next / gaps / i18n / validate / 進度管理
├── tutorial/             # ★ 動手營：8 步親手造 harness（含逐步檢查器與參考實現）
│   ├── check.py          #   python3 tutorial/check.py —— 進度總覽 / 逐步驗收
│   ├── steps/            #   9 份步驟文檔（每步：目標 → 規格 → 提示 → 常見坑）
│   └── solutions/        #   完整參考實現（卡住 30 分鐘才許看）
├── miniharness/          # 核心包（9 個模塊，約 1600 行，零依賴）
│   ├── protocol.py       #   工具調用協議：解析 / 格式化 / 系統提示詞
│   ├── llm.py            #   大腦介面：MockLLM + OpenAI 兼容適配器（純 urllib）
│   ├── tools.py          #   工具註冊表 + 5 個內置工具 + 安全閘
│   ├── context.py        #   上下文預算與歷史裁剪
│   ├── loop.py           #   AgentLoop：整個 harness 的心臟
│   ├── brains.py         #   從 0 造腦：RuleBrain / NgramBrain / PolicyBrain（09 章）
│   ├── eval.py           #   迷你評測 runner
│   └── tasks.py          #   3 個內置評測任務 + 離線 mock 劇本
├── demos/                # mock（離線）/ from_zero（造腦）/ cli（真模型）/ eval（評測）
├── docs/                 # 10 章概念文檔（第 5 階段 harness 模組的教材）
├── tests/                # 40 個測試（核心 30 + 課程結構 10）
├── ROADMAP.md            # 專案層規劃：內容/多語言/工具/社群四條線
└── pyproject.toml
```

## 設計原則

1. **可讀 > 功能**：每個模塊一屏能看完核心邏輯；註釋講「為什麼」而不是「是什麼」；
2. **零依賴**：真實 API 調用就是一個 HTTP POST，用 stdlib 親手寫一遍；
3. **錯誤是第一公民**：一切錯誤以可讀文本喂回模型（self-repair），永不拋向天空；
4. **可互換的大腦**：MockLLM ↔ 自訓小模型（09 章）↔ 真實 API 一行切換——離線教學與真實實驗共用同一套機制；
5. **誠實的安全敘事**：[06 章](docs/06-sandbox.md)同時講防線與繞法，不假裝字符串過濾等於沙箱。

## 相關項目對照

| 項目 | 教什麼 | 與本項目的關係 |
| --- | --- | --- |
| [minimind](https://github.com/jingyaogong/minimind) | 從零**訓練**小型 LLM | 對偶問題：它造大腦，MiniHarness 造馬具 |
| [AI for Beginners](https://github.com/microsoft/AI-For-Beginners) | AI 通識課程 | 章節組織的參照 |
| [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) | 生產級極簡 agent | 進階閱讀：讀完本項目後它的源碼會非常好懂 |
| [smolagents](https://github.com/huggingface/smolagents) | 代碼即行動流派 | [02 章](docs/02-protocol.md)的流派對比 |
| [OpenHands](https://github.com/All-Hands-AI/OpenHands) | 完整平臺 | [08 章](docs/08-roadmap.md)的生產化參照 |

## FAQ

**Q：這和 LangChain / Agents SDK 有什麼區別？**
框架幫你「跳過」這層抽象；MiniHarness 幫你「看懂」它——甚至連模型都繞開了
（[09 章](docs/09-from-zero.md)），純手搓。讀完之後你用任何框架，
都知道 prompt 球放在哪、錢花在哪、會在哪裡碎。

**Q：能直接用在生產嗎？**
不能，也不打算。[08 章](docs/08-roadmap.md)列出了到生產級的差距清單與補齊順序。

**Q：必須有 API Key 嗎？**
不需要。所有 demo 默認離線；[09 章](docs/09-from-zero.md)更進一步——
連模型都自己造（手寫規則、自訓語言模型、模仿學習策略）。
接真模型只是換一行構造函數。

## 參與

歡迎 PR：新增評測任務（最歡迎）、新增一章、修錯字。
問題請開 issue，附上 `NO_COLOR=1` 的完整輸出。

## License

[MIT](LICENSE) © 2026 MiniHarness contributors
