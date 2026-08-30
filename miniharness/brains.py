"""從零造腦：沒有 API Key、沒有預訓練模型時，「大腦」還能是什麼（docs/09-from-zero.md）。

Agent = harness + 大腦。Part 1 的大腦是 LLM（或 MockLLM）；本章證明大腦這個
插槽可以插任何東西，只要它遵守同一份協議（```toolcall 文本合同）：

- RuleBrain    手寫規則策略：沒有學習，沒有模型，但 agent 照樣誕生；
- NgramBrain   字符級 n-元語言模型：真的用統計學「訓練」出來，會「說話」，
               但不會說協議語言——用來理解為什麼指令跟隨（對齊）有價值；
- PolicyBrain  模仿學習的 softmax 策略：從專家軌跡裡學出「下一步調什麼工具」，
               決策可學習、可保存、可評測。

三個大腦與 MockLLM / 真實 LLM 接的是同一個 Agent、同一套 TASKS 評測——
跑 `demos/demo_from_zero.py` 可以看到四種大腦的成績單。

誠實聲明（也是教學點）：TinyBrain 只學「決策」（選哪個動作），
不學「生成」（寫什麼內容）；生成外包給下面的技能庫（SKILLS）。
真 LLM 的稀缺性正在於它把決策與生成一起學會了，還能泛化到沒見過的任務。
"""
from __future__ import annotations

import json
import math
import random
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .llm import BaseLLM, MockLLM
from .loop import Agent
from .protocol import (
    MalformedToolCall,
    ToolCall,
    format_toolcall,
    parse_response,
)
from .tools import ToolRegistry, make_builtin_tools

# 手寫計劃文本：與 tasks.TODO_TEXT 保持一致，讓 RuleBrain 的軌跡與專家軌跡同形。
PLAN_TEXT = "[ ] 查看目錄結構\n[ ] 搜索 TODO 標記\n[ ] 統計並寫入 REPORT.md"


# --------------------------------------------------------------- 消息工具

def _task_of(messages: List[dict]) -> str:
    """任務正文永遠是 history[1]（見 loop.py 的循環不變量）。"""
    return messages[1]["content"] if len(messages) > 1 else ""


def _last_user(messages: List[dict]) -> str:
    """最新的用戶消息 = 最新一條「觀察」（第一步時就是任務本身）。"""
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"]
    return ""


def _prev_call(messages: List[dict]) -> Optional[ToolCall]:
    """上一輪的動作。大腦靠「上一步做了什麼 + 看到了什麼」決定下一步。"""
    for message in reversed(messages):
        if message["role"] == "assistant":
            try:
                return parse_response(message["content"]).toolcall
            except MalformedToolCall:
                return None
    return None


def _strip_envelope(text: str) -> str:
    return text.split("\n", 1)[1] if text.startswith("TOOL RESULT") else text


# --------------------------------------------------------------- 技能庫

def balance_parens(source: str) -> str:
    """機械修復技能：補齊缺失的右括號。笨，但對語法錯誤任務剛好夠用。"""
    deficit = source.count("(") - source.count(")")
    return source + ")" * max(0, deficit)


def _skill_fix_parens(messages: List[dict]) -> str:
    source = _strip_envelope(_last_user(messages))
    fixed = balance_parens(source)
    return format_toolcall("write_file", {"path": "broken.py", "content": fixed})


def _skill_write_report(messages: List[dict]) -> str:
    """組合技能：把上一條 grep 觀察整理成 REPORT.md。"""
    found: Dict[str, List[str]] = {}
    for line in _last_user(messages).splitlines():
        if not line.startswith("./"):
            continue
        path, _, rest = line.split(":", 2)
        found.setdefault(path[2:], []).append(rest.strip())
    if not found:
        return "最終回答：工作區裡沒有找到 TODO 標記。"
    lines = []
    for path, hits in found.items():
        notes = "；".join(h.split("TODO:", 1)[-1].strip() or "(無說明)" for h in hits)
        lines.append(f"- {path}（{len(hits)} 處）：{notes}")
    report = "# TODO 報告\n\n" + "\n".join(lines) + "\n"
    return format_toolcall("write_file", {"path": "REPORT.md", "content": report})


def _skill_answer_token(messages: List[dict]) -> str:
    match = re.search(r'"(mh-demo-[0-9a-f]+)"', _last_user(messages))
    token = match.group(1) if match else "(未找到)"
    return f"Thought: 交卷。\n\n最終回答：token 藏在 src/config/prod.py 裡，值是 {token}"


# 動作空間：小模型只負責「選哪個」，參數由技能按當前觀察組裝。
SKILLS: Dict[str, Callable[[List[dict]], str]] = {
    "plan": lambda m: format_toolcall("todo", {"action": "write", "content": PLAN_TEXT}),
    "list_all": lambda m: format_toolcall("list_dir", {"path": ".", "recursive": True}),
    "read_broken": lambda m: format_toolcall("read_file", {"path": "broken.py"}),
    "fix_parens": _skill_fix_parens,
    "check_syntax": lambda m: format_toolcall("run_bash", {"command": "python3 -m py_compile broken.py"}),
    "grep_todo": lambda m: format_toolcall("run_bash", {"command": 'grep -rn "TODO" --include=*.py .'}),
    "write_report": _skill_write_report,
    "show_todo": lambda m: format_toolcall("todo", {"action": "show"}),
    "grep_token": lambda m: format_toolcall("run_bash", {"command": "grep -rn TOKEN --include=*.py ."}),
    "answer_report": lambda m: (
        "Thought: 收工。\n\n最終回答：TODO 清單已寫入 REPORT.md；"
        "notes.txt 中的「TODO」字樣因不是 .py 文件已正確排除。"
    ),
    "answer_fix": lambda m: (
        "Thought: 修好了。\n\n最終回答：broken.py 缺失的右括號已補上，語法檢查通過。"
    ),
    "answer_token": _skill_answer_token,
    "give_up": lambda m: "最終回答：我沒有學會這個任務，只能放棄。",
}
LABELS: Tuple[str, ...] = tuple(SKILLS)


def label_for_reply(reply: str, task_text: str) -> Optional[str]:
    """把一條（專家）回覆映射到動作標籤——收集模仿學習數據時用。"""
    try:
        parsed = parse_response(reply)
    except MalformedToolCall:
        return None
    if parsed.toolcall is None:
        if "REPORT" in task_text:
            return "answer_report"
        if "token" in task_text.lower():
            return "answer_token"
        if "修復" in task_text or "broken" in task_text:
            return "answer_fix"
        return None
    name, args = parsed.toolcall.name, parsed.toolcall.args
    if name == "todo":
        return "plan" if args.get("action") == "write" else "show_todo"
    if name == "list_dir":
        return "list_all"
    if name == "read_file":
        return "read_broken"
    if name == "write_file":
        return "write_report" if "REPORT" in str(args.get("path", "")) else "fix_parens"
    if name == "run_bash":
        command = str(args.get("command", ""))
        if "py_compile" in command:
            return "check_syntax"
        if "TOKEN" in command:
            return "grep_token"
        return "grep_todo"
    return None


# --------------------------------------------------------------- RuleBrain

class RuleBrain(BaseLLM):
    """手寫規則策略：一個 if-elif 長鏈。沒有模型、沒有學習，但它是合法大腦。

    讀完它的 generate 你會發現：它就是把專家軌跡寫成了代碼。
    它能在熟題上拿滿分，也永遠學不會新題——這正是手寫規則的天花板，
    也是「為什麼值得花力氣訓練模型」的第一直覺。
    """

    name = "rule"

    def generate(self, messages: List[dict]) -> str:
        task = _task_of(messages)
        prev = _prev_call(messages)
        if prev is None:
            return SKILLS["plan"](messages)
        if prev.name == "todo":
            nxt = "list_all" if prev.args.get("action") == "write" else "answer_report"
        elif prev.name == "list_dir":
            if "token" in task.lower():
                nxt = "grep_token"
            elif "broken" in task or "修復" in task:
                nxt = "read_broken"
            else:
                nxt = "grep_todo"
        elif prev.name == "read_file":
            nxt = "fix_parens"
        elif prev.name == "write_file":
            nxt = (
                "check_syntax"
                if "broken" in str(prev.args.get("path", ""))
                else "show_todo"
            )
        elif prev.name == "run_bash":
            command = str(prev.args.get("command", ""))
            if "py_compile" in command:
                nxt = "answer_fix"
            elif "TOKEN" in command:
                nxt = "answer_token"
            else:
                nxt = "write_report"
        else:
            nxt = "give_up"
        return SKILLS[nxt](messages)


# --------------------------------------------------------------- NgramBrain

class NgramBrain(BaseLLM):
    """字符級 n-元語言模型：真正的「訓練」（統計計數），零依賴、幾秒鐘跑完。

    它會學到語料裡哪些字符序列常見，於是能生成「看起來像那回事」的文本。
    但它不懂任務、不懂協議——餵給 Agent 後通常一步就被當成最終回答，
    評測顆粒無收。教學點：**語言能力 ≠ 指令跟隨能力**，
    後者才是 harness 敢把模型接進循環的前提。
    """

    name = "ngram"

    def __init__(self, order: int = 5, seed: int = 0):
        self.order = order
        # 固定種子的普通隨機數：只為採樣可復現，與任何安全/加密用途無關。
        self.rng = random.Random(seed)
        self.table: Dict[str, Dict[str, int]] = {}

    def fit(self, corpus: str) -> "NgramBrain":
        padded = "\n" * self.order + corpus
        for i in range(len(padded) - self.order):
            context = padded[i:i + self.order]
            nxt = padded[i + self.order]
            row = self.table.setdefault(context, {})
            row[nxt] = row.get(nxt, 0) + 1
        return self

    def sample(self, n_chars: int = 240) -> str:
        context = "\n" * self.order
        out: List[str] = []
        for _ in range(n_chars):
            row = self.table.get(context)
            if not row:
                break
            chars = list(row)
            weights = [row[c] for c in chars]
            nxt = self.rng.choices(chars, weights=weights, k=1)[0]
            out.append(nxt)
            context = context[1:] + nxt
        return "".join(out)

    def generate(self, messages: List[dict]) -> str:
        return self.sample(240)


def build_corpus(tasks, script_for) -> str:
    """把一批 mock 劇本的文本抽幹出來當訓練語料。"""
    parts: List[str] = []
    for task in tasks:
        for item in script_for(task.name):
            if isinstance(item, str):
                parts.append(item)
    return "\n\n".join(parts)


# --------------------------------------------------------------- PolicyBrain

@dataclass
class TrajectorySample:
    """一條模仿學習樣本：(任務, 觀察, 上一步) -> 下一步動作標籤。"""

    task_text: str
    observation: str
    prev: str
    label: str


def featurize(task_text: str, observation: str, prev: str) -> Dict[str, float]:
    """特徵工程：替小模型裝一雙「眼睛」。

    刻意用粗粒度標誌（而不是原文 bigram）：表述換個說法，標誌依然成立，
    學到的策略才能在自己（而非專家）的軌跡上穩定工作。
    """
    # 先剝掉 TOOL RESULT 信封再打標誌，否則「写入回执」和「查看結果」
    # 兩種觀察會被信封前綴蓋成一樣的，訓練樣本自相矛盾。
    observation = _strip_envelope(observation)
    feats: Dict[str, float] = {"bias": 1.0, "prev=" + prev: 1.0}
    if "REPORT" in task_text:
        feats["task=report"] = 1.0
    if "token" in task_text.lower():
        feats["task=token"] = 1.0
    if "修復" in task_text or "broken" in task_text:
        feats["task=fix"] = 1.0
    if "[ ]" in observation:
        feats["obs=todo"] = 1.0
    if observation.startswith("OK："):
        feats["obs=write_ok"] = 1.0
    if "REPORT.md" in observation:
        feats["obs=wrote_report"] = 1.0
    if "broken.py" in observation:
        feats["obs=wrote_broken"] = 1.0
    if "./" in observation:
        feats["obs=grep_hits"] = 1.0
    if ".py" in observation or "/" in observation:
        feats["obs=listing"] = 1.0
    if "def " in observation:
        feats["obs=code"] = 1.0
    if "[exit=0]" in observation:
        feats["obs=exit0"] = 1.0
    if "[exit=1]" in observation:
        feats["obs=exit1"] = 1.0
    if "(無輸出)" in observation:
        feats["obs=no_output"] = 1.0
    if "mh-demo-" in observation:
        feats["obs=token"] = 1.0
    return feats


class _RecordingBrain(BaseLLM):
    """包裹大腦，記下每一步 (看見了什麼, 說了什麼)。"""

    name = "recorder"

    def __init__(self, inner: BaseLLM):
        self.inner = inner
        self.steps: List[Tuple[List[dict], str]] = []

    def generate(self, messages: List[dict]) -> str:
        reply = self.inner.generate(messages)
        self.steps.append((list(messages), reply))
        return reply


def collect_trajectories(tasks, script_for) -> List[TrajectorySample]:
    """讓「專家」（MockLLM 劇本）重考一遍，錄下每步決策，產出模仿學習數據。"""
    samples: List[TrajectorySample] = []
    for task in tasks:
        recorder = _RecordingBrain(MockLLM(script_for(task.name)))
        workspace = Path(tempfile.mkdtemp(prefix="mh-collect-"))
        task.setup(workspace)
        Agent(recorder, make_builtin_tools(workspace), verbose=False).run(task.prompt)
        prev = "start"
        for messages, reply in recorder.steps:
            label = label_for_reply(reply, _task_of(messages))
            if label is None:
                prev = "start"
                continue
            samples.append(TrajectorySample(
                task_text=_task_of(messages),
                observation=_last_user(messages),
                prev=prev,
                label=label,
            ))
            call = _prev_call([*messages, {"role": "assistant", "content": reply}])
            prev = call.name if call else "start"
    return samples


class PolicyBrain(BaseLLM):
    """softmax 策略：純 Python 的多項邏輯回歸。

    fit() 用梯度上升最大化專家動作的對數似然（交叉熵損失的手寫版）；
    generate() 貪心選擇概率最大的動作，再交給技能庫組裝成協議文本。
    訓練只需毫秒級——數據小、特徵粗，這正是它誠實的邊界。
    """

    name = "policy"

    def __init__(self, weights: Optional[Dict[str, Dict[str, float]]] = None):
        self.weights: Dict[str, Dict[str, float]] = weights or {
            label: {} for label in LABELS
        }

    # ---- 學習 ----

    def fit(self, samples: List[TrajectorySample], epochs: int = 120, lr: float = 0.5) -> "PolicyBrain":
        for _ in range(epochs):
            for sample in samples:
                feats = featurize(sample.task_text, sample.observation, sample.prev)
                probs = self._probs(feats)
                for label in LABELS:
                    delta = lr * ((1.0 if label == sample.label else 0.0) - probs[label])
                    row = self.weights[label]
                    for key, value in feats.items():
                        row[key] = row.get(key, 0.0) + delta * value
        return self

    def _probs(self, feats: Dict[str, float]) -> Dict[str, float]:
        scores = {
            label: sum(row.get(key, 0.0) * value for key, value in feats.items())
            for label, row in self.weights.items()
        }
        peak = max(scores.values())
        exps = {label: math.exp(score - peak) for label, score in scores.items()}
        total = sum(exps.values())
        return {label: value / total for label, value in exps.items()}

    # ---- 推理（遵守 BaseLLM 協議）----

    def decide(self, messages: List[dict]) -> str:
        prev_call = _prev_call(messages)
        feats = featurize(
            _task_of(messages),
            _last_user(messages),
            prev_call.name if prev_call else "start",
        )
        probs = self._probs(feats)
        return max(LABELS, key=lambda label: probs[label])

    def generate(self, messages: List[dict]) -> str:
        return SKILLS[self.decide(messages)](messages)

    # ---- 權重持久化（路徑由本地調用方給定，模型輸出不會流入這裡）----

    def save(self, path: str) -> None:
        Path(path).write_text(
            json.dumps(self.weights, ensure_ascii=False, sort_keys=True), encoding="utf-8"
        )

    @classmethod
    def load(cls, path: str) -> "PolicyBrain":
        return cls(weights=json.loads(Path(path).read_text(encoding="utf-8")))
