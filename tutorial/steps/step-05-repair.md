# 第 5 步 · 自我修復

> 對應概念：[docs/01-agent-loop.md](../../docs/01-agent-loop.md) 的「解析失敗的自愈」
> 參考實現：`solutions/my_harness_full.py` 的 `run_agent` 裡的 `except BadToolCall` 分支

## 目標

大腦是概率系統，總有一天輸出壞 JSON。菜鳥實現直接崩潰；
正確做法是把錯誤**喂回給大腦**，讓它自己改——這是 agent 可靠性的秘密。

## 規格

升級 `run_agent`：`parse_reply` 拋出 `BadToolCall` 時，

1. 不終止、不崩潰；
2. 往 `history` 追加一條 `{"role": "user", "content": ...}` 糾錯消息，
   內容必須包含 `ERROR` 和大腦看得懂的补救說明；
3. `continue` 進入下一輪。

## 提示

- 糾錯消息是**寫給大腦看的**：說清楚錯在哪、正確格式長什麼樣。
  對照 `miniharness/protocol.py` 的 `format_parse_error()`；
- 壞調用同樣消耗一步（`steps` 照加）——它不是免費的；
- 想看效果：跑 `python3 - <<'EOF'` 之類的小腳本，構造一個
  `["```toolcall\n{oops\n```", "修好了"]` 的劇本。

## 常見坑

- `except` 裡忘了 `continue`，代碼接著用解析失敗的 `parsed` 又炸一次；
- 糾錯消息以 assistant 身份追加——錯誤反饋必須是 user 消息，
  這是「環境對模型說話」的通道。

## 驗收

```bash
python3 tutorial/check.py 5
```
