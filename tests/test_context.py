"""上下文管理測試：裁剪必須成對丟棄、保護最新觀察、且永不丟系統提示與任務。"""
from miniharness.context import ContextManager


def _make_history(n_pairs: int, filler: int = 500) -> list:
    history = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "task"},
    ]
    for i in range(n_pairs):
        history.append({"role": "assistant", "content": f"call {i} " + "x" * filler})
        history.append({"role": "user", "content": f"result {i} " + "y" * filler})
    return history


def test_under_budget_untouched():
    manager = ContextManager(max_chars=100000)
    history = _make_history(3)
    assert manager.fit(history) == history


def test_over_budget_keeps_recent_pairs():
    manager = ContextManager(max_chars=4000)
    history = _make_history(10, filler=500)
    fitted = manager.fit(history)

    # 系統提示與任務永遠在
    assert fitted[0]["content"] == "sys"
    assert fitted[1]["content"] == "task"
    # 丟棄發生時必須留下佔位說明
    assert any("裁剪" in m["content"] for m in fitted[2:-2])
    # 最新的 (調用, 觀察) 對必須完整保留
    assert fitted[-2]["content"].startswith("call 9")
    assert fitted[-1]["content"].startswith("result 9")
    # 裁剪後確實回到預算內
    assert manager._size(fitted) <= manager.max_chars


def test_pairs_dropped_together():
    manager = ContextManager(max_chars=2500)
    history = _make_history(4, filler=500)
    fitted = manager.fit(history)
    # 保留的是完整的最新兩對，不出現「沒有結果的調用」
    assert fitted[-4]["content"].startswith("call 2")
    assert fitted[-3]["content"].startswith("result 2")
    assert fitted[-2]["content"].startswith("call 3")
    assert fitted[-1]["content"].startswith("result 3")
