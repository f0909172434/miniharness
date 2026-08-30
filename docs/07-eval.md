# 07 · 迷你評測：怎麼證明你的 harness 有用

> 對應代碼：`miniharness/eval.py` 與 `miniharness/tasks.py`。
> 跑起來：`python3 demos/demo_eval.py`（離線）/ `--real`（真模型）。

## 沒有評測，改進就是玄學

你給系統提示詞加了一條規則、換了一個模型、把 `max_output` 從 4000
調到 8000——變好了嗎？「我感覺好多了」不是工程答案。
Harness 開發 80% 的迭代靠的是一個樸素循環：

```
改動 harness → 跑任務集 → 看通過率與軌跡 → 再改動
```

SWE-bench、Terminal-Bench 這些工業級評測做的也是同一件事，
只是規模和任務的真實程度不同。

## Task = setup + prompt + check

```python
Task(
    name="todo-report",
    prompt="找出工作區裡所有包含 TODO 標記的 .py 文件，把清單寫入 REPORT.md……",
    setup=make_demo_workspace,   # 每次考試前，造一個乾淨考場
    check=_check_report,         # 驗收產物
)
```

三件套各有講究：

### setup：可重放的考場

每個任務都在**全新的臨時工作區**裡搭出確定的初始狀態
（`_FIXTURE_FILES` 字典 + harness 自己的 `write_file`）。
同一份試卷，今天跑和明天跑、你跑和我跑，考場必須一模一樣——
否則通過率的波動你無法歸因。

### prompt：只描述目標，不劇透路徑

「把清單寫入 REPORT.md」是目標；「先跑 grep -rn 再寫文件」是劇透。
好的 prompt 允許不同的解法存在，這樣評測才能反映 harness 的真實能力。

### check：驗產物，不驗過程

看 MiniHarness 三個 checker 的寫法：

```python
# todo-report：驗報告內容包含三個文件路徑
missing = [p for p in REPORT_PATHS if p not in text]

# fix-syntax：讓 Python 語法樹做裁判
ast.parse(src.read_text(encoding="utf-8"))

# find-token：驗最終回答包含正確 token
return PLANTED_TOKEN in result.final
```

兩條軍規：

1. **驗產物不驗過程**。agent 用 grep 還是 find、走三步還是六步，
   都不管——東西對了就算過。過程檢查會把「更聰明的新解法」誤判為失敗；
2. **check 必須確定、便宜、無 LLM**。`ast.parse` 毫秒級且絕對可重放。
   （「用另一個 LLM 當裁判」是常見的升級路線，但引入了裁判的方差，
   教學階段先不碰。）

## 從 3 個任務到 SWE-bench

| 維度 | MiniHarness | SWE-bench / Terminal-Bench |
| --- | --- | --- |
| 考場 | 臨時目錄 + 幾個小文件 | 真實 GitHub repo + Docker 鏡像 |
| 試卷 | 3 個手寫任務 | 2294 個真實 issue（SWE-bench） |
| 驗收 | `ast.parse` / 字符串比對 | 跑倉庫的單元測試（FAIL_TO_PASS） |
| 成績 | 通過率 | % resolved，按 repo/難度切分 |

概念完全同構。理解了 MiniHarness 的 `run_eval`，你就理解了所有
agent leaderboard 背後的機器。

## 除了通過率，還該看什麼

demo 輸出裡每行末尾的兩個數字別忽略：

- **steps / tool_calls**：同樣 PASS，3 步和 12 步是兩種產品。
  步數是費用與延遲的代理指標；
- **ok=False 的原因分佈**：`max_steps` 熔斷多 → 任務太難或步數預算太小；
  最終回答錯 → 模型能力或提示詞問題。**失敗模式比通過率更有信息量。**

## 練習（畢業作業）

1. 加一個新任務 `refactor`: 把 `app/utils.py` 的函數改名並更新所有引用，
   checker 用 `ast.parse` 驗證改名後無殘留舊名；
2. 跑 20 次取通過率而不是 1 次——親眼看到方差，理解為什麼論文報均值；
3. 對比實驗：同一任務集，`max_steps=6` vs `=15`、`max_output=2000` vs `=8000`，
   寫下你的結論。這就是一篇迷你 harness 消融實驗（ablation）。

## 延伸閱讀

- [SWE-bench 論文](https://arxiv.org/abs/2310.06770)—— 任務構建與 FAIL_TO_PASS 驗收的設計；
- [Terminal-Bench](https://github.com/laude-institute/terminal-bench) —— 容器化終端任務集；
- [OpenAI: Evaluating and ablations](https://platform.openai.com/docs/guides/evals) —— API 廠商視角的評測指南。
