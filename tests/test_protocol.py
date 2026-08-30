"""協議層測試：解析器是 harness 裡最容易碎的地方，值得優先釘死。"""
import pytest

from miniharness.protocol import MalformedToolCall, format_toolcall, parse_response


def test_parse_toolcall():
    text = (
        "Thought: 看一下目錄。\n"
        '```toolcall\n{"tool": "list_dir", "args": {"path": "."}}\n```'
    )
    parsed = parse_response(text)
    assert parsed.thought == "Thought: 看一下目錄。"
    assert parsed.toolcall is not None
    assert parsed.toolcall.name == "list_dir"
    assert parsed.toolcall.args == {"path": "."}


def test_parse_final_answer():
    parsed = parse_response("任務完成，報告已寫入 REPORT.md。")
    assert parsed.toolcall is None
    assert "REPORT.md" in parsed.thought


def test_malformed_json_raises():
    with pytest.raises(MalformedToolCall):
        parse_response("```toolcall\n{broken json}\n```")


def test_missing_tool_key_raises():
    with pytest.raises(MalformedToolCall):
        parse_response('```toolcall\n{"args": {}}\n```')


def test_args_not_object_raises():
    with pytest.raises(MalformedToolCall):
        parse_response('```toolcall\n{"tool": "list_dir", "args": [1, 2]}\n```')


def test_format_roundtrip():
    parsed = parse_response(format_toolcall("read_file", {"path": "a.txt"}))
    assert parsed.toolcall.name == "read_file"
    assert parsed.toolcall.args == {"path": "a.txt"}
