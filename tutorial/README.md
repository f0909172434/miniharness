# MiniHarness 動手營

**跟著 8 個步驟，從一個空文件開始，親手寫出自己的 agent harness。**
寫完的 `my_harness.py` 約 200 行，具備正式版 MiniHarness 的全部核心件：
循環、協議、工具、安全閘、自我修復、上下文裁剪、評測、規則大腦。

## 玩法

```
讀一步 steps/ 文檔 → 在 tutorial/my_harness.py 裡寫代碼 → 跑檢查器 → 全綠進下一步
```

```bash
python3 tutorial/check.py        # 進度總覽：哪幾步過了、卡在哪
python3 tutorial/check.py 3      # 只驗收第 3 步（失敗附詳細提示）
```

要求：Python 3.9+，零依賴。工作量約 3-5 小時。

## 三條營規

1. **不許 `import miniharness`**——檢查器會攔截。`miniharness/` 包是
   你畢業之後回去對照的參考源碼，不是起點；
2. **卡住先看錯誤提示，再讀對應概念章（docs/），30 分鐘後才許開
   `solutions/my_harness_full.py`**——而且只看你卡住的那一段；
3. **規格優先**：檢查器驗收的是「行為」而不是實現方式。
   函數名、返回結構、錯誤文本關鍵字是合同；內部怎麼寫全是你的自由。

## 步驟表

| 步 | 文檔 | 你寫出什麼 | 對應概念章 |
| --- | --- | --- | --- |
| 1 | [step-01](steps/step-01-loop.md) | `ScriptBrain` + `run_agent` 循環骨架 | [01 循環](../../docs/01-agent-loop.md) |
| 2 | [step-02](steps/step-02-protocol.md) | toolcall 協議與解析器 | [02 協議](../../docs/02-protocol.md) |
| 3 | [step-03](steps/step-03-tools.md) | 工具箱 + 執行器（錯誤即文本） | [03 工具](../../docs/03-tools.md) |
| 4 | [step-04](steps/step-04-guard-files.md) | 路徑守衛 + 讀寫文件 | [03](../../docs/03-tools.md) / [06 安全](../../docs/06-sandbox.md) |
| 5 | [step-05](steps/step-05-repair.md) | 解析失敗的自我修復 | [01 循環](../../docs/01-agent-loop.md) |
| 6 | [step-06](steps/step-06-context.md) | 上下文預算與成對裁剪 | [04 上下文](../../docs/04-context.md) |
| 7 | [step-07](steps/step-07-eval.md) | 迷你評測 runner | [07 評測](../../docs/07-eval.md) |
| 8 | [step-08](steps/step-08-graduation.md) | 🎓 畢業考：規則大腦跑通 TODO 報告 | [09 造腦](../../docs/09-from-zero.md) |
| 9 | [step-09](steps/step-09-bonus.md) | （選做）接上真模型 | [docs/01](../../docs/01-agent-loop.md) |

## 為什麼這樣排序

前 5 步搭出「能幹活」的循環（協議 → 雙手 → 自愈），
第 6 步解「能跑很久」（上下文），第 7 步解「知道好不好」（評測），
第 8 步補上「智能」——而且特意用一個**沒有模型**的規則大腦：
它會讓你親眼確認這門課的核心命題——**智能在模型，工程在 harness**。
智能可以換（第 9 步換成真 LLM），工程才是你自己的。

## 畢業之後

- 對照閱讀 `miniharness/` 包源碼（順序：`loop` → `protocol` → `tools` →
  `context` → `brains`），你會讀得飛快；
- 跑 `python3 demos/demo_eval.py --real`，讓真模型在你的 harness 思路上
  的正式版裡打工；
- 給評測集加一個自己的任務（docs/07 練習 1），或把你的 `my_harness.py`
  改造心得寫成 PR。

`tutorial/my_harness.py` 是你的作業文件，已被 `.gitignore` 忽略——
想提交自己的實現也行，去掉那一行 ignore 即可。
