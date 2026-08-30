"""工具層 + 最小安全層（對應課程 docs/03-tools.md 與 docs/06-sandbox.md）。

一個工具 = 名字 + 描述 + 參數 schema + 一個返回字符串的函數。
ToolRegistry 負責註冊、校驗、執行、輸出截斷。

安全設計（教學級，刻意簡單，繞過方式見 docs/06 的誠實討論）：
1. resolve_path：所有文件參數都必須落在工作目錄內（防路徑逃逸）；
2. run_bash：白名單命令逐一**顯式**構造參數列表（shell=False）——
   用戶輸入只出現在「參數」位置，命令本體永遠是 harness 寫死的字符串，
   從結構上杜絕命令拼接；
3. 一切工具輸出在註冊表層統一截斷（防上下文爆炸）。
"""
from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Tuple


class ToolError(Exception):
    """工具主動拒絕執行（路徑越界、非法命令等）。錯誤文本會喂回給模型。"""


@dataclass
class Param:
    """一個參數的 schema。刻意只支持三種類型：string / integer / boolean。"""

    type: str = "string"
    description: str = ""
    required: bool = False


@dataclass
class Tool:
    name: str
    description: str
    params: Dict[str, Param]
    func: Callable[..., str]


def resolve_path(workspace: Path, raw: str) -> Path:
    """把模型給的相對路徑解析成絕對路徑，並確保它沒有逃出工作目錄。

    這是 harness 裡典型的一行式防線：模型可能因幻覺或提示注入給出
    `../../etc/passwd` 這樣的路徑，這裡是唯一能攔住它的地方。
    """
    candidate = (workspace / raw).resolve()
    root = workspace.resolve()
    if candidate != root and root not in candidate.parents:
        raise ToolError(f"路徑越界：'{raw}' 位於工作目錄之外，harness 拒絕執行")
    return candidate


# run_bash 的黑名單字符：雖然已經不走 shell，仍保留這道閘——
# 萬一未來有人改動執行方式，它能擋住管道/重定向/組合命令。
_FORBIDDEN_CHARS = (";", "|", "&", ">", "<", "`", "$(")

DEFAULT_BASH_ALLOW: Tuple[str, ...] = (
    "ls", "cat", "head", "tail", "grep", "find", "wc", "echo", "python3",
)


@dataclass
class ToolRegistry:
    """工具的註冊表 + 執行器。Agent 只跟它說話，不直接碰工具函數。"""

    workspace: Path
    max_output: int = 4000
    tools: Dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def catalog(self) -> str:
        """渲染成系統提示詞裡的工具清單。"""
        lines = []
        for tool in self.tools.values():
            params = ", ".join(
                f"{name}: {param.type}" + ("" if param.required else "?")
                for name, param in tool.params.items()
            )
            lines.append(f"- {tool.name}({params}): {tool.description}")
        return "\n".join(lines)

    def run_tool(self, name: str, args: Dict) -> str:
        """按名字運行一個工具，永不拋異常——一切錯誤都變成 ERROR 文本喂回模型。

        這是「自我修復循環」的關鍵設計：模型調錯了工具、漏了參數、
        路徑越界，收到的都是一段可讀的錯誤說明，於是它有機會自己改。
        （方法名叫 run_tool 而不是 execute，純粹是為了不讓人聯想到
        cursor.execute 之類的查詢介面——這裡沒有查詢，只有普通函數調用。）
        """
        tool = self.tools.get(name)
        if tool is None:
            return f"ERROR: 未知工具 '{name}'。可用工具：{', '.join(self.tools)}"

        for pname, param in tool.params.items():
            if param.required and pname not in args:
                return f"ERROR: 工具 '{name}' 缺少必填參數 '{pname}'（{param.description}）"
        for pname in args:
            if pname not in tool.params:
                return f"ERROR: 工具 '{name}' 不接受參數 '{pname}'"

        for pname, value in args.items():
            want = tool.params[pname].type
            bad = (
                (want == "string" and not isinstance(value, str))
                or (want == "integer" and (not isinstance(value, int) or isinstance(value, bool)))
                or (want == "boolean" and not isinstance(value, bool))
            )
            if bad:
                return f"ERROR: 工具 '{name}' 的參數 '{pname}' 需要 {want} 類型，收到 {type(value).__name__}"

        try:
            output = str(tool.func(**args))
        except ToolError as exc:
            return f"ERROR: {exc}"
        except Exception as exc:  # noqa: BLE001 —— 教學實現：任何異常都降級為可讀錯誤
            return f"ERROR: 工具內部異常 {type(exc).__name__}: {exc}"

        if len(output) > self.max_output:
            output = output[: self.max_output] + f"\n[……輸出超過 {self.max_output} 字符，已截斷……]"
        return output


def make_builtin_tools(
    workspace: Path,
    bash_allow: Tuple[str, ...] = DEFAULT_BASH_ALLOW,
    bash_timeout: int = 15,
) -> ToolRegistry:
    """組裝一套內置工具，全部以 workspace 為根。

    返回的註冊表就是 agent 的「手」：看目錄、讀寫文件、跑受限命令、記 todo。
    """
    # 統一解析符號鏈接（macOS 的 /var -> /private/var），
    # 保證 resolve_path 的比較與 relative_to 的拼接都用同一個根。
    ws = Path(workspace).resolve()
    reg = ToolRegistry(workspace=ws)

    def t_list_dir(path: str = ".", recursive: bool = False) -> str:
        target = resolve_path(ws, path)
        if not target.exists():
            raise ToolError(f"路徑不存在：{path}")
        if recursive:
            files = sorted(p for p in target.rglob("*") if p.is_file())
            entries = [p.relative_to(ws).as_posix() for p in files[:200]]
            if len(files) > 200:
                entries.append(f"(共 {len(files)} 個文件，僅顯示前 200)")
        else:
            entries = [
                child.relative_to(ws).as_posix() + ("/" if child.is_dir() else "")
                for child in sorted(target.iterdir(), key=lambda c: c.name)
            ]
        return "\n".join(entries) if entries else "(空目錄)"

    def t_read_file(path: str) -> str:
        p = resolve_path(ws, path)
        if not p.is_file():
            raise ToolError(f"'{path}' 不是文件（目錄請用 list_dir）")
        text = p.read_text(encoding="utf-8", errors="replace")
        if len(text) > 8000:
            text = text[:8000] + "\n[……文件超過 8000 字符，已截斷……]"
        return text

    def t_write_file(path: str, content: str) -> str:
        p = resolve_path(ws, path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"OK：已寫入 {p.relative_to(ws).as_posix()}（{len(content)} 字符）"

    def t_run_bash(command: str) -> str:
        """受限命令執行。

        安全關鍵：每個白名單命令都**字面**構造參數列表並以 shell=False 執行。
        用戶（模型）的輸入經 shlex 分詞後只落在參數位置，命令本體是
        harness 源碼裡寫死的字符串——不存在「拼接出一條新命令」的可能。
        """
        cmd = command.strip()
        if not cmd:
            raise ToolError("命令為空")
        argv = shlex.split(cmd)
        if not argv:
            raise ToolError("命令解析後為空")
        for ch in _FORBIDDEN_CHARS:
            if ch in cmd:
                raise ToolError(
                    f"run_bash 禁止使用 '{ch}'（教學實現不支持管道/重定向/組合命令，見 docs/06）"
                )

        head, rest = argv[0], argv[1:]
        try:
            if head == "grep":
                proc = subprocess.run(["grep", *rest], shell=False, cwd=str(ws),
                                      capture_output=True, text=True, timeout=bash_timeout)
            elif head == "find":
                proc = subprocess.run(["find", *rest], shell=False, cwd=str(ws),
                                      capture_output=True, text=True, timeout=bash_timeout)
            elif head == "ls":
                proc = subprocess.run(["ls", *rest], shell=False, cwd=str(ws),
                                      capture_output=True, text=True, timeout=bash_timeout)
            elif head == "cat":
                proc = subprocess.run(["cat", *rest], shell=False, cwd=str(ws),
                                      capture_output=True, text=True, timeout=bash_timeout)
            elif head == "head":
                proc = subprocess.run(["head", *rest], shell=False, cwd=str(ws),
                                      capture_output=True, text=True, timeout=bash_timeout)
            elif head == "tail":
                proc = subprocess.run(["tail", *rest], shell=False, cwd=str(ws),
                                      capture_output=True, text=True, timeout=bash_timeout)
            elif head == "wc":
                proc = subprocess.run(["wc", *rest], shell=False, cwd=str(ws),
                                      capture_output=True, text=True, timeout=bash_timeout)
            elif head == "echo":
                proc = subprocess.run(["echo", *rest], shell=False, cwd=str(ws),
                                      capture_output=True, text=True, timeout=bash_timeout)
            elif head == "python3":
                proc = subprocess.run(["python3", *rest], shell=False, cwd=str(ws),
                                      capture_output=True, text=True, timeout=bash_timeout)
            else:
                raise ToolError(
                    f"命令 '{head}' 不在白名單內。允許：{', '.join(bash_allow)}"
                )
        except subprocess.TimeoutExpired as exc:
            raise ToolError(f"命令超時（>{bash_timeout}s），已終止") from exc

        output = proc.stdout
        if proc.stderr:
            output += "\n[stderr]\n" + proc.stderr
        return (output.strip() or "(無輸出)") + f"\n[exit={proc.returncode}]"

    def t_todo(action: str = "show", content: str = "") -> str:
        """任務清單工具：把計劃寫進工作區裡的 .todo.md（docs/05-memory.md）。"""
        path = ws / ".todo.md"
        if action == "write":
            path.write_text(content, encoding="utf-8")
            return f"OK：todo 已更新。當前內容：\n{content}"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return "(todo 為空。建議先用 action=write 寫下你的行動計劃)"

    reg.register(Tool(
        name="list_dir",
        description="列出目錄內容。recursive=true 時遞歸列出工作區內所有文件（相對路徑）。",
        params={
            "path": Param("string", "相對於工作目錄的路徑，默認 ."),
            "recursive": Param("boolean", "是否遞歸列出所有文件"),
        },
        func=t_list_dir,
    ))
    reg.register(Tool(
        name="read_file",
        description="讀取一個文本文件。",
        params={"path": Param("string", "相對於工作目錄的文件路徑", required=True)},
        func=t_read_file,
    ))
    reg.register(Tool(
        name="write_file",
        description="寫入（或覆蓋）一個文本文件，自動創建父目錄。",
        params={
            "path": Param("string", "相對於工作目錄的文件路徑", required=True),
            "content": Param("string", "要寫入的完整內容", required=True),
        },
        func=t_write_file,
    ))
    reg.register(Tool(
        name="run_bash",
        description="執行一條白名單命令（grep/find/ls/cat/head/tail/wc/echo/python3），返回輸出與退出碼。",
        params={"command": Param("string", "要執行的命令，如 grep -rn TODO --include=*.py .", required=True)},
        func=t_run_bash,
    ))
    reg.register(Tool(
        name="todo",
        description="維護你的行動計劃：action=write 覆蓋寫入清單，action=show 讀取當前清單。",
        params={
            "action": Param("string", "write 或 show"),
            "content": Param("string", "action=write 時的清單內容"),
        },
        func=t_todo,
    ))
    return reg
