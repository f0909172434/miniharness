"""循環層測試：正常兩步、解析失敗自愈、步數熔斷、工具錯誤反饋。"""
from miniharness import Agent, MockLLM
from miniharness.protocol import format_toolcall
from miniharness.tools import make_builtin_tools


def _agent(tmp_path, script, **kwargs) -> Agent:
    return Agent(MockLLM(script), make_builtin_tools(tmp_path), verbose=False, **kwargs)


def test_two_step_run(tmp_path):
    script = [
        "Thought: 看看目錄。\n" + format_toolcall("list_dir", {}),
        "Thought: 目錄是空的，沒什麼可做。\n\n最終回答：工作區目前是空的。",
    ]
    result = _agent(tmp_path, script).run("看看工作區裡有什麼")
    assert result.ok
    assert result.steps == 2
    assert result.tool_calls == 1
    assert "空的" in result.final
    # 完整軌跡：system, task, 調用, 觀察, 最終回答
    assert len(result.history) == 5


def test_self_repair_after_malformed(tmp_path):
    script = [
        "```toolcall\n{broken json}\n```",
        "Thought: 這次寫對。\n" + format_toolcall("list_dir", {}),
        "最終回答：完成。",
    ]
    result = _agent(tmp_path, script).run("隨便看看")
    assert result.ok
    assert result.steps == 3
    assert result.tool_calls == 1
    joined = "".join(m["content"] for m in result.history)
    assert "TOOL RESULT (parse)" in joined and "ERROR" in joined


def test_max_steps_stop(tmp_path):
    script = [format_toolcall("list_dir", {})] * 5
    result = _agent(tmp_path, script, max_steps=2).run("無限循環")
    assert not result.ok
    assert result.error == "max_steps"
    assert result.steps == 2


def test_tool_error_fed_back(tmp_path):
    script = [
        '```toolcall\n{"tool": "read_file", "args": {"path": "missing.txt"}}\n```',
        "最終回答：文件不存在，任務無法繼續。",
    ]
    result = _agent(tmp_path, script).run("讀一個不存在的文件")
    assert result.ok
    joined = "".join(m["content"] for m in result.history)
    assert "ERROR" in joined


def test_mock_reactive_script(tmp_path):
    """劇本可調用項：大腦能看到上一輪觀察再決定說什麼。"""
    def react(messages):
        last = messages[-1]["content"]
        return f"看到了：{last[:20]}。最終回答：完成。"

    result = _agent(tmp_path, [format_toolcall("list_dir", {}), react]).run("測試反應式")
    assert result.ok
    assert "看到了" in result.history[-1]["content"]
