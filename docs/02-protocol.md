# 02 · 協議：模型怎麼「說」它要調用工具

> 對應代碼：`miniharness/protocol.py`。這是模型與 harness 之間唯一的「合同」。

## 問題：模型只會吐文本，harness 只認函數

模型能做的只有「生成下一段文本」。它說「我想列出目錄」沒有用——
harness 需要的是一次**可機讀、可執行、可校驗**的調用請求。
怎麼把自然語言變成結構化請求？業界有三個流派：

| 流派 | 做法 | 代表 | 優點 | 缺點 |
| --- | --- | --- | --- | --- |
| 原生 function calling | API 層提供 `tools` 參數，返回結構化 `tool_calls` 欄位 | OpenAI/Anthropic 官方 API | 穩、可校驗、支持並行 | 綁定 API 特性；黑盒 |
| 文本協議 | 約定模型在文本裡輸出特定格式，harness 解析 | 本項目、早期 ReAct | 100% 透明；任何端點都能跑 | 解析可能碎（要自愈） |
| 代碼即行動 | 模型直接寫 Python，harness 執行代碼 | smolagents CodeAgent | 表達力最強 | 需要真沙箱，風險最高 |

MiniHarness 選文本協議，是**教學取舍**：每一輪「模型到底說了什麼」
都原樣打印在終端裡，解析、報錯、自愈全部可見。讀懂它之後，
function calling 只是換了個「更結實的信封」，概念完全平移。

## MiniHarness 的合同（全文就兩條）

1. 想調工具：輸出一個 ` ```toolcall ` 代碼塊，內容是 JSON：

   ````
   Thought: 先看一下目錄結構。
   ```toolcall
   {"tool": "list_dir", "args": {"path": ".", "recursive": true}}
   ```
   ````

2. 不想調工具（任務完成）：整段回覆就是給用戶的最終回答。

對應的解析器只有一個正則 + 一個 `json.loads`：

```python
_FENCE_RE = re.compile(r"```toolcall\s*(.*?)\s*```", re.DOTALL)
```

設計細節，每條都有理由：

- **每輪至多一個工具調用**。多個調用會引入「並行執行順序」的複雜度，
  教學階段先砍掉（08 章講怎麼加回來）；
- **只認第一個代碼塊**，其餘忽略——系統提示詞已經約定了，違約也安全；
- **Thought 在代碼塊外面**。強迫模型「先想後做」，觀察 demo 輸出你會發現
  這大幅提高工具選擇的質量（同樣是 CoT 的效果）；
- **解析失敗不是異常逃逸，而是一條喂回模型的糾錯消息**
  （`format_parse_error`）。合同裡專門寫了違約後的補救流程。

## 系統提示詞：合同的另一半

`build_system_prompt()` 生成的提示詞包含：你是誰、工作目錄在哪、
工具清單（`tools.catalog()` 自動渲染）、回合規則、違約補救。
注意一個槓桿關係：**想改 agent 的行為習慣，先改提示詞，而不是改模型參數。**
比如你想讓它「每次寫文件前先報備」，在規則 3 裡加一句試試。

## 錯誤是第一公民

`protocol.py` 裡一半的代碼在處理「不對勁」的情況：

| 情況 | 處理 | 為什麼 |
| --- | --- | --- |
| JSON 壞了 | `MalformedToolCall` → 喂回錯誤 | 模型能讀懂錯誤並修正 |
| 缺 `tool` 鍵 / `args` 不是對象 | 同上 | 越具體的錯誤，修正越快 |
| 工具名不存在 | `run_tool` 返回 ERROR 文本 | 讓模型知道有哪些工具可選 |
| 參數缺失/類型錯 | 同上 | 教模型學會讀 schema |
| 路徑越界 | `ToolError` → ERROR 文本 | 安全事件也走同一條反饋通道 |

統一原則：**錯誤以「可讀文本」回到模型面前，而不是異常拋向天空。**
harness 的魯棒性，大半來自這一條。

## 練習

1. 把協議換成「JSON Mode」：要求模型輸出整段 JSON（含 thought 欄位），
   對比兩種協議在真模型下的碎裂率（提示：跑 07 章的評測各 20 次）；
2. 支持一輪多個工具調用：解析所有 toolcall 塊，依次執行、逐條喂回；
3. （進階）接到真實 function calling：把 `parse_response` 換成讀取
   `choices[0].message.tool_calls`，觀察 `loop.py` 幾乎不用改——
   這就是協議層被隔離出來的回報。

## 延伸閱讀

- [OpenAI Function Calling 指南](https://platform.openai.com/docs/guides/function-calling)；
- [Anthropic Tool Use 文檔](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)；
- [smolagents 文檔：Code Agent 為什麼可行](https://huggingface.co/docs/smolagents/index)；
- ReAct 論文第 3 節——最早的「文本協議」設計討論之一。
