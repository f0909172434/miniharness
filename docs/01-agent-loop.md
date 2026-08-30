# 01 · Agent 循環：整個 harness 就是一個 while

> 對應代碼：`miniharness/loop.py`（不到 170 行）。先跑 `demos/demo_mock.py` 再讀本章。

## 從一次調用到一個 agent

裸調 API 的樣子：

```python
reply = llm.generate([{"role": "user", "content": "幫我統計 TODO"}])
```

一次調用 = 模型讀一遍、說一遍、結束。它沒看見任何真實世界的结果，
所以「統計」只能是猜。Agent 的本質是把這一次調用變成一個**閉環**：

```python
history = [system_prompt, task]
while True:
    reply = llm(history)             # 1. 模型看著歷史，決定下一步
    if 沒有工具調用(reply):           # 2. 不調工具 => 它認為做完了
        return reply
    result = 執行工具(reply)          # 3. harness 代它動手
    history += [reply, result]       # 4. 觀察寫回歷史，回到 1
```

這就是 ReAct（Yao et al., 2022）講的「推理→行動→觀察」循環，
也是 mini-swe-agent 用 100 行代碼傳達的核心思想：
**agent 的智能來自模型，但「持續幹活的能力」來自這個循環。**

## MiniHarness 的實現要點

打開 `loop.py`，`Agent.run()` 就是上面的 while 加了四件工程必需品：

### 1. 解析失敗的自愈（self-repair）

模型是概率系統，總有一天會輸出壞 JSON。菜鳥實現直接崩潰或跳過；
正確做法是把錯誤**喂回給模型**：

```python
except MalformedToolCall as exc:
    history.append(_user_msg(format_parse_error(str(exc))))
    continue   # 不計失敗，進入下一輪，模型看到錯誤說明後會自己改
```

運行 `tests/test_loop.py::test_self_repair_after_malformed` 可以看到：
一個「先犯錯、後改對」的劇本照樣順利收尾。這個小小的 try/except
就是真實 harness 裡 "agentic self-healing" 的種子。

### 2. 步數上限（step budget）

循環必須有熔斷器。模型可能陷入「調同一個工具→同樣報錯→再調」的死循環，
每一次都是真金白銀的 token。`max_steps` 到頂就誠實返回失敗：

```python
return RunResult(final="已達到步數上限……", ok=False, error="max_steps", ...)
```

評測時 `ok=False` 會被記為 FAIL——寧可不及格，不可無限燒錢。

### 3. 上下文預算（喂給模型前先裁剪）

```python
messages = self.context.fit(history)   # 超預算時裁掉最舊的歷史
reply = self.llm.generate(messages)
```

細節在 [04 章](04-context.md)。這裡只需知道：歷史是無限增長的，
窗口是有限的，harness 必須替模型管理這個資源。

### 4. 過程日誌（讓人看得見）

`verbose=True` 時每一步都打印：模型說了什麼、調了什麼工具、觀察到什麼。
Agent 系統最難的不是寫出來，而是**調試**——可見性就是可調試性。

## 循環不變量（invariant）

`context.py` 依賴一條紀律：`history[2:]` 永遠是
`(assistant 工具調用, user 工具結果)` **成對出現**。
這樣裁剪歷史時才能整對丟棄，不出現「孤兒調用」。
`tests/test_context.py::test_pairs_dropped_together` 釘住了這條性質。

## 什麼時候循環會停？

三種出口，缺一不可：

| 出口 | 觸發條件 | 結果 |
| --- | --- | --- |
| 模型收工 | 回覆不含 toolcall 塊 | `ok=True`，回覆即最終回答 |
| 步數熔斷 | `step > max_steps` | `ok=False`，`error="max_steps"` |
| 上層放棄 | 調用方自己中斷（如 REPL 的 Ctrl-C） | 交給宿主程序 |

「模型不再調用工具 = 任務完成」這條協議在 [02 章](02-protocol.md)細講，
它簡單，但有著名的失敗模式：模型可能「忘了自己要做什麼」提前收工，
或「強迫症發作」永遠再多調一次工具。第 07 章的評測會把這些暴露出來。

## 練習

1. 給 `Agent` 加一個 `on_step(step, info)` 回調，把每一步寫進 JSONL 文件
   （這就是最簡單的「軌跡記錄」，評測和復盤都靠它）；
2. 讓 max_steps 觸發後，把「已完成的進度」作為 `final` 的一部分返回——
   提示：讓 todo 工具的內容參與進來；
3. （進階）實現「繼續跑」：把上一輪的 history 傳回 `run()`，接著跑而不是重跑。

## 延伸閱讀

- [mini-swe-agent 的 agent loop 源碼](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/agents/default.py)——對照閱讀，看看工業版多做了什麼；
- [ReAct 論文](https://arxiv.org/abs/2210.03629)；
- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)——
  "agents are models using tools in a loop" 一節與本章一一對應。
