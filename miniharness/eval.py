"""迷你評測 harness（對應課程 docs/07-eval.md）。

一個 Task = setup（搭工作區）+ prompt（給 agent 的任務）+ check（驗收產物）。
run_eval 逐個任務：開乾淨工作區 → 跑 agent → 跑 checker → 報 PASS/FAIL。

評測設計的兩條軍規：
1. checker 驗「產物」，不驗「過程」——過程路徑不同沒關係，東西做對了就行；
2. checker 必須確定、可重放——同一份工作區，誰來評結論都一樣。
"""
from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from .loop import Agent, RunResult

# (工作區路徑, 運行結果) -> (是否通過, 一句話說明)
Checker = Callable[[Path, RunResult], Tuple[bool, str]]


@dataclass
class Task:
    name: str
    prompt: str
    setup: Callable[[Path], None]
    check: Checker


def run_eval(
    agent_factory: Callable[[Task, Path], Agent],
    tasks: List[Task],
    root: Optional[Path] = None,
) -> float:
    """跑一整個任務集。agent_factory(task, workspace) 負責造一個新 agent。

    每個任務都在獨立的臨時工作區裡運行，互不污染。
    返回通過率（0.0 ~ 1.0）。
    """
    root = root or Path(tempfile.mkdtemp(prefix="miniharness-eval-"))
    print(f"== MiniHarness 迷你評測：{len(tasks)} 個任務，工作區根目錄 {root} ==\n")

    passed = 0
    for index, task in enumerate(tasks, 1):
        workspace = root / f"{index:02d}-{task.name}"
        workspace.mkdir(parents=True, exist_ok=True)
        task.setup(workspace)

        agent = agent_factory(task, workspace)
        result = agent.run(task.prompt)

        try:
            ok, note = task.check(workspace, result)
        except Exception as exc:  # noqa: BLE001 —— checker 壞了也算 FAIL，不能炸掉整場評測
            ok, note = False, f"checker 自身異常：{type(exc).__name__}: {exc}"

        status = "PASS" if ok else "FAIL"
        mark = "✓" if ok else "✗"
        print(f"[{status}] {mark} {task.name} — {note}（steps={result.steps}, tool_calls={result.tool_calls}）")
        if ok:
            passed += 1

    rate = passed / len(tasks) if tasks else 0.0
    print(f"\n總計：{passed}/{len(tasks)} 通過（{rate:.0%}）")
    return rate
