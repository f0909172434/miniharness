# 第 1 步 · 循環與台詞大腦

> 對應概念：[docs/01-agent-loop.md](../../docs/01-agent-loop.md)
> 參考實現：`solutions/my_harness_full.py` 的「1) 循環與台詞大腦」段（卡住 30 分鐘再看）

## 目標

把「一次調用」升級成「一個循環」：大腦反覆看著歷史說話，harness 反覆記錄。
本步還沒有工具、沒有協議——先把骨架立起來。

## 你要在 `tutorial/my_harness.py` 裡寫出什麼

```python
class ScriptBrain:
    """背台詞的大腦：按順序返回預設回覆。"""
    def __init__(self, lines): ...      # lines 是字符串列表
    def generate(self, messages): ...   # 返回下一句；台詞耗盡時返回 None


def run_agent(brain, task, max_steps=5):
    """返回 {"final": str, "steps": int, "history": list}"""
```

`run_agent` 的行為規格（check.py 按這個驗收）：

- `history` 前兩條固定為 `[{"role": "system", ...}, {"role": "user", "content": 含任務文本}]`；
- 每輪：把整個 `history` 餵給 `brain.generate(...)`，把回覆作為
  `{"role": "assistant", ...}` 追加進 `history`，`steps` 加一；
- 台詞耗盡（大腦返回 `None`）→ 以最後一句台詞作為 `final` 停下；
- 跑滿 `max_steps` 輪 → 也停下（`final` 為最後一句台詞）。

## 提示（不劇透）

- `ScriptBrain` 用一個下標指針就夠了；
- 本步每句台詞都只是「又被記了一筆」——你可能覺得循環沒有意義。
  對，現在還沒有意義。第 2 步引入協議後，「說什麼」才開始有後果；
  `max_steps` 的價值也要到那時才顯現（現在它是防大腦無限背台詞的保險絲）。

## 常見坑

- 忘了把大腦的回覆 append 進 `history`（下一輪大腦就看不到自己說過什麼）；
- `None` 判斷放在 `append` 之後（會把 None 記進歷史）。

## 驗收

```bash
python3 tutorial/check.py 1
```
