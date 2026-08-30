# 第 7 步 · 迷你評測

> 對應概念：[docs/07-eval.md](../../docs/07-eval.md)
> 參考實現：`solutions/my_harness_full.py` 的「7) 迷你評測」段

## 目標

寫出評測 runner：同一套任務，誰來考都得到同樣的分數。
從此你改動 harness 的每一行，都有數字說話。

## 規格

```python
def run_eval(tasks, brain_factory): ...
    # tasks: [{"name", "prompt", "setup", "check"}, ...]
    # setup(ws) 搭建工作區；check(ws, result) -> (bool, str) 驗收
    # 返回通過率 float
```

行為：

1. **每個任務**都開一個全新的臨時工作區（互不串味）；
2. 先跑 `setup(ws)`，再用 `brain_factory()` 造一個新大腦跑任務
   （工具箱用 `make_tools(ws)` 現做）；
3. `check` 返回真 → 通過；返回假 → 不通過；
   **`check` 自己拋異常 → 也算不通過**（評測不能被壞 checker 炸掉）；
4. 逐個打印 `[PASS]/[FAIL] 任務名 — 說明`，最後返回 `通過數/總數`。

## 提示

- `tempfile.mkdtemp()` 開工作區；
- `check` 的調用包在 `try/except` 裡，異常轉成 FAIL + 說明；
- 「checker 驗產物不驗過程」的設計討論在 docs/07——本步先讓機器轉起來。

## 常見坑

- 所有任務共用一個工作區 → 任務之間互相污染（檢查器專門測這個）；
- `brain_factory()` 只在循環外調用一次 → 所有大腦共享狀態；
- checker 異常直接讓整場評測崩潰。

## 驗收

```bash
python3 tutorial/check.py 7
```
