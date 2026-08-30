"""MiniHarness：教學用最小 Agent Harness。

核心問題：在「模型」之外，還需要哪些工程件，才能把一次 API 調用
變成一個能幹活的 agent？答案是六個模塊，每個都對應課程的一章：

    protocol  協議——模型怎麼「說」要調用工具      docs/02
    tools     工具——模型的雙手與安全閘            docs/03、06
    context   上下文——歷史太長怎麼裁              docs/04
    loop      循環——把以上全部串起來的心臟        docs/01
    eval      評測——怎麼知道你的 agent 有用        docs/07
    llm       大腦——Mock 與真實 API 的統一介面     docs/01
    brains    從零造腦——規則/語言模型/模仿學習      docs/09
"""
from .context import ContextManager
from .eval import Task, run_eval
from .llm import BaseLLM, MockLLM, OpenAICompatLLM
from .loop import Agent, RunResult
from .protocol import ToolCall, parse_response
from .tools import Tool, ToolRegistry, make_builtin_tools

__version__ = "0.1.0"

__all__ = [
    "Agent",
    "BaseLLM",
    "ContextManager",
    "MockLLM",
    "OpenAICompatLLM",
    "RunResult",
    "Task",
    "Tool",
    "ToolCall",
    "ToolRegistry",
    "make_builtin_tools",
    "parse_response",
    "run_eval",
    "__version__",
]
