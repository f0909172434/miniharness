#!/usr/bin/env python3
"""Demo 3：迷你評測 harness。默認離線跑（MockLLM），--real 切換到真實 API。

    python3 demos/demo_eval.py            # 離線：驗證 harness 機制
    python3 demos/demo_eval.py --real     # 換上真模型，看真實水平
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from miniharness import Agent, MockLLM, OpenAICompatLLM, run_eval   # noqa: E402
from miniharness.tasks import TASKS, mock_script                    # noqa: E402
from miniharness.tools import make_builtin_tools                    # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="MiniHarness 迷你評測")
    parser.add_argument("--real", action="store_true", help="用真實 LLM API（需設置 OPENAI_API_KEY 等環境變量）")
    parser.add_argument("--quiet", action="store_true", help="隱藏 agent 過程日誌")
    args = parser.parse_args()

    if args.real:
        def factory(task, workspace):
            return Agent(
                llm=OpenAICompatLLM.from_env(),
                tools=make_builtin_tools(workspace),
                verbose=not args.quiet,
            )
    else:
        def factory(task, workspace):
            return Agent(
                llm=MockLLM(mock_script(task.name)),
                tools=make_builtin_tools(workspace),
                verbose=not args.quiet,
            )

    run_eval(factory, TASKS)

    if not args.real:
        print("\n提示：MockLLM 是「開卷考」，驗證的是 harness 機制本身是否通暢。")
        print("加上 --real 換成真模型，才能回答「我的 harness 讓模型變強了嗎」。")


if __name__ == "__main__":
    main()
