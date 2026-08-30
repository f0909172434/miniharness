#!/usr/bin/env python3
"""Demo 2：真實 API 的交互 REPL——把 harness 當成一個命令行 agent 用。

    export OPENAI_API_KEY=sk-...
    # 任意 OpenAI 兼容端點均可，例如：
    # export MINIHARNESS_BASE_URL=https://open.bigmodel.cn/api/paas/v4
    # export MINIHARNESS_MODEL=glm-4-flash
    python3 demos/demo_cli.py

內置命令：/quit 退出；/reset 清空工作區。
試一試：'建一個 hello.py，內容是打印 1 到 10，然後運行它驗證'。
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from miniharness import Agent, ContextManager, OpenAICompatLLM    # noqa: E402
from miniharness.tools import make_builtin_tools                   # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="MiniHarness 交互式 REPL（真實 API）")
    parser.add_argument("--workspace", default="workspace_cli", help="agent 的工作目錄（默認 ./workspace_cli）")
    args = parser.parse_args()

    try:
        llm = OpenAICompatLLM.from_env()
    except RuntimeError as exc:
        print(exc)
        print("（只想先看離線效果？跑 demos/demo_mock.py）")
        sys.exit(1)

    workspace = Path(args.workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    print(f"大腦：{llm.model} @ {llm.base_url}")
    print(f"工作區：{workspace}")
    print("輸入任務開始；/reset 清空工作區；/quit 退出。\n")

    while True:
        try:
            task = input("你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not task:
            continue
        if task == "/quit":
            break
        if task == "/reset":
            shutil.rmtree(workspace)
            workspace.mkdir(parents=True)
            print("(工作區已清空)\n")
            continue

        agent = Agent(
            llm=llm,
            tools=make_builtin_tools(workspace),
            context=ContextManager(max_chars=24000),
            max_steps=15,
        )
        result = agent.run(task)
        print(f"\nagent > {result.final}")
        print(f"（{result.steps} 步，{result.tool_calls} 次工具調用，ok={result.ok}）\n")


if __name__ == "__main__":
    main()
