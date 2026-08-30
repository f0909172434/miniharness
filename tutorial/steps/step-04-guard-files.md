# 第 4 步 · 路徑守衛與文件讀寫

> 對應概念：[docs/03-tools.md](../../docs/03-tools.md) 與 [docs/06-sandbox.md](../../docs/06-sandbox.md)
> 參考實現：`solutions/my_harness_full.py` 的「4) 路徑守衛與文件讀寫」段

## 目標

給工具箱加讀寫能力，並豎起第一道安全閘：**大腦給的路徑不許逃出工作區**。

## 規格

```python
def guard_path(workspace, raw): ...
    # 返回解析後的絕對 Path；越界（如 "../x"）拋 ValueError

def make_tools(workspace): ...
    # 在 list_dir 之外，新增：
    #   read_file(path) -> 文件內容
    #   write_file(path, content) -> "OK：已寫入 ...（N 字符）"（自動創建父目錄）
```

讀寫工具內部必須先過 `guard_path`；越界時讓異常發生，
由 `run_tool` 的第 2 條規則兜底成 `ERROR` 文本。

## 提示

- 守衛的寫法只要一句話：把 `workspace / raw` 做 `resolve()`，
  然後檢查它仍在 `workspace` 之內（比較 `parents`）；
- **macOS 坑**：`/var` 是 `/private/var` 的符號鏈接。把 `workspace` 先
  `resolve()` 一次再統一使用，否則 `relative_to` 會當場爆炸
  （MiniHarness 正式版在 `make_builtin_tools` 裡也踩過這個坑）。

## 常見坑

- `write_file` 忘了 `mkdir(parents=True, exist_ok=True)`，子目錄寫入失敗；
- 只擋 `..` 字符串而不做 `resolve()`——`a/../../x` 這種就繞過了。
  規範化之後再比較才是真防線。

## 驗收

```bash
python3 tutorial/check.py 4
```
