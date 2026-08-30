# 04 · 上下文工程：模型唯一看得見的世界

> 對應代碼：`miniharness/context.py`。參考：
> [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)（Anthropic, 2025）。

## 為什麼上下文是最稀缺資源

Agent 每一輪都要把**整段歷史**重發給模型。歷史由什麼構成？
系統提示詞、任務、模型每次的思考、以及**所有工具的輸出**。
跑得越久，歷史越長，於是兩個後果：

1. **貴**：費用按輸入 token 計，第 N 步的費用 ≈ N × 歷史長度；
2. **稀釋**：長上下文中部的信息利用率下降（"lost in the middle"，
   Liu et al., 2023, [arXiv:2307.03172](https://arxiv.org/abs/2307.03172)），
   模型對第 40 輪之前那個 grep 結果的記憶，遠比你以為的不可靠。

上下文工程的定義因此很樸素：**用有限的窗口，裝對模型最有用的信息。**

## MiniHarness 的三道閘

### 第一道：在創建點截斷（tools.py）

工具輸出進入歷史**之前**就被封頂：`run_bash` 4000 字符、`read_file`
8000 字符。這是最便宜的防線——垃圾根本進不來。

### 第二道：歷史裁剪（context.py 的 `fit()`）

歷史總字符數超過 `max_chars`（默認 24000，約 6-8k token）時：

```
[system] [task] [舊對話…] [舊對話…] [較新對話] [最新對話]
    ↑        ↑        └──── 整對丟棄 ────┘│        │
    └永不丟┘  └永不丟┘                    └─ 保留最近的 ─┘
              丟棄處插入一條佔位說明
```

實現裡有三個值得注意的細節：

- **按 (調用, 觀察) 成對丟棄**。單丟一半會留下「孤兒調用」，
  模型會困惑「我調了這個嗎？結果呢？」——`tests/test_context.py` 釘住了這點；
- **丟棄處留佔位說明**：「更早的對話已被裁剪……」。坦白比假裝好：
  模型知道歷史被裁過，就不會幻想自己記得全部；
- **系統提示詞和最初任務永不丟**。它們是 agent 的「憲法」和「委任狀」。

### 第三道：字符數當 token 代理

`_size()` 只數字符。真 token 數需要分詞器（引入依賴、增加耦合），
而「字符數 ÷ 3~4」對教學足夠精確。這也是一個通用工程直覺：
**度量誤差 25% 但零依賴的方案，常常優於精確但昂貴的方案。**

## 生產系統還做什麼（我們沒做的）

| 策略 | 一句話 | 誰在做 |
| --- | --- | --- |
| 壓縮/摘要（compaction） | 歷史過半時，調 LLM 把舊對話總結成一段 | Claude Code 的 `/compact` |
| 結構化記憶 | 把結論寫進文件（见 05 章），歷史只留指針 | 幾乎所有編碼 agent |
| 工具結果清除 | 保留「我調過 X」這個事實，清掉 X 的輸出 | Anthropic context engineering 博客 |
| 子代理隔離 | 讓一個子 agent 讀完 10 個文件，只返回結論 | Claude Code subagents |

注意共同點：**它們都在對抗同一件事——歷史線性增長。** 裁剪是止血，
壓縮和記憶才是治本。

## 練習

1. 把 `max_chars` 調到 3000 再跑 `demo_mock.py`，親眼看看佔位說明什麼時候出現；
2. 實現摘要壓縮：超預算時不丟棄，而是調 `llm.generate` 把舊對話總結成一段
   「此前進展」消息替換之（MockLLM 下可以返回固定文本）；
3. 給 `RunResult` 統計每步的歷史長度，畫出增長曲線——親眼看到 O(n²) 的費用。

## 延伸閱讀

- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)；
- [Lost in the Middle](https://arxiv.org/abs/2307.03172)；
- Claude Code 的 [compact 機制說明](https://docs.anthropic.com/en/docs/claude-code)（Auto-compact 一節）。
