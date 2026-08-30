# 第 8 步（畢業）· 規則大腦 + TODO 報告

> 對應概念：[docs/09-from-zero.md](../../docs/09-from-zero.md)
> 參考實現：`solutions/my_harness_full.py` 的「8) 畢業：規則大腦」段

## 目標

畢業考：親手寫一個**沒有模型的規則大腦**，驅動你這 7 步造出的整套
harness，完成一個真實的多步任務。跑通它，你就擁有了一個完整 agent。

## 規格

給工具箱加最後一件工具：

```python
def make_tools(workspace): ...
    # 新增 "search"：t_search(pattern, glob="*.py")
    # 在工作區內遞歸搜索，返回 "路徑:行號: 內容" 每行一條（封頂 100 條）
```

再寫出規則大腦：

```python
class RuleBrain:
    def generate(self, messages): ...   # 遵守第 2 步的協議
```

**實現完全自由**——檢查器只驗終態。畢業任務（檢查器會自動搭建考場）：

> 找出工作區裡所有包含 TODO 標記的 .py 文件，把清單寫入 REPORT.md
> （每行一條，含文件路徑）。

通過標準：12 步之內，`REPORT.md` 存在、包含 `app/core.py`、
`app/utils.py`、`scripts/pipeline.py` 三條路徑，且**不含** `notes.txt`
（它不是 .py，是誘餌）。

## 提示

- 規則大腦看兩樣東西決定下一步：`_prev_call(messages)`（上一步動作）
  和 `_last_user(messages)`（最新觀察）——這兩個小助手值得先寫；
- 建議的最小動作序列：`search` → 把觀察整理成報告 `write_file` → 收工；
- 觀察行是 `path:line: text` 格式，`split(":", 1)[0]` 取路徑；
- 想加 `list_dir` / `todo` 等動作隨意——動作越多規則鏈越長，
  這正是 docs/09 說的「手寫規則的維護成本」。

## 常見坑

- 把 `notes.txt` 的命中混進報告（`glob` 參數是幹這個用的）；
- 觀察裡的 `TOOL RESULT` 信封行、`[exit=...]` 行被當成命中行解析；
- 忘了最後一輪「不輸出 toolcall = 最終回答」，跑到步數上限。

## 驗收（畢業考）

```bash
python3 tutorial/check.py 8
python3 tutorial/check.py    # 全綠 → 🎓
```
