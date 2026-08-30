# 08 · 路線圖：從 600 行到生產級 harness

> 你已經有一個能跑、能測、能評的 harness 了。本章是「接下來抄誰的作業」地圖——
> 每一項都指著一個可以讀源碼的開源參照物。

## 差距清單（按投入產出比排序）

### 1. 流式輸出（體驗，1 天）

現在每一步都是「沉默很久 → 刷一下全出來」。把 `generate` 換成
SSE 流式端點，token 到一行印一行。**參照**：OpenAI/Anthropic 的
streaming 文檔；`urllib` 不支持 SSE 就用 `httpx`（這將是項目第一個依賴）。

### 2. 原生 function calling（穩定性，1-2 天）

按 [02 章](02-protocol.md)練習 3 的思路替換協議層。好處是參數
100% 合法 JSON、支持並行調用。**參照**：OpenAI Agents SDK
（[openai-agents-python](https://github.com/openai/openai-agents-python)）的
工具抽象。

### 3. 並行工具與子代理（能力，2-4 天）

- 並行：一輪多個 toolcall，`ThreadPoolExecutor` 同時執行；
- 子代理：給 agent 一個 `spawn_subagent(goal)` 工具，子 agent 有自己的
  歷史與步數預算，只把結論交回——這是 [04 章](04-context.md)「上下文隔離」
  的終極形態。**參照**：Claude Code 的 subagent 機制；
  [OpenHands](https://github.com/All-Hands-AI/OpenHands) 的 delegation。

### 4. 真沙箱（安全，1 週+）

把 `run_bash` 的字符串防線升級為容器：Docker 一次性容器 +
只挂載工作區 + 默認斷網。**參照**：[06 章](06-sandbox.md)的 E2B /
OpenHands runtime。本地開發可用 [microsandbox](https://github.com/microsandbox/microsandbox)。

### 5. 工具生態：MCP（規模，2-3 天）

當你想接入別人寫的工具（瀏覽器、數據庫、Slack……），別再手寫
`Tool` 註冊——實現一個 [MCP](https://modelcontextprotocol.io) 客戶端，
把遠端工具目錄映射進 `ToolRegistry`。你會發現 `ToolRegistry.run_tool`
的介面和 MCP 的 `tools/call` 幾乎同構——**這就是好抽象的證明。**

### 6. 會話持久化與恢復（可靠性，2-3 天）

把 `history` 定期落盤（JSONL），崩潰後從最近檢查點恢復。
長任務（數小時）的 harness 沒有它就是賭博。**參照**：
mini-swe-agent 的 trajectory 保存。

### 7. 更聰明的上下文管理（成本）

按 [04 章](04-context.md)練習 2 實現摘要壓縮；再進一步做
「結構化狀態 + 歷史指針」。**參照**：Anthropic context engineering 博客
與 Claude Code 的 auto-compact。

### 8. 給它一張臉（分發）

TUI（`rich`/`textual`）或 Web UI，把 verbose 日誌變成可折疊的時間線。
**參照**：[gptme](https://github.com/gptme/gptme) 的終端 UI。

## 學習路徑建議

```
讀完 00-07 章，跑通 demo 與測試          ← 你在這裡
  └─ 畢業作業：給評測集加一個任務（07 練習 1）
      └─ 改造 1：流式 + function calling（1、2）
          └─ 改造 2：MCP 接入（5）——開始「用生態」而不是「造輪子」
              └─ 改造 3：容器沙箱 + 持久化（4、6）——可以幹長活了
                  └─ 回頭讀 mini-swe-agent / OpenHands 源碼，你會讀得飞快
```

## 一個誠實的提醒

極簡 harness（包括本項目）在簡單任務上與生產系統差距不大——
mini-swe-agent 用 100 行解真實 GitHub issue 就是證明。
差距出現在：長任務、高併發、多租戶、不可信輸入、需要審計的場景。
**先跑通再變厚**，永遠是對的順序；反過來（先搭平台再造第一個 agent）
是行業裡最常見的死法。

## 致謝

本項目的章節結構參考了 Microsoft
[AI for Beginners](https://github.com/microsoft/AI-For-Beginners) 的課程化組織；
「極簡可讀」的代碼美學致敬 [minimind](https://github.com/jingyaogong/minimind)、
[nanoGPT](https://github.com/karpathy/nanoGPT) 與
[mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)。
歡迎 PR：新增一章、新增一個評測任務、或把你的練習答案變成 `contrib/` 目錄。
