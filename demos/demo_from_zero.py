#!/usr/bin/env python3
"""Demo 4：從 0 開始——沒有 API Key、沒有預訓練模型，造出自己的 agent。

同一個 harness（loop.py 一行不改），依次給它換四種大腦：

    [1] NgramBrain   自己「訓練」的字符級語言模型（統計 n-元）
    [2] RuleBrain    手寫規則策略（沒有模型，也有 agent）
    [3] PolicyBrain  模仿學習訓練出的 softmax 策略（純 Python，毫秒級）
    [4] 真實 LLM     （留給 demo_cli.py，同一個插槽）

跑法：python3 demos/demo_from_zero.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from miniharness import Agent, run_eval                          # noqa: E402
from miniharness.brains import (                                 # noqa: E402
    NgramBrain,
    PolicyBrain,
    RuleBrain,
    build_corpus,
    collect_trajectories,
)
from miniharness.tasks import TASKS, mock_script                 # noqa: E402
from miniharness.tools import make_builtin_tools                 # noqa: E402


def make_agent_factory(brain):
    def factory(task, workspace):
        return Agent(
            llm=brain,
            tools=make_builtin_tools(workspace),
            verbose=False,
            max_steps=10,
        )
    return factory


def main() -> None:
    print("=" * 62)
    print("場景：沒有 API Key、沒有預訓練模型，只有 Python 標準庫。")
    print("同一個 harness（loop.py 一行不改），換不同的大腦上崗。")
    print("=" * 62)

    # ---- [1] 自己訓練一個語言模型 --------------------------------
    corpus = build_corpus(TASKS, mock_script)
    lm = NgramBrain(order=5, seed=0).fit(corpus)
    print(f"\n[1] NgramBrain：字符級 5-元語言模型，語料 {len(corpus)} 字符（統計計數訓練）")
    print("    它生成的文字（節選）：")
    print("      " + lm.sample(120).replace("\n", "\n      "))
    rate_lm = run_eval(make_agent_factory(lm), TASKS)
    print(f"    → 成績 {rate_lm:.0%}：會『說話』，但不會說協議語言。\n")

    # ---- [2] 手寫規則 --------------------------------------------
    print("[2] RuleBrain：if-elif 手寫規則策略（零學習）")
    rate_rule = run_eval(make_agent_factory(RuleBrain()), TASKS)
    print(f"    → 成績 {rate_rule:.0%}：沒有模型，也有 agent——但不會學新題。\n")

    # ---- [3] 模仿學習 --------------------------------------------
    samples = collect_trajectories(TASKS, mock_script)
    brain = PolicyBrain().fit(samples)
    print(f"[3] PolicyBrain：從 {len(samples)} 條專家軌跡做模仿學習"
          f"（softmax 策略，純 Python，毫秒級）")
    rate_policy = run_eval(make_agent_factory(brain), TASKS)
    print(f"    → 成績 {rate_policy:.0%}：『下一步調什麼工具』可以被學出來。\n")

    # ---- 結論 ----------------------------------------------------
    print("=" * 62)
    print(f"{'大腦':<26}{'成績':>6}   一句話")
    print("-" * 62)
    rows = [
        ("NgramBrain（自訓語言模型）", rate_lm, "語言能力 ≠ 指令跟隨能力"),
        ("RuleBrain（手寫規則）", rate_rule, "熟題滿分，永不會新題"),
        ("PolicyBrain（模仿學習）", rate_policy, "決策可學習；泛化才是稀缺品"),
    ]
    for name, rate, note in rows:
        print(f"{name:<26}{rate:>7.0%}   {note}")
    print("-" * 62)
    print("結論：harness 是常量，大腦是變量。真 LLM 的價值，")
    print("      是一個『什麼任務都見過』的泛化大腦——插槽已經留好：")
    print("      python3 demos/demo_cli.py")


if __name__ == "__main__":
    main()
