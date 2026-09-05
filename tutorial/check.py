#!/usr/bin/env python3
"""MiniHarness 动手营检查器。

用法：
    python3 tutorial/check.py        # 进度总览：哪几步过了、卡在哪
    python3 tutorial/check.py 3      # 只验收第 3 步（失败会给出详细提示）

规则：tutorial/my_harness.py 由你跟着 steps/ 一步一步写出来；
     检查器只验收「行为」是否符合规格，不关心你怎么实现。
     唯一的禁令：不许 import miniharness——那是毕业之后回去对照的
     参考源码，不是起点（检查器会拦截）。
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TARGET = Path(__file__).resolve().parent / "my_harness.py"


def _c(text: str, code: str) -> str:
    import os
    if os.environ.get("NO_COLOR"):
        return text
    return f"\033[{code}m{text}\033[0m"


# ----------------------------------------------------------- 加载学习者代码

def load_learner():
    if not TARGET.exists():
        print(_c("还没有创建 tutorial/my_harness.py。", "31"))
        print("从第 1 步开始：打开 tutorial/steps/step-01-loop.md，跟着写，写完跑：")
        print("    python3 tutorial/check.py 1")
        sys.exit(1)
    source = TARGET.read_text(encoding="utf-8")
    if re.search(r"\b(?:from|import)\s+miniharness\b", source):
        print(_c("🚫 动手营规则：my_harness.py 不许 import miniharness。", "31"))
        print("   自己写出来的才叫会了；参考实现留在 solutions/ 里等你卡住时对照。")
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("my_harness", TARGET)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        print(_c("my_harness.py 无法导入（语法错误，或顶层代码抛了异常）：", "31"))
        traceback.print_exc(limit=3)
        sys.exit(1)
    return module


# ----------------------------------------------------------- 考场夹具（与学习者代码无关）

from miniharness.tools import make_builtin_tools  # noqa: E402 —— 只用来搭考场


def _fresh_ws(prefix: str = "mh-lab-") -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))


def _put(ws: Path, rel: str, content: str) -> None:
    reply = make_builtin_tools(ws).run_tool("write_file", {"path": rel, "content": content})
    assert reply.startswith("OK"), reply


CORE_SRC = (
    '"""核心逻辑。"""\n'
    "\n"
    "\n"
    "def scale(value, factor):\n"
    "    # TODO: 邊界值校驗\n"
    "    return value * factor\n"
    "\n"
    "\n"
    "def clamp(value, low, high):\n"
    "    # TODO: 參數順序容易搞混\n"
    "    return max(low, min(value, high))\n"
)
UTILS_SRC = (
    "def slugify(text):\n"
    "    # TODO: 處理中文與空格\n"
    "    return text.lower().replace(\" \", \"-\")\n"
)
PIPELINE_SRC = (
    '"""示例流水線。"""\n'
    "\n"
    "# TODO: 接入日誌\n"
    "STAGES = [\"extract\", \"transform\"]\n"
)
REPORT_PATHS = ("app/core.py", "app/utils.py", "scripts/pipeline.py")


def _fill_messy(ws: Path) -> None:
    _put(ws, "app/core.py", CORE_SRC)
    _put(ws, "app/utils.py", UTILS_SRC)
    _put(ws, "scripts/pipeline.py", PIPELINE_SRC)
    _put(ws, "notes.txt", "週末記得整理 TODO 清單（本文件不是 .py，不應被統計）\n")
    _put(ws, "README.md", "# 示例工作區\n")


def _messy_ws() -> Path:
    ws = _fresh_ws()
    _fill_messy(ws)
    return ws


GRADUATION_PROMPT = ("找出工作區裡所有包含 TODO 標記的 .py 文件，"
                     "把清單寫入 REPORT.md（每行一條，含文件路徑）。")


class _Spy:
    """探针大脑：按剧本回答，同时量出每次「喂给它的历史有多大」。"""

    def __init__(self, lines):
        self._lines = list(lines)
        self._i = 0
        self.sizes = []

    def generate(self, messages):
        self.sizes.append(sum(len(m["content"]) for m in messages))
        line = self._lines[self._i] if self._i < len(self._lines) else "（没词了）"
        self._i += 1
        return line


def _boom_check(ws, res):
    raise RuntimeError("checker 自己炸了")


# ----------------------------------------------------------- 各步检查

def expect(cond, msg):
    if not cond:
        raise AssertionError(msg)


def expect_raises(fn, msg):
    try:
        fn()
    except Exception:
        return
    raise AssertionError(msg)


LIST_DIR_CALL = '```toolcall\n{"tool": "list_dir", "args": {}}\n```'


def s1_script_brain(L):
    brain = L.ScriptBrain(["甲", "乙"])
    expect(brain.generate([]) == "甲", "ScriptBrain 应按顺序返回台词：第一句应为 '甲'")
    expect(brain.generate([]) == "乙", "第二次 generate 应返回 '乙'")
    expect(brain.generate([]) is None, "台词耗尽时 generate 应返回 None（第 1 步临时的『说完了』信号）")


def s1_run_agent_basic(L):
    result = L.run_agent(L.ScriptBrain(["你好"]), "打扫卫生")
    expect(isinstance(result, dict), f"run_agent 应返回 dict，得到 {type(result).__name__}")
    expect(result["final"] == "你好",
           f"final 应为最后一句台词 '你好'，得到 {result.get('final')!r}")
    expect(result["steps"] == 1, f"steps 应为 1（消耗了一句台词），得到 {result.get('steps')}")


def s1_run_agent_history(L):
    result = L.run_agent(L.ScriptBrain(["a"]), "打扫卫生")
    history = result["history"]
    expect(isinstance(history, list) and len(history) == 3,
           f"history 应为 [system, user, assistant] 共 3 条，得到 {len(history) if isinstance(history, list) else type(history)}")
    expect(history[0]["role"] == "system", "history[0] 的 role 应为 'system'")
    expect(any(m["role"] == "user" and "打扫卫生" in m["content"] for m in history[:2]),
           "history 里应有一条 user 消息包含任务文本")


def s1_max_steps(L):
    # 用 toolcall 台词撑满预算：无围栏的台词在协议到位后会被当成最终回答。
    result = L.run_agent(L.ScriptBrain([LIST_DIR_CALL] * 6), "t", max_steps=3)
    expect(result["steps"] == 3, f"max_steps=3 时应恰好跑 3 步停下，得到 {result['steps']}")
    expect(bool(result["final"]), "停下时 final 应有内容")


def s2_format(L):
    text = L.format_toolcall("list_dir", {"path": "."})
    expect("```toolcall" in text, f"输出应包含 ```toolcall 围栏，得到：{text[:60]!r}")
    parsed = L.parse_reply(text)
    expect(parsed["toolcall"] is not None, "自己 format 的调用应能被自己的 parse_reply 解析出来")
    expect(parsed["toolcall"]["name"] == "list_dir" and parsed["toolcall"]["args"] == {"path": "."},
           f"解析出的 name/args 应与输入一致，得到 {parsed['toolcall']}")


def s2_parse_final(L):
    parsed = L.parse_reply("任务完成，报告已寫入 REPORT.md。")
    expect(parsed["toolcall"] is None, "没有 toolcall 围栏时，toolcall 应为 None（最终回答）")
    expect("REPORT.md" in parsed["thought"], "thought 应保留围栏之外的正文")


def s2_parse_call(L):
    text = 'Thought: 看目錄。\n```toolcall\n{"tool": "list_dir", "args": {"path": "."}}\n```'
    parsed = L.parse_reply(text)
    expect(parsed["toolcall"]["name"] == "list_dir", f"应解析出 list_dir，得到 {parsed['toolcall']}")
    expect(parsed["toolcall"]["args"] == {"path": "."}, "args 应为 {'path': '.'}")
    expect("看目錄" in parsed["thought"] and "```" not in parsed["thought"],
           "thought 应为围栏之外的文字，且不含围栏记号")


def s2_parse_bad(L):
    expect_raises(lambda: L.parse_reply("```toolcall\n{oops\n```"),
                  "toolcall 里是坏 JSON 时应抛异常（自定义 BadToolCall 之类）")
    expect_raises(lambda: L.parse_reply('```toolcall\n{"args": {}}\n```'),
                  "缺少 'tool' 键时应抛异常")
    expect_raises(lambda: L.parse_reply('```toolcall\n{"tool": "x", "args": [1]}\n```'),
                  "'args' 不是对象时应抛异常")


def s3_make_tools(L):
    tools = L.make_tools(_fresh_ws())
    expect(isinstance(tools, dict) and "list_dir" in tools,
           f"make_tools 应返回包含 'list_dir' 的 dict，得到 {sorted(tools) if isinstance(tools, dict) else type(tools).__name__}")


def s3_list_dir(L):
    ws = _fresh_ws()
    _put(ws, "a.txt", "hi")
    _put(ws, "sub/b.txt", "")
    out = L.run_tool(L.make_tools(ws), "list_dir", {})
    expect("a.txt" in out and "sub" in out, f"list_dir 应列出文件与子目录，得到：{out[:80]!r}")
    empty = L.run_tool(L.make_tools(_fresh_ws()), "list_dir", {})
    expect(isinstance(empty, str), "空目录也应返回字符串（如 '(空目錄)'），不要抛异常")


def s3_unknown_tool(L):
    out = L.run_tool(L.make_tools(_fresh_ws()), "nope", {})
    expect(out.startswith("ERROR"), f"未知工具应返回以 ERROR 开头的文本，得到 {out[:60]!r}")


def s3_error_and_truncate(L):
    tools = L.make_tools(_fresh_ws())

    def boom(**kwargs):
        raise RuntimeError("炸了")

    tools["boom"] = boom
    expect(L.run_tool(tools, "boom", {}).startswith("ERROR"),
           "工具抛异常时应降级为 ERROR 文本，而不是把异常抛出去")
    tools["long"] = lambda **kwargs: "x" * 999
    out = L.run_tool(tools, "long", {})
    expect("截斷" in out and len(out) <= 500,
           f"超长输出应截断（默认上限 400 字符左右）且提示包含『截斷』字样，得到长度 {len(out)}")


def s3_loop_with_tools(L):
    ws = _fresh_ws()
    _put(ws, "a.txt", "hi")
    result = L.run_agent(L.ScriptBrain([LIST_DIR_CALL, "看完了"]), "看看",
                         tools=L.make_tools(ws))
    expect(result["final"] == "看完了", f"第二轮无 toolcall，final 应为 '看完了'，得到 {result['final']!r}")
    expect(result["steps"] == 2, f"steps 应为 2，得到 {result['steps']}")
    expect(result["tool_calls"] == 1,
           f"tool_calls 应为 1（run_agent 的返回 dict 需要有这个键），得到 {result.get('tool_calls')}")
    expect(any("TOOL RESULT (list_dir)" in m["content"] for m in result["history"]),
           "观察应以 'TOOL RESULT (工具名):' 开头写回 history")


def s4_guard(L):
    ws = _fresh_ws()
    p = L.guard_path(ws, "a.txt")
    expect(Path(p).resolve().is_relative_to(ws.resolve()), "正常路径应返回 workspace 内的 Path")
    expect_raises(lambda: L.guard_path(ws, "../escape.txt"), "../ 逃逸应抛异常")


def s4_read_write(L):
    tools = L.make_tools(_fresh_ws())
    out = L.run_tool(tools, "write_file", {"path": "sub/dir/f.txt", "content": "hi"})
    expect(out.startswith("OK"), f"write_file 成功应返回 OK 开头的回执，得到 {out[:60]!r}")
    expect(L.run_tool(tools, "read_file", {"path": "sub/dir/f.txt"}) == "hi",
           "写入后 read_file 应原样读回 'hi'（且自动创建了父目录）")


def s4_escape_via_tool(L):
    out = L.run_tool(L.make_tools(_fresh_ws()), "read_file", {"path": "../x.txt"})
    expect(out.startswith("ERROR"), "越界读取应被 guard 拦下并返回 ERROR 文本")


def s4_loop_files(L):
    tools = L.make_tools(_fresh_ws())
    script = ['```toolcall\n{"tool": "write_file", "args": {"path": "notes/f.txt", "content": "abc"}}\n```',
              '```toolcall\n{"tool": "read_file", "args": {"path": "notes/f.txt"}}\n```',
              "done"]
    result = L.run_agent(L.ScriptBrain(script), "寫並讀", tools=tools)
    expect(result["steps"] == 3 and result["tool_calls"] == 2,
           f"写+读+收尾应为 3 步 2 次调用，得到 steps={result['steps']}, tool_calls={result['tool_calls']}")
    expect("abc" in "".join(m["content"] for m in result["history"]), "读回的内容应出现在观察里")


def s5_self_repair(L):
    bad = "```toolcall\n{oops\n```"
    result = L.run_agent(L.ScriptBrain([bad, "修好了"]), "t", tools=L.make_tools(_fresh_ws()))
    expect(result["final"] == "修好了",
           f"解析失败后循环应继续，final 应为 '修好了'，得到 {result['final']!r}")
    expect(result["steps"] == 2, f"坏调用也算一步：steps 应为 2，得到 {result['steps']}")
    joined = "".join(m["content"] for m in result["history"])
    expect("ERROR" in joined, "应把解析错误作为含 ERROR 的用户消息喂回 history（自我修复的起点）")


def s6_fit_small(L):
    history = [{"role": "system", "content": "s"}, {"role": "user", "content": "t"},
               {"role": "assistant", "content": "a"}, {"role": "user", "content": "o"}]
    fitted = L.fit_history(history, 1000)
    expect([m["content"] for m in fitted] == [m["content"] for m in history],
           "预算内的历史应原样返回")


def _big_history():
    history = [{"role": "system", "content": "sys"}, {"role": "user", "content": "task-text"}]
    for i in range(6):
        history.append({"role": "assistant", "content": f"call {i} " + "x" * 300})
        history.append({"role": "user", "content": f"result {i} " + "y" * 300})
    return history


def s6_fit_big(L):
    history = _big_history()
    fitted = L.fit_history(history, 2000)
    size = sum(len(m["content"]) for m in fitted)
    expect(size <= 2000, f"裁剪后应 ≤ max_chars=2000，得到 {size}")
    expect(fitted[0]["role"] == "system" and "task-text" in fitted[1]["content"],
           "系统提示与任务消息不能被裁掉")
    expect(fitted[-1]["content"].startswith("result 5") and fitted[-2]["content"].startswith("call 5"),
           "最新的 (调用, 观察對) 必須完整保留")
    expect(any("裁剪" in m["content"] for m in fitted[2:-2]),
           "发生丢弃时应留下带『裁剪』字样的占位说明")
    body = [m for m in fitted[2:] if "裁剪" not in m["content"]]
    roles = [m["role"] for m in body]
    expect(roles == ["assistant", "user"] * (len(roles) // 2) and len(roles) % 2 == 0,
           "除占位说明外，消息必须仍按 (assistant, user) 成对排列，不能出现孤儿调用")


def s6_fit_in_loop(L):
    tools = L.make_tools(_fresh_ws())
    tools["spam"] = lambda **kwargs: "z" * 400
    spam_call = '```toolcall\n{"tool": "spam", "args": {}}\n```'
    spy = _Spy([spam_call] * 12 + ["done"])
    L.run_agent(spy, "t", tools=tools, max_steps=15, max_chars=3000)
    expect(spy.sizes[-1] <= 3000,
           f"开启 max_chars 后，喂给大脑的历史应 ≤3000 字符，实测 {spy.sizes[-1]} —— "
           "run_agent 需要在每次 generate 前调用 fit_history")
    spy2 = _Spy([spam_call] * 12 + ["done"])
    L.run_agent(spy2, "t", tools=tools, max_steps=15)
    expect(spy2.sizes[-1] > 4000, "不传 max_chars 时不应裁剪（同一场景对比）")


def s7_run_eval(L):
    calls = []

    def factory():
        calls.append(1)
        return _Spy(["ok"])

    tasks = [
        {"name": "pass", "prompt": "p", "setup": lambda ws: None,
         "check": lambda ws, res: (res["final"] == "ok", "")},
        {"name": "fail", "prompt": "p", "setup": lambda ws: None,
         "check": lambda ws, res: ((ws / "REPORT.md").exists(), "REPORT.md 应存在")},
        {"name": "broken-check", "prompt": "p", "setup": lambda ws: None,
         "check": _boom_check},
    ]
    rate = L.run_eval(tasks, factory)
    expect(isinstance(rate, float) and abs(rate - 1 / 3) < 1e-9,
           f"三个任务（过 / 不过 / checker 异常算 FAIL）通过率应为 1/3，得到 {rate}")
    expect(len(calls) == 3, "每个任务都应调用一次 brain_factory 造新大脑")


def s7_fresh_workspace(L):
    seen = []

    def make_setup(marker):
        def setup(ws):
            seen.append(ws)
            _put(ws, "mark.txt", marker)
        return setup

    def make_check(marker):
        # 规格：check 必须返回 (bool, 说明) 二元组
        return lambda ws, res: ((ws / "mark.txt").read_text(encoding="utf-8") == marker, "")

    tasks = [{"name": "a", "prompt": "p", "setup": make_setup("A"), "check": make_check("A")},
             {"name": "b", "prompt": "p", "setup": make_setup("B"), "check": make_check("B")}]
    rate = L.run_eval(tasks, lambda: _Spy(["ok"]))
    expect(rate == 1.0 and len(seen) == 2,
           f"每个任务应拿到独立的新工作区，互不串味（rate={rate}，工作区数={len(seen)}）")


def s8_search_tool(L):
    out = L.run_tool(L.make_tools(_messy_ws()), "search", {"pattern": "TODO", "glob": "*.py"})
    expect("app/core.py" in out and "scripts/pipeline.py" in out,
           f"search 应命中 .py 里的 TODO（输出形如 'path:line: text'），得到：{out[:100]!r}")
    expect("notes.txt" not in out, "glob=*.py 时不应命中 notes.txt")


def s8_graduation(L):
    ws = _messy_ws()
    result = L.run_agent(L.RuleBrain(), GRADUATION_PROMPT,
                         tools=L.make_tools(ws), max_steps=12)
    report = ws / "REPORT.md"
    expect(report.exists(),
           f"你的 RuleBrain 应在 {result['steps']} 步内写出 REPORT.md"
           f"（final={result.get('final', '')[:40]!r}）")
    text = report.read_text(encoding="utf-8")
    missing = [p for p in REPORT_PATHS if p not in text]
    expect(not missing, f"REPORT.md 缺少文件：{missing}")
    expect("notes.txt" not in text, "notes.txt 不是 .py，不该出现在报告里")


def s8_graduation_via_eval(L):
    def report_check(ws, res):
        report = ws / "REPORT.md"
        text = report.read_text(encoding="utf-8") if report.exists() else ""
        ok = all(p in text for p in REPORT_PATHS) and "notes.txt" not in text
        return ok, ("报告内容完整" if ok else "报告缺失文件或混入了诱饵")

    tasks = [{"name": "todo-report", "prompt": GRADUATION_PROMPT,
              "setup": _fill_messy, "check": report_check}]
    rate = L.run_eval(tasks, L.RuleBrain)
    expect(rate == 1.0, f"用自己的 run_eval 跑毕业任务应通过（rate={rate}）")


STEPS = [
    (1, "循環與台詞大腦", [s1_script_brain, s1_run_agent_basic, s1_run_agent_history, s1_max_steps]),
    (2, "協議：會說「調工具」", [s2_format, s2_parse_final, s2_parse_call, s2_parse_bad]),
    (3, "工具執行", [s3_make_tools, s3_list_dir, s3_unknown_tool, s3_error_and_truncate, s3_loop_with_tools]),
    (4, "路徑守衛與文件讀寫", [s4_guard, s4_read_write, s4_escape_via_tool, s4_loop_files]),
    (5, "自我修復", [s5_self_repair]),
    (6, "上下文預算", [s6_fit_small, s6_fit_big, s6_fit_in_loop]),
    (7, "迷你評測", [s7_run_eval, s7_fresh_workspace]),
    (8, "畢業：規則大腦 + TODO 報告", [s8_search_tool, s8_graduation, s8_graduation_via_eval]),
]


def run_step(number: int, L, verbose: bool = True):
    title, checks = next((n, t, c) for n, t, c in STEPS if n == number)[1:]
    if verbose:
        print(_c(f"—— 第 {number} 步 · {title} ——", "36"))
    passed = 0
    for fn in checks:
        try:
            fn(L)
            passed += 1
            if verbose:
                print("  " + _c("✓", "32") + f" {fn.__name__.split('_', 1)[1]}")
        except AssertionError as exc:
            if verbose:
                print("  " + _c("✗", "31") + f" {fn.__name__.split('_', 1)[1]}")
                print("      " + _c(str(exc), "2"))
        except AttributeError as exc:
            passed_label = f"my_harness.py 还缺：{exc}"
            if verbose:
                print("  " + _c("✗", "31") + f" {fn.__name__.split('_', 1)[1]}")
                print("      " + _c(passed_label + "（回看步骤文档里的规格）", "2"))
        except Exception as exc:  # noqa: BLE001
            if verbose:
                print("  " + _c("✗", "31") + f" {fn.__name__.split('_', 1)[1]}")
                print("      " + _c(f"检查器异常：{type(exc).__name__}: {exc}", "2"))
    if verbose:
        print(f"  小计 {passed}/{len(checks)}\n")
    return passed, len(checks)


def main() -> int:
    global TARGET
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", nargs="?", type=int, choices=range(1, 9))
    parser.add_argument("--submission", type=Path, default=TARGET,
                        help="要驗收的作業檔；不會改寫此檔")
    args = parser.parse_args()
    TARGET = args.submission.resolve()
    L = load_learner()
    if args.step is not None:
        number = args.step
        if not any(n == number for n, _, _ in STEPS):
            print(f"没有第 {number} 步。有效步骤：{', '.join(str(n) for n, _, _ in STEPS)}")
            sys.exit(1)
        passed, total = run_step(number, L)
        return 0 if passed == total else 1

    print("== MiniHarness 动手营 · 进度总览 ==\n")
    first_fail = None
    for number, title, checks in STEPS:
        passed, total = run_step(number, L, verbose=False)
        mark = _c("✓", "32") if passed == total else _c(f"{passed}/{total}", "33" if passed else "31")
        print(f"  第 {number} 步  {title:<16} {mark}")
        if passed < total and first_fail is None:
            first_fail = number
    print()
    if first_fail is None:
        print(_c("🎓 8/8 全过——毕业了！你的 my_harness.py 已具备 harness 的全部核心件。", "32"))
        print("   下一步：")
        print("   1) 对照 miniharness/ 包源码（loop → protocol → tools → context → brains）；")
        print("   2) steps/step-09-bonus：给大脑接上真模型；")
        print("   3) 给 docs/07 的评测集加一个自己的任务。")
    else:
        print(f"当前卡在：第 {first_fail} 步。打开 tutorial/steps/ 对应文档修改，然后：")
        print(f"    python3 tutorial/check.py {first_fail}")

    return 0 if first_fail is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
