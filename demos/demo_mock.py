#!/usr/bin/env python3
"""Demo 1（離線可跑）：MockLLM 扮演大腦，完整走一遍 harness。

不需要任何 API Key。重點不是模型多聰明，而是看「循環」本身：
思考 → 工具調用 → 觀察 → 再思考……直到模型不再調用工具。

    python3 demos/demo_mock.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from miniharness import Agent, ContextManager, MockLLM          # noqa: E402
from miniharness.tasks import make_demo_workspace, mock_script   # noqa: E402
from miniharness.tools import make_builtin_tools                 # noqa: E402


def main() -> None:
    workspace = Path(tempfile.mkdtemp(prefix="miniharness-demo-"))
    make_demo_workspace(workspace)  # 造一個「亂但真實」的考場
    print(f"工作區：{workspace}")
    print("大腦：MockLLM（腳本化，離線）\n")

    agent = Agent(
        llm=MockLLM(mock_script("todo-report")),
        tools=make_builtin_tools(workspace),
        context=ContextManager(max_chars=24000),
        max_steps=10,
        verbose=True,
    )
    result = agent.run("找出工作區裡所有包含 TODO 標記的 .py 文件，把清單寫入 REPORT.md。")

    print("\n" + "=" * 62)
    print("最終回答：", result.final)
    print(f"統計：{result.steps} 步，{result.tool_calls} 次工具調用，ok={result.ok}")

    report = workspace / "REPORT.md"
    print("\n── 產物 REPORT.md ──")
    print(report.read_text(encoding="utf-8") if report.exists() else "(未生成)")
    print(f"（工作區保留在 {workspace}，可直接查看）")


if __name__ == "__main__":
    main()
