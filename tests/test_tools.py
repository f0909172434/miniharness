"""工具層測試：重點釘住三道安全閘與錯誤反饋的格式。"""
import pytest

from miniharness.tools import make_builtin_tools


@pytest.fixture()
def registry(tmp_path):
    return make_builtin_tools(tmp_path)


def test_write_then_read(registry):
    out = registry.run_tool("write_file", {"path": "src/a.txt", "content": "hello"})
    assert out.startswith("OK")
    assert registry.run_tool("read_file", {"path": "src/a.txt"}) == "hello"


def test_path_escape_blocked(registry):
    out = registry.run_tool("read_file", {"path": "../outside.txt"})
    assert out.startswith("ERROR")
    assert "越界" in out


def test_unknown_tool(registry):
    out = registry.run_tool("nope", {})
    assert out.startswith("ERROR")
    assert "未知工具" in out


def test_missing_required_param(registry):
    out = registry.run_tool("write_file", {"path": "x.txt"})
    assert out.startswith("ERROR")
    assert "缺少必填參數" in out


def test_unknown_param_rejected(registry):
    out = registry.run_tool("read_file", {"path": "a.txt", "evil": 1})
    assert out.startswith("ERROR")


def test_wrong_param_type(registry):
    out = registry.run_tool("list_dir", {"recursive": "yes"})
    assert out.startswith("ERROR")
    assert "boolean" in out


def test_bash_allowlist(registry):
    out = registry.run_tool("run_bash", {"command": "rm -rf ."})
    assert out.startswith("ERROR")
    assert "白名單" in out


def test_bash_runs_and_reports_exit(registry):
    out = registry.run_tool("run_bash", {"command": "echo hello"})
    assert "hello" in out
    assert "exit=0" in out


def test_todo_roundtrip(registry):
    registry.run_tool("todo", {"action": "write", "content": "[ ] 第一步"})
    assert "第一步" in registry.run_tool("todo", {"action": "show"})
