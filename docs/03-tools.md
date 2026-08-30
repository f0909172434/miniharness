# 03 · 工具：agent 的雙手

> 對應代碼：`miniharness/tools.py`。工具層是 harness 裡「產品味」最重的部分——
> 它的介面設計直接決定模型表現，這正是 SWE-agent 論文提出
> Agent-Computer Interface（ACI）概念的動機。

## 一個工具的解剖圖

```python
Tool(
    name="read_file",                          # 模型引用的名字
    description="讀取一個文本文件。",            # 模型決定用不用它
    params={"path": Param("string", "...", required=True)},  # 模型怎麼填參數
    func=t_read_file,                          # harness 怎麼執行
)
```

四個部位，兩種受眾：`name/description/params` 是**給模型看的 API 文檔**，
`func` 是**給 Python 看的實現**。寫工具 = 同時寫文檔和代碼，
而文檔的一半質量決定了 agent 的一半智商。

## ToolRegistry：註冊、校驗、執行、截斷

`run_tool(name, args)` 是模型與真實世界之間唯一的門，它按順序做五件事：

1. **工具存在嗎？** 不存在 → ERROR + 列出可用工具（模型可以自我糾正）；
2. **必填參數齊嗎？** 缺 → ERROR + 參數說明；
3. **參數合法嗎？** 不認識的參數名、錯誤的類型 → ERROR；
4. **執行**，任何異常降級為 `ERROR: ...` 文本，永不向上拋；
5. **截斷輸出**到 `max_output`（默認 4000 字符），超長加省略標記。

第 5 條值得單獨強調：工具輸出會整段進入上下文，一個 `cat` 大文件
就能把對話預算燒光。**在創建點截斷**（而不是事後裁歷史）是最便宜的防線。

## 好工具的五條設計原則

這些原則全部來自真實 harness 的踩坑史：

1. **少而精，組合用。** MiniHarness 只有 5 個工具，靠組合完成所有任務。
   工具越多，模型選錯的概率越高（這有實證：工具數超過十幾個，
   選擇準確率明顯下降）。與其加 `count_lines`，不如讓模型用 `run_bash wc -l`；
2. **輸出永遠有限、可讀。** `list_dir` 遞歸模式封頂 200 條並註明總數；
   `read_file` 封頂 8000 字符。無限輸出 = 上下文炸彈；
3. **錯誤信息是寫給模型看的**。「ERROR: 路徑越界」比 `raise Exception()`
   有用得多——前者能觸發自愈，後者只能觸發崩潰；
4. **參數類型越少越好。** 只支持 string/integer/boolean。模型最擅長生成
   這三種；嵌套對象參數是碎裂重災區；
5. **副作用明確、可撤銷。** `write_file` 返回「寫到哪、寫了多少」；
   破壞性操作（如刪除）在生產 harness 裡通常還要二次確認。

## MiniHarness 的五件套

| 工具 | 能力 | 教學點 |
| --- | --- | --- |
| `list_dir` | 列目錄（可遞歸） | 輸出封頂的示範 |
| `read_file` | 讀文件 | 路徑守衛 + 長度封頂 |
| `write_file` | 寫文件 | 自動建父目錄、回執信息 |
| `run_bash` | 白名單命令 | 安全設計，見 [06 章](06-sandbox.md) |
| `todo` | 讀寫計劃文件 | 見 [05 章](05-memory.md) |

注意一個「負空間」：**沒有** `delete_file`、`move_file`、`search_web`。
不是不能寫，而是每加一個工具都要過一遍五條原則——
留給你當練習，順便體會取捨。

## 加一個新工具（10 分鐘練習）

在 `make_builtin_tools()` 裡加一個 `search` 工具（在所有 .py 裡搜正則）：

```python
def t_search(pattern: str, glob: str = "*.py") -> str:
    import re as _re
    hits = []
    rx = _re.compile(pattern)
    for p in sorted(ws.rglob(glob)):
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if rx.search(line):
                hits.append(f"{p.relative_to(ws).as_posix()}:{i}: {line.strip()}")
    return "\n".join(hits[:50]) or "(無命中)"
```

然後註冊、跑 `demos/demo_mock.py`、再跑 `python3 -m pytest`。
注意兩件事：輸出依然要封頂；以及這個工具讓 grep 白名單變得多餘——
工具之間會互相競爭，這也是「少而精」的理由。

## 延伸閱讀

- SWE-agent 論文（[arXiv:2405.15793](https://arxiv.org/abs/2405.15793)）第 3 節 ACI 設計；
- [Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering)（工程博客系列）；
- [MCP（Model Context Protocol）](https://modelcontextprotocol.io)——
  當工具需要跨應用共享時，業界的標準化答案；08 章討論怎麼接。
