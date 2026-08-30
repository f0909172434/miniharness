# 第 3 步 · 工具執行

> 對應概念：[docs/03-tools.md](../../docs/03-tools.md)
> 參考實現：`solutions/my_harness_full.py` 的「3) 工具執行」段

## 目標

給 agent 一雙手。本步結束時，你的 agent 第一次真正「動」了：
大腦說調工具 → harness 執行 → 觀察寫回歷史。

## 規格

```python
def make_tools(workspace): ...
    # 返回 {"工具名": callable(**args) -> str}，本步至少要有 "list_dir"

def run_tool(tools, name, args): ...
    # 永不拋異常，永遠返回字符串
```

`run_tool` 的行為：

1. 工具不存在 → 返回 `ERROR: ...` 文本（附上可用工具名）；
2. 工具拋異常 → 降級為 `ERROR: ...` 文本（永不向上拋）；
3. 輸出超過 400 字符 → 截斷，並在尾部提示中包含「截斷」字樣。

`run_agent` 本步升級（新增 `tools=None` 參數與返回鍵 `tool_calls`）：

- 解析回覆：無 `toolcall` → 返回 `final`（維持第 1 步語義）；
- 有 `toolcall` → `run_tool` 執行，把
  `{"role": "user", "content": "TOOL RESULT (工具名):\n結果"}` 追加進歷史；
- 返回 dict 增加 `"tool_calls"`（執行了多少次工具）。

## 提示

- 工具函數簽名用 `def t_list_dir(path=".", recursive=False)` 這種帶默認值的
  關鍵字參數，`run_tool` 裡用 `tool(**args)` 調用——這樣大腦傳什麼參數名就
  自動對上；
- 本步的 `list_dir` 只需非遞歸列出（子目錄名加 `/` 後綴便於大腦辨認），
  遞歸版到第 8 步要用時再加。

## 常見坑

- `run_tool` 忘了 `str(...)` 包一層（工具萬一返回非字符串）；
- 觀察忘了 `TOOL RESULT (工具名):` 信封——大腦（和你自己）讀歷史時
  全靠這個前綴分辨「這是環境的話」。

## 驗收

```bash
python3 tutorial/check.py 3
```
