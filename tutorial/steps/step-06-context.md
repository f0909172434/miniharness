# 第 6 步 · 上下文預算

> 對應概念：[docs/04-context.md](../../docs/04-context.md)
> 參考實現：`solutions/my_harness_full.py` 的「6) 上下文預算」段

## 目標

歷史無限增長，窗口有限。寫出裁剪器，並接進循環。

## 規格

```python
def fit_history(history, max_chars): ...
    # 返回裁剪後的「新列表」，不改動原列表
```

行為：

- 總字符數 ≤ `max_chars` → 原樣返回；
- 超了 → 保住 `history[0]`（system）與 `history[1]`（任務），
  從**最舊**的 `(assistant, user)` 對開始丟棄，保留最新的；
- 發生丟棄時，在被裁的位置插入一條 `user` 消息，內容包含「裁剪」字樣，
  告訴大腦「歷史被剪過」；
- 裁完總長度 ≤ `max_chars`；除占位說明外，消息仍按 `(assistant, user)` 成對排列。

`run_agent` 升級：新增 `max_chars=None` 參數——不為 `None` 時，
**每次** `generate` 之前先 `fit_history`。

## 提示

- 從最新往回收集 `(assistant, user)` 對，收不下的留在後面；
- 檢查器會用一個「探針大腦」量每次餵給它的歷史大小，
  所以裁剪必須發生在 `generate` 之前，而不是事後。

## 常見坑

- **單條丟棄**：只丟 assistant 或只丟 user，歷史裡出現「孤兒調用」
  （有大腦的調用卻沒有觀察，或反之）——必須整對丟；
- 忘了「原樣返回時也要返回拷貝」；直接返回原列表雖然能過檢查，
  但讓調用方拿到可變共享狀態是隱患。

## 驗收

```bash
python3 tutorial/check.py 6
```
