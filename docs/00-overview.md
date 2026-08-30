# 00 · 總覽：harness 到底是什麼

> 本課程假設你已經會調用一次 LLM API。現在我們回答下一個問題：
> **在「模型」之外，還需要哪些工程件，才能把一次 API 調用變成一個能幹活的 agent？**

## 一句話定義

**Harness（馬具/腳手架）= 套在模型外面、讓它能持續幹活的工程系統。**

模型本身只會一件事：讀入一串文本，吐出一段文本。它沒有手（不能執行）、
沒有記憶（對話外全忘）、沒有終止條件（不知道任務何時算完成）。把
「讀文本吐文本」變成「查目錄、改代碼、跑測試、交付報告」的中間那一整層，
就是 harness。你可能在這些名字下見過它：agent runtime、agent scaffold、
agent loop、coding agent 的 "engine"。

## 模型 vs harness 的分工

| 職責 | 歸誰 | 在 MiniHarness 裡 |
| --- | --- | --- |
| 判斷下一步做什麼 | 模型 | 任意 OpenAI 兼容端點 / MockLLM |
| 說「我要調工具」的格式 | 協議約定 | `protocol.py` |
| 真的去執行工具 | harness | `tools.py` |
| 決定模型能看見什麼歷史 | harness | `context.py` |
| 防止越界與失控 | harness | `tools.py` 安全閘 + `loop.py` 步數上限 |
| 判斷「做完了沒、做對了沒」 | harness（評測） | `eval.py` + `tasks.py` |

記住這張表，你就理解了這個領域最重要的心智模型：
**智能在模型，工程在 harness。** 換模型不改 harness，換 harness 不改模型——
MiniHarness 的 `MockLLM` 與 `OpenAICompatLLM` 可直接互換，就是這種解耦的證明。

## 全景圖

```
                    ┌────────────────────────────────────┐
                    │            AgentLoop               │
                    │            (loop.py)               │
                    │                                    │
   任務 ──────────▶ │  history = [system, task]          │
                    │  ┌──────────────────────────────┐  │
                    │  │ 1. LLM.generate(history)     │◀──┼──── llm.py
                    │  │ 2. parse_response(reply)     │  │    (Mock / 真實 API)
                    │  │    ├─ 最終回答 → 返回        │  │
                    │  │    └─ 工具調用 ↓             │  │
                    │  │ 3. ToolRegistry.run_tool()   │──┼──── tools.py
                    │  │ 4. 觀察寫回 history，重複     │  │    (含路徑守衛/白名單)
                    │  └──────────────────────────────┘  │
                    │   ▲ history 太長？                 │
                    │   └── ContextManager.fit() ────────┼──── context.py
                    └────────────────────────────────────┘
                              │
                    run_eval(tasks) ◀──────────────────────── eval.py + tasks.py
```

## 課程地圖

| 章 | 主題 | 對應代碼 | 你將搞懂的問題 |
| --- | --- | --- | --- |
| [01](01-agent-loop.md) | Agent 循環 | `loop.py` | agent 的「心臟」為什麼只是一個 while？ |
| [02](02-protocol.md) | 工具調用協議 | `protocol.py` | 模型怎麼「說」它要調工具？ |
| [03](03-tools.md) | 工具設計 | `tools.py` | 什麼樣的工具才算好工具？ |
| [04](04-context.md) | 上下文工程 | `context.py` | 歷史越滾越長怎麼辦？ |
| [05](05-memory.md) | 記憶與計劃 | `todo` 工具 | 為什麼頂級 agent 都在寫 todo 文件？ |
| [06](06-sandbox.md) | 安全與沙箱 | `tools.py` 安全閘 | agent 亂來怎麼辦？ |
| [07](07-eval.md) | 迷你評測 | `eval.py` `tasks.py` | 怎麼證明你的 harness 有用？ |
| [08](08-roadmap.md) | 進階路線圖 | —— | 從 600 行到生產級，差在哪？ |
| [09](09-from-zero.md) | 從 0 造腦 | `brains.py` | 沒有模型，也能有 agent 嗎？ |

## 怎麼學

**本倉庫現在是一條完整的「從零計算機基礎到 AI 研究員」路線**
（[academy/](../academy/README.md)：6 階段 / 110 條 Goal）。零基礎請從
`python3 tools/academy.py map` 開始看地圖；已經會寫程式的讀者，
本頁之下的兩條路線任選：

- **路線 A · 動手營（推薦入口）**：打開 [../tutorial/README.md](../tutorial/README.md)，
  跟著 8 個步驟從空文件親手寫出自己的 harness，每步有檢查器驗收；
  寫完再讀本章節，等於複習自己的作品；
- **路線 B · 先看成品再拆**：按下面的順序讀：

1. 先跑 `python3 demos/demo_mock.py`——零 API Key，看一遍完整循環；
2. 對照 [01 章](01-agent-loop.md)讀 `loop.py`（全文不到 170 行，含註釋）；
3. 跑 `python3 -m pytest` 看 30 個測試怎麼釘住每個模塊的行為；
4. 有 API Key 的話，`python3 demos/demo_cli.py` 換上真模型，把它當工具用；
5. 沒有 API Key？跑 `python3 demos/demo_from_zero.py`，跟著
   [09 章](09-from-zero.md)手搓三種大腦——連模型都可以是自己的；
6. 按 [07 章](07-eval.md)加一個自己的評測任務——這是最好的畢業作業。

## 延伸閱讀與參考項目

MiniHarness 站在這些項目的肩膀上（按對本課程的影響排序）：

- [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) —— SWE-agent 團隊的
  "100 行 agent"，證明極簡 harness 就能解真實 GitHub issue。本課程的整體思路與它最接近；
- [SWE-agent](https://github.com/SWE-agent/SWE-agent)（論文
  [arXiv:2405.15793](https://arxiv.org/abs/2405.15793)，NeurIPS 2024）——
  提出 Agent-Computer Interface（ACI）概念：工具介面設計和模型一樣重要；
- [smolagents](https://github.com/huggingface/smolagents) —— Hugging Face 的極簡
  agent 庫，「代碼即行動」流派的代表；
- [minimind](https://github.com/jingyaogong/minimind) —— 從零訓練小型 LLM 的教學項目。
  它教「造大腦」，MiniHarness 教「造馬具」，剛好互補；
- [AI for Beginners](https://github.com/microsoft/AI-For-Beginners) 與
  [Generative AI for Beginners](https://github.com/microsoft/generative-ai-for-beginners)
  —— 微軟的課程化開源項目，本課程的章節組織參考了它們；
- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
  （Anthropic, 2024）—— agent 設計模式的第一手總結；
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  （Anthropic, 2025）—— 第 04 章的理論背景；
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
  （Yao et al., 2022）—— 「思考→行動→觀察」循環的開山論文；
- [SWE-bench](https://www.swebench.com/)（[arXiv:2310.06770](https://arxiv.org/abs/2310.06770)）
  與 [Terminal-Bench](https://github.com/laude-institute/terminal-bench) ——
  第 07 章聊的「怎麼給 agent 考試」的工業級答案。
