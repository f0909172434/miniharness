# 第 2 步 · 協議：讓大腦會說「調工具」

> 對應概念：[docs/02-protocol.md](../../docs/02-protocol.md)
> 參考實現：`solutions/my_harness_full.py` 的「2) 協議」段

## 目標

給大腦一個說「我要調工具」的格式，並寫出解析器。本步全是純函數，
不碰 `run_agent`（下一步才把它接進循環）。

## 規格

```python
TOOLCALL_FENCE = "```toolcall"

def format_toolcall(name, args): ...
    # 返回 f"{TOOLCALL_FENCE}\n{json}\n```"，json 為 {"tool": name, "args": args}

class BadToolCall(ValueError): ...   # 解析失敗時拋出


def parse_reply(text): ...
    # 返回 {"thought": str, "toolcall": None | {"name": str, "args": dict}}
```

`parse_reply` 的合同（只有兩條）：

1. 文本裡有 ```toolcall 圍欄 → 取出 JSON，`toolcall` 為 `{"name": ..., "args": ...}`，
   圍欄之外的文字放進 `thought`；
2. 沒有圍欄 → `toolcall` 為 `None`，整段文本就是 `thought`（= 最終回答）。

以下三種情況必須拋 `BadToolCall`：圍欄內不是合法 JSON；缺 `"tool"` 鍵；
`"args"` 不是對象。

## 提示

- 正則記得 `re.DOTALL`（JSON 可能跨行）；
- 「多個圍欄只取第一個」——用 `search` 而不是 `findall`；
- 把圍欄從原文裡 `sub` 掉剩下的就是 `thought`，不用自己拼。

## 常見坑

- 忘記 `ensure_ascii=False`，中文參數被轉成 `\uXXXX`；
- 對「缺鍵 / 類型不對」直接讓 `KeyError`/`TypeError` 飛出去——
  要轉成 `BadToolCall`（第 5 步的循環要靠它做自我修復）。

## 驗收

```bash
python3 tutorial/check.py 2
```
