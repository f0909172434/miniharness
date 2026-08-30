"""內置評測任務與「會做題」的腳本化大腦（配合 demos/demo_eval.py 使用）。

三個任務分別考察 harness 的不同側面：
- todo-report：多步規劃 + 工具鏈（todo → list_dir → grep → write_file）；
- fix-syntax：讀代碼 → 定位 → 修改 → 驗證（經典 debug 小循環）；
- find-token：在嵌套目錄裡偵查（考察探索式工具使用）。

mock_script() 為每個任務提供一份腳本化解法，讓評測在**離線**狀態下
也能驗證 harness 機制本身。其中用到了「可調用項」：劇本會讀上一輪的
工具結果再決定下一步——這正是循環賦予模型能動性的縮影。
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Union

from .eval import Task
from .llm import Message
from .protocol import format_toolcall
from .tools import make_builtin_tools

# 課題里埋的「答案」常量，checker 與 mock 劇本共用，保證兩邊不打架。
PLANTED_TOKEN = "mh-demo-9f27c1"
REPORT_PATHS = ("app/core.py", "app/utils.py", "scripts/pipeline.py")

TODO_TEXT = "[ ] 查看目錄結構\n[ ] 搜索 TODO 標記\n[ ] 統計並寫入 REPORT.md"

BROKEN_SOURCE = (
    'def add(a, b):\n'
    '    return a + b\n'
    '\n'
    '\n'
    'if __name__ == "__main__":\n'
    '    print(add(1, 2)\n'
)
FIXED_SOURCE = BROKEN_SOURCE.replace("print(add(1, 2)\n", "print(add(1, 2))\n")


# --------------------------------------------------------------- 工作區搭建

# 一個「亂但真實」的小工作區：TODO 散落、有誘餌文件、有嵌套目錄。
_FIXTURE_FILES: Dict[str, str] = {
    "app/__init__.py": "",
    "app/core.py": (
        '"""核心邏輯。"""\n'
        '\n'
        '\n'
        'def scale(value, factor):\n'
        '    # TODO: 加入邊界值校驗\n'
        '    return value * factor\n'
        '\n'
        '\n'
        'def clamp(value, low, high):\n'
        '    # TODO: 參數順序容易搞混，改成關鍵字參數\n'
        '    return max(low, min(value, high))\n'
    ),
    "app/utils.py": (
        'def slugify(text):\n'
        '    # TODO: 處理中文與空格\n'
        '    return text.lower().replace(" ", "-")\n'
    ),
    "scripts/pipeline.py": (
        '"""示例流水線。"""\n'
        '\n'
        '# TODO: 接入日誌\n'
        'STAGES = ["extract", "transform"]\n'
    ),
    # 誘餌：內容含 TODO 但不是 .py，正確的 agent 不應把它算進去。
    "notes.txt": "週末記得整理 TODO 清單（本文件不是 .py，不應被統計）\n",
    "README.md": "# 示例工作區\n",
}


def _materialize(ws: Path, files: Dict[str, str]) -> None:
    """搭建夾具工作區：直接借用 harness 自己的 write_file 工具（自舉）。

    好處有二：夾具寫入與 agent 走**完全相同**的路徑守衛
    （tools.resolve_path 的越界檢查），夾具若有非法路徑當場失敗；
    同時這也是一次對 write_file 的隱性測試——考場用考官的捲尺來量。
    """
    fixtures = make_builtin_tools(ws)
    for relative, content in files.items():
        reply = fixtures.run_tool("write_file", {"path": relative, "content": content})
        if not reply.startswith("OK"):
            raise RuntimeError(f"搭建夾具失敗：{relative} → {reply}")


def make_demo_workspace(ws: Path) -> None:
    _materialize(ws, _FIXTURE_FILES)


def _setup_broken(ws: Path) -> None:
    _materialize(ws, {**_FIXTURE_FILES, "broken.py": BROKEN_SOURCE})


def _setup_token(ws: Path) -> None:
    _materialize(ws, {
        **_FIXTURE_FILES,
        "src/config/prod.py": f'API_TOKEN = "{PLANTED_TOKEN}"  # 不要提交到 git\n',
    })


# --------------------------------------------------------------- 驗收 checker

def _check_report(ws: Path, result) -> Tuple[bool, str]:
    report = ws / "REPORT.md"
    if not report.exists():
        return False, "REPORT.md 不存在"
    text = report.read_text(encoding="utf-8")
    missing = [p for p in REPORT_PATHS if p not in text]
    if missing:
        return False, f"報告缺少文件：{missing}"
    return True, f"報告包含全部 {len(REPORT_PATHS)} 個文件"


def _check_fixed(ws: Path, result) -> Tuple[bool, str]:
    src = ws / "broken.py"
    if not src.exists():
        return False, "broken.py 不存在"
    try:
        # 用語法樹驗收，而不是比對文本——agent 怎麼改的無所謂，解析通了就行。
        ast.parse(src.read_text(encoding="utf-8"), filename="broken.py")
    except SyntaxError as exc:
        return False, f"仍有語法錯誤：{exc}"
    return True, "語法檢查通過"


def _check_token(ws: Path, result) -> Tuple[bool, str]:
    if PLANTED_TOKEN in result.final:
        return True, "最終回答包含正確 token"
    return False, f"最終回答未包含 token（前 120 字：{result.final[:120]!r}）"


# --------------------------------------------------------------- 任務集

TASKS = [
    Task(
        name="todo-report",
        prompt="找出工作區裡所有包含 TODO 標記的 .py 文件，把清單寫入 REPORT.md"
               "（每行一條，格式如 `- 路徑（N 處）：說明`）。",
        setup=make_demo_workspace,
        check=_check_report,
    ),
    Task(
        name="fix-syntax",
        prompt="工作區裡的 broken.py 有語法錯誤，請修復它。",
        setup=_setup_broken,
        check=_check_fixed,
    ),
    Task(
        name="find-token",
        prompt="工作區某處藏著一個 API token，找到它，並在最終回答裡給出完整的 token 值。",
        setup=_setup_token,
        check=_check_token,
    ),
]


# --------------------------------------------------------------- Mock 劇本

def mock_script(task_name: str) -> List[Union[str, object]]:
    """返回指定任務的腳本化解法（MockLLM 劇本）。"""
    if task_name == "todo-report":
        return _report_script()
    if task_name == "fix-syntax":
        return _fix_script()
    if task_name == "find-token":
        return _token_script()
    raise KeyError(f"沒有為任務 '{task_name}' 準備 mock 劇本")


def _report_script() -> list:
    return [
        "Thought: 收到任務。先把計劃寫進 todo，防止漏步驟。\n"
        + format_toolcall("todo", {"action": "write", "content": TODO_TEXT}),
        "Thought: 先遞歸看一下工作區裡有什麼。\n"
        + format_toolcall("list_dir", {"path": ".", "recursive": True}),
        "Thought: 結構清楚了。用 grep 在所有 .py 文件裡搜 TODO 標記。\n"
        + format_toolcall("run_bash", {"command": 'grep -rn "TODO" --include=*.py .'}),
        _write_report_turn,  # 反應式：讀 grep 結果，統計後再寫報告
        "Thought: 報告已寫入，最後確認一遍 todo。\n"
        + format_toolcall("todo", {"action": "show"}),
        "Thought: 三步計劃全部完成，可以收尾了。\n"
        "\n最終回答：我在工作區的 3 個 Python 文件裡共找到 4 處 TODO 標記，"
        "逐條清單已寫入 REPORT.md；notes.txt 中的「TODO」字樣因不是 .py 文件已正確排除。",
    ]


def _write_report_turn(messages: List[Message]) -> str:
    grep_out = messages[-1]["content"]
    found: dict = {}
    for line in grep_out.splitlines():
        if not line.startswith("./"):
            continue
        path, _, rest = line.split(":", 2)
        found.setdefault(path[2:], []).append(rest.strip())
    if not found:
        return (
            "Thought: grep 沒有命中，可能標記大小寫不同，換不區分大小寫的模式再試。\n"
            + format_toolcall("run_bash", {"command": "grep -rni todo --include=*.py ."})
        )
    lines = []
    for path, hits in found.items():
        notes = "；".join(h.split("TODO:", 1)[-1].strip() or "(無說明)" for h in hits)
        lines.append(f"- {path}（{len(hits)} 處）：{notes}")
    report = "# TODO 報告\n\n" + "\n".join(lines) + "\n"
    return (
        "Thought: 統計完成，把報告寫入 REPORT.md。\n"
        + format_toolcall("write_file", {"path": "REPORT.md", "content": report})
    )


def _fix_script() -> list:
    return [
        "Thought: 先讀源碼，定位語法錯誤。\n"
        + format_toolcall("read_file", {"path": "broken.py"}),
        _fix_turn,  # 反應式：確認讀到的內容後才動手改
        "Thought: 已修復，讓白名單裡的語法檢查命令做最終裁決。\n"
        + format_toolcall("run_bash", {"command": "python3 -m py_compile broken.py"}),
        "Thought: 語法檢查退出碼為 0，說明已恢復。\n"
        "\n最終回答：broken.py 的錯誤是最後一行 print(add(1, 2) 少了一個右括號，已補上；"
        "語法檢查驗證通過。",
    ]


def _fix_turn(messages: List[Message]) -> str:
    content = messages[-1]["content"]
    if "print(add(1, 2)" not in content:
        return (
            "Thought: 讀到的內容和預期不符，再讀一次確認。\n"
            + format_toolcall("read_file", {"path": "broken.py"})
        )
    return (
        "Thought: 找到了——最後一行 print(add(1, 2) 少一個右括號，補上它。\n"
        + format_toolcall("write_file", {"path": "broken.py", "content": FIXED_SOURCE})
    )


def _token_script() -> list:
    return [
        "Thought: 先遞歸列出工作區，找可疑的配置文件。\n"
        + format_toolcall("list_dir", {"path": ".", "recursive": True}),
        "Thought: 結構裡有 src/config/，很像放配置的地方，直接全局搜 TOKEN。\n"
        + format_toolcall("run_bash", {"command": "grep -rn TOKEN --include=*.py ."}),
        _token_final_turn,  # 反應式：從搜索結果裡提取真實 token 值
    ]


def _token_final_turn(messages: List[Message]) -> str:
    out = messages[-1]["content"]
    match = re.search(r'"(mh-demo-[0-9a-f]+)"', out)
    token = match.group(1) if match else "(未找到)"
    return f"Thought: 找到了。\n\n最終回答：token 藏在 src/config/prod.py 裡，值是 {token}"
