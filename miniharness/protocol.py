"""協議層：模型與 harness 之間「怎麼說」（對應課程 docs/02-protocol.md）。

MiniHarness 選擇了最透明的**文本協議**：模型在回覆裡用一個 ```toolcall
代碼塊表達「我要調用工具」，harness 用正則解析它。

    Thought: 我先看一下目錄。
    ```toolcall
    {"tool": "list_dir", "args": {"path": "."}}
    ```

規則只有兩條：
1. 回覆裡有 toolcall 塊  => harness 執行工具，把結果作為下一條用戶消息喂回去；
2. 回覆裡沒有 toolcall 塊 => 整段文字就是給用戶的最終回答，循環結束。

生產級 harness 多用 API 原生的 function calling（結構化、更穩），
但文本協議的好處是：換任何一家 OpenAI 兼容端點都能跑，而且每一步
「模型說了什麼」都原樣可見，非常適合教學。取捨對比見 docs/02。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

TOOLCALL_FENCE = "```toolcall"

# 匹配第一個 toolcall 代碼塊（非貪婪）。多個塊時只取第一個，其餘忽略——
# 系統提示詞裡已明確「每輪至多一個工具調用」。
_FENCE_RE = re.compile(r"```toolcall\s*(.*?)\s*```", re.DOTALL)


@dataclass
class ToolCall:
    """一次待執行的工具調用。"""

    name: str
    args: Dict


@dataclass
class ParsedResponse:
    """解析結果：thought 是代碼塊之外的自由文本，toolcall 為 None 表示最終回答。"""

    thought: str = ""
    toolcall: Optional[ToolCall] = None


class MalformedToolCall(ValueError):
    """模型輸出了 toolcall 塊但內容不合法（壞 JSON、缺欄位等）。"""


def format_toolcall(name: str, args: Dict) -> str:
    """把一次工具調用渲染成模型應當輸出的文本形態（測試 / Mock 也靠它保持一致）。"""
    payload = json.dumps({"tool": name, "args": args}, ensure_ascii=False)
    return f"{TOOLCALL_FENCE}\n{payload}\n```"


def format_tool_result(name: str, output: str) -> str:
    """工具結果的統一信封。模型靠這個前綴辨認「這是環境喂回來的觀察」。"""
    return f"TOOL RESULT ({name}):\n{output}"


def format_parse_error(reason: str) -> str:
    """解析失敗時喂回給模型的糾錯消息——agent「自我修復」的起點。"""
    return (
        "TOOL RESULT (parse):\n"
        f"ERROR: {reason}\n"
        "請重新輸出：用 ```toolcall 代碼塊給出且僅給出一個合法 JSON 工具調用，"
        '格式為 {"tool": "工具名", "args": {...}}。'
    )


def parse_response(text: str) -> ParsedResponse:
    """把模型回覆拆成 (思考文本, 工具調用?)。

    解析失敗不拋到天上，而是拋 MalformedToolCall——由 Agent 捕獲後
    把錯誤喂回給模型，讓它自己修（見 loop.py 的 except 分支）。
    """
    match = _FENCE_RE.search(text)
    thought = _FENCE_RE.sub("", text).strip()

    if match is None:
        # 沒有工具調用 => 整段就是最終回答。
        return ParsedResponse(thought=thought)

    body = match.group(1)
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise MalformedToolCall(f"toolcall 塊不是合法 JSON：{exc}") from exc

    if not isinstance(data, dict) or "tool" not in data:
        raise MalformedToolCall(
            'toolcall 塊必須是形如 {"tool": "名字", "args": {...}} 的 JSON 對象'
        )

    args = data.get("args", {})
    if not isinstance(args, dict):
        raise MalformedToolCall('"args" 必須是 JSON 對象（鍵值對）')

    return ParsedResponse(
        thought=thought,
        toolcall=ToolCall(name=str(data["tool"]), args=args),
    )


def build_system_prompt(tools, workspace: Path, extra_rules: str = "") -> str:
    """系統提示詞：告訴模型它是誰、在哪裡、手上有什麼工具、按什麼規則說話。

    這是 harness「塑造模型行為」的第一槓桿。想改 agent 的性格/習慣，
    先改這裡，而不是去改模型。
    """
    return f"""你是一個運行在 MiniHarness（教學用 agent harness）中的 agent。
你的工作目錄：{workspace}
所有文件路徑都相對於它書寫；harness 會拒絕越出該目錄的訪問。

## 可用工具
{tools.catalog()}

## 回合規則
1. 每一輪先用一兩句話寫下你的思考（以 Thought: 開頭），需要行動時輸出至多一個工具調用：
{TOOLCALL_FENCE}
{{"tool": "工具名", "args": {{"參數名": "值"}}}}
```
2. 工具的執行結果會以「TOOL RESULT (工具名):」開頭的用戶消息返回給你。
3. 一次只調用一個工具，等結果回來再做下一步決策；不要臆測工具的輸出。
4. 工具返回 ERROR 時，讀懂錯誤信息、修正參數後重試；不要原樣重複調用。
5. 任務完成後不要再調用任何工具：直接輸出給用戶的最終回答，
   說清結論以及產物（文件）的位置。
{extra_rules}"""
