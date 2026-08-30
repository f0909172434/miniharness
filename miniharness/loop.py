"""AgentLoop：harness 的心臟（對應課程 docs/01-agent-loop.md）。

先看偽代碼，整個 agent 其實就是這個 while 循環：

    history = [system_prompt, task]
    while True:
        reply = llm(history)            # 模型讀歷史，決定下一步
        if "no tool call" in reply:     # 不再調用工具 => 任務完成
            return reply
        result = tools(reply.toolcall)  # harness 運行工具
        history += [reply, result]      # 觀察寫回歷史，進入下一輪

真實實現多出來的 30% 代碼，都在處理「模型不完美」與「資源有限」：
解析失敗的自愈（把錯誤喂回去讓模型自己改）、步數上限（防失控循環）、
上下文預算（歷史太長先裁剪）、以及過程日誌（讓人看得見 agent 在幹嘛）。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

from .context import ContextManager
from .llm import BaseLLM
from .protocol import (
    MalformedToolCall,
    build_system_prompt,
    format_parse_error,
    format_tool_result,
    parse_response,
)
from .tools import ToolRegistry

_DIM, _CYAN, _YELLOW, _RED, _GREEN = "2", "36", "33", "31", "32"


def _c(text: str, code: str) -> str:
    """極簡 ANSI 上色，尊重 NO_COLOR 環境變量（管道/重定向時輸出也乾淨）。"""
    if os.environ.get("NO_COLOR"):
        return text
    return f"\033[{code}m{text}\033[0m"


def _preview(text: str, limit: int = 160) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + "……"


def _assistant_msg(content: str) -> dict:
    return {"role": "assistant", "content": content}


def _user_msg(content: str) -> dict:
    return {"role": "user", "content": content}


@dataclass
class RunResult:
    """一次完整運行的結果與跡證。history 保留全部對話，供調試與評測復盤。"""

    final: str
    steps: int
    tool_calls: int
    ok: bool
    error: Optional[str] = None
    history: List[dict] = field(default_factory=list)


class Agent:
    """把 大腦(LLM) + 雙手(工具) + 工作記憶(上下文) 裝進一個 while 循環。"""

    def __init__(
        self,
        llm: BaseLLM,
        tools: ToolRegistry,
        max_steps: int = 12,
        verbose: bool = True,
        context: Optional[ContextManager] = None,
        extra_rules: str = "",
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.verbose = verbose
        self.context = context if context is not None else ContextManager()
        self.system_prompt = build_system_prompt(tools, tools.workspace, extra_rules)

    # ---------- 對外主入口 ----------

    def run(self, task: str) -> RunResult:
        """執行一個任務，直到模型給出最終回答或觸發停止條件。"""
        history: List[dict] = [
            {"role": "system", "content": self.system_prompt},
            _user_msg(f"任務：{task}"),
        ]
        tool_calls = 0
        parsed = None

        for step in range(1, self.max_steps + 1):
            self._log(f"┌─ Step {step} / {self.max_steps}", _DIM)

            # 1) 上下文預算檢查後，讓模型看著歷史說話
            messages = self.context.fit(history)
            reply = self.llm.generate(messages)
            history.append(_assistant_msg(reply))
            self._log(f"│ 模型：{_preview(reply, 200)}", _DIM)

            # 2) 解析回覆。解析失敗不終止——把錯誤喂回去，給模型自我修復的機會
            try:
                parsed = parse_response(reply)
            except MalformedToolCall as exc:
                self._log(f"│ ✗ 解析失敗：{exc}", _RED)
                history.append(_user_msg(format_parse_error(str(exc))))
                continue

            # 3) 沒有工具調用 => 模型認為任務完成，整段文本就是最終回答
            if parsed.toolcall is None:
                self._log(f"└─ ✓ 完成（{step} 步，{tool_calls} 次工具調用）", _GREEN)
                return RunResult(
                    final=parsed.thought or reply,
                    steps=step,
                    tool_calls=tool_calls,
                    ok=True,
                    history=history,
                )

            # 4) 運行工具，把結果作為「觀察」寫回歷史
            call = parsed.toolcall
            result = self.tools.run_tool(call.name, call.args)
            tool_calls += 1
            self._log(f"│ ⚙ {call.name} {call.args}", _CYAN)
            self._log(f"│ ↳ {_preview(result)}", _DIM)
            history.append(_user_msg(format_tool_result(call.name, result)))

        # 5) 步數耗盡：寧可誠實失敗，也不讓 agent 無限燒錢
        return RunResult(
            final="已達到步數上限，未能給出最終回答。",
            steps=self.max_steps,
            tool_calls=tool_calls,
            ok=False,
            error="max_steps",
            history=history,
        )

    # ---------- 內部 ----------

    def _log(self, text: str, code: str) -> None:
        if self.verbose:
            print(_c(text, code))
