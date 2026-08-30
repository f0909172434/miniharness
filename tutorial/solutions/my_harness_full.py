"""MiniHarness 动手营 · 完整参考实现（tutorial/my_harness.py 的终点长这样）

用法：先自己写；卡住超过 30 分钟，再对照「当前卡住的那一段」。
各段标题与 tutorial/steps/ 一一对应。全程只依赖标准库。
"""
import json
import re
import tempfile
from pathlib import Path

TOOLCALL_FENCE = "```toolcall"
MAX_OUTPUT = 400
_FENCE_RE = re.compile(r"```toolcall\s*(.*?)\s*```", re.DOTALL)


class BadToolCall(ValueError):
    """toolcall 围栏内容不合法。"""


class ToolError(Exception):
    """工具主动拒绝执行（路径越界等）。"""


# =================================================== 1) 循环与台词大脑

class ScriptBrain:
    """背台词的大脑：按顺序吐出预设回复（miniharness.MockLLM 的雏形）。

    台词耗尽返回 None——这是第 1 步临时的「说完了」信号；
    第 2 步协议到位后，「无围栏 = 最终回答」成为正式的停机方式，
    None 分支保留作兜底。
    """

    def __init__(self, lines):
        self._lines = list(lines)
        self._i = 0

    def generate(self, messages):
        if self._i >= len(self._lines):
            return None
        line = self._lines[self._i]
        self._i += 1
        return line


def run_agent(brain, task, max_steps=5, tools=None, max_chars=None):
    """AgentLoop：整个 harness 的心脏。

    循环不变量：history[2:] 永远是 (assistant, user) 成对出现。
    """
    tools = tools or {}
    history = [
        {"role": "system", "content": "你是一个运行在 my_harness 里的 agent，用工具完成任务。"},
        {"role": "user", "content": f"任务：{task}"},
    ]
    steps = 0
    tool_calls = 0
    last_reply = ""
    while steps < max_steps:
        messages = fit_history(history, max_chars) if max_chars else history
        reply = brain.generate(messages)
        if reply is None:
            break  # 大脑没词了：以最后一句台词收尾
        history.append({"role": "assistant", "content": reply})
        last_reply = reply
        steps += 1
        try:
            parsed = parse_reply(reply)
        except BadToolCall as exc:
            # 自我修复：解析失败不终止，把错误喂回去让大脑自己改。
            history.append({"role": "user",
                            "content": f"TOOL RESULT (parse):\nERROR: {exc}\n"
                                       "请重新输出一个合法的 toolcall。"})
            continue
        call = parsed["toolcall"]
        if call is None:
            return {"final": parsed["thought"] or reply, "steps": steps,
                    "tool_calls": tool_calls, "history": history}
        result = run_tool(tools, call["name"], call["args"])
        tool_calls += 1
        history.append({"role": "user",
                        "content": f"TOOL RESULT ({call['name']}):\n{result}"})
    return {"final": last_reply or "已達到步數上限，未能給出最終回答。", "steps": steps,
            "tool_calls": tool_calls, "history": history}


# =================================================== 2) 协议

def format_toolcall(name, args):
    payload = json.dumps({"tool": name, "args": args}, ensure_ascii=False)
    return f"{TOOLCALL_FENCE}\n{payload}\n```"


def parse_reply(text):
    """把回复拆成 (thought, toolcall?)。合同：无围栏 = 最终回答。"""
    match = _FENCE_RE.search(text)
    thought = _FENCE_RE.sub("", text).strip()
    if match is None:
        return {"thought": thought, "toolcall": None}
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise BadToolCall(f"toolcall 不是合法 JSON：{exc}") from exc
    if not isinstance(data, dict) or "tool" not in data:
        raise BadToolCall('toolcall 必须是 {"tool": 名字, "args": {...}}')
    args = data.get("args", {})
    if not isinstance(args, dict):
        raise BadToolCall("args 必须是对象")
    return {"thought": thought, "toolcall": {"name": str(data["tool"]), "args": args}}


# =================================================== 3) 工具执行

def run_tool(tools, name, args):
    """按名字运行工具。永不抛异常——一切错误都降级为可读的 ERROR 文本。"""
    tool = tools.get(name)
    if tool is None:
        return f"ERROR: 未知工具 '{name}'。可用：{', '.join(tools) or '(无)'}"
    try:
        output = str(tool(**args))
    except ToolError as exc:
        return f"ERROR: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: 工具内部异常 {type(exc).__name__}: {exc}"
    if len(output) > MAX_OUTPUT:
        output = output[:MAX_OUTPUT] + f"\n[……输出超過 {MAX_OUTPUT} 字符，已截斷……]"
    return output


# =================================================== 4) 路径守卫与文件读写

def guard_path(workspace, raw):
    """路径守卫：resolve 之后必须仍在 workspace 内（防 ../ 逃逸）。"""
    root = Path(workspace).resolve()
    candidate = (root / raw).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"路徑越界：'{raw}' 位於工作目錄之外")
    return candidate


def make_tools(workspace):
    """组出工具箱。macOS 注意：/var 是符号链接，workspace 先 resolve 统一基准。"""
    ws = Path(workspace).resolve()

    def t_list_dir(path=".", recursive=False):
        target = guard_path(ws, path)
        if not target.exists():
            raise ToolError(f"路徑不存在：{path}")
        if recursive:
            entries = [p.relative_to(ws).as_posix()
                       for p in sorted(target.rglob("*")) if p.is_file()][:200]
        else:
            entries = [c.relative_to(ws).as_posix() + ("/" if c.is_dir() else "")
                       for c in sorted(target.iterdir())]
        return "\n".join(entries) if entries else "(空目錄)"

    def t_read_file(path):
        p = guard_path(ws, path)
        if not p.is_file():
            raise ToolError(f"'{path}' 不是文件")
        text = p.read_text(encoding="utf-8", errors="replace")
        return text if len(text) <= 2000 else text[:2000] + "\n[……已截斷……]"

    def t_write_file(path, content):
        p = guard_path(ws, path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"OK：已寫入 {p.relative_to(ws).as_posix()}（{len(content)} 字符）"

    def t_search(pattern, glob="*.py"):
        hits = []
        for p in sorted(ws.rglob(glob)):
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            for i, line in enumerate(lines, 1):
                if pattern in line:
                    hits.append(f"{p.relative_to(ws).as_posix()}:{i}: {line.strip()}")
        return "\n".join(hits[:100]) or "(無命中)"

    return {"list_dir": t_list_dir, "read_file": t_read_file,
            "write_file": t_write_file, "search": t_search}


# =================================================== 6) 上下文预算

def fit_history(history, max_chars):
    """超预算时从最旧的 (assistant, user) 对开始丢，留占位说明。

    必须成对丢弃：单丢一半会出现「没有结果的调用」。
    """
    total = sum(len(m["content"]) for m in history)
    if total <= max_chars:
        return list(history)
    head = history[:2]
    budget = max_chars - len(head[0]["content"]) - len(head[1]["content"])
    body = history[2:]
    kept = []
    used = 0
    index = len(body)
    while index >= 2:
        pair = body[index - 2:index]
        size = sum(len(m["content"]) for m in pair)
        if used + size > budget:
            break
        kept = pair + kept
        used += size
        index -= 2
    out = list(head)
    if index > 0:
        out.append({"role": "user", "content": "[……更早的對話已被裁剪以節省上下文……]"})
    out.extend(kept)
    return out


# =================================================== 7) 迷你评测

def run_eval(tasks, brain_factory):
    """逐个任务：开新工作区 → setup → 跑 agent → check 验收 → 报分。"""
    passed = 0
    for index, task in enumerate(tasks, 1):
        ws = Path(tempfile.mkdtemp(prefix="mh-eval-"))
        task["setup"](ws)
        result = run_agent(brain_factory(), task["prompt"],
                           tools=make_tools(ws), max_steps=12)
        try:
            ok, note = task["check"](ws, result)
        except Exception as exc:  # noqa: BLE001 —— checker 坏了也算 FAIL
            ok, note = False, f"checker 自身异常：{exc}"
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {task['name']} — {note}（steps={result['steps']}）")
        if ok:
            passed += 1
    rate = passed / len(tasks) if tasks else 0.0
    print(f"總計：{passed}/{len(tasks)} 通過")
    return rate


# =================================================== 8) 毕业：规则大脑

def _prev_call(messages):
    for message in reversed(messages):
        if message["role"] == "assistant":
            try:
                return parse_reply(message["content"])["toolcall"]
            except BadToolCall:
                return None
    return None


def _last_user(messages):
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"]
    return ""


class RuleBrain:
    """规则大脑：看「上一步做了什么 + 看到了什么」，从动作表里选下一步。

    只负责决策；报告内容等「生成」由下面的组装代码机械完成——
    这正是 docs/09 说的「决策与生成分工」。
    """

    def generate(self, messages):
        prev = _prev_call(messages)
        observation = _last_user(messages)
        if prev is None:
            return format_toolcall("search", {"pattern": "TODO", "glob": "*.py"})
        if prev["name"] == "search":
            paths = []
            for line in observation.splitlines():
                if line.startswith(("TOOL RESULT", "ERROR", "[", "(無命中")):
                    continue
                path = line.split(":", 1)[0].strip()
                if path and path not in paths:
                    paths.append(path)
            report = "# TODO 報告\n\n" + "\n".join(f"- {p}" for p in paths) + "\n"
            return format_toolcall("write_file", {"path": "REPORT.md", "content": report})
        if prev["name"] == "write_file":
            return "Thought: 收工。\n\n最終回答：TODO 清單已寫入 REPORT.md。"
        return "最終回答：我不知道下一步該做什麼了。"
