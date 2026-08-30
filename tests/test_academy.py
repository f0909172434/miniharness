"""MiniAcademy 结构测试：把「随时找漏洞」固化进 CI。

manifest 的任何结构性破坏（重复 ID、悬空引用、依赖环、
ready 模块缺正文、文件缺失）都会让这些测试变红。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.academy import (  # noqa: E402
    ROOT,
    find_cycle,
    goal_index,
    goal_owner,
    i18n_report,
    learning_queue,
    load_manifest,
    load_progress,
    save_progress,
    validate,
)

MANIFEST = load_manifest()


def test_manifest_structure_valid():
    errors, _warnings = validate(MANIFEST)
    assert errors == [], f"manifest 有结构错误：{errors}"


def test_every_goal_is_referenced_by_a_module():
    owner = goal_owner(MANIFEST)
    orphans = [gid for gid in goal_index(MANIFEST) if gid not in owner]
    assert orphans == [], f"未被任何模块引用的 goal：{orphans}"


def test_goal_ids_follow_stage_prefix():
    for stage in MANIFEST["stages"]:
        for module in stage["modules"]:
            for gid in module["goals"]:
                assert gid.startswith(f"G{stage['id']}."), (
                    f"{module['id']} 引用了别的阶段的 goal {gid}")


def test_prerequisite_graph_has_no_cycle():
    assert find_cycle(MANIFEST) is None


def test_ready_modules_have_existing_content():
    for stage in MANIFEST["stages"]:
        for module in stage["modules"]:
            if module["status"] != "ready":
                continue
            paths = [p for files in module["content"].values() for p in files]
            assert paths, f"{module['id']} status=ready 但没有登记任何内容"
            for rel in paths:
                assert (ROOT / rel).exists(), f"{module['id']} 内容缺失：{rel}"


def test_stage_exits_reference_own_stage_goals():
    for stage in MANIFEST["stages"]:
        stage_goal_ids = {gid for m in stage["modules"] for gid in m["goals"]}
        for gid in stage["exit"]:
            assert gid in stage_goal_ids, f"阶段 {stage['id']} 的 exit 引用了外部 goal {gid}"


def test_learning_queue_respects_stage_order():
    # 空进度时，推荐队列必须来自最早的未完成阶段（0），不许跨阶段跳级
    candidates, _blocked = learning_queue(MANIFEST, set())
    assert candidates, "空进度时应有可学模块"
    assert all(entry[0] == 0 for entry in candidates)


def test_learning_queue_blocks_on_unmet_prerequisites(tmp_path):
    # 假装 stage 0 已全部达成：队列应推进到阶段 1；阶段 2 模块不得进入队列
    stage0_done = {gid for m in MANIFEST["stages"][0]["modules"] for gid in m["goals"]}
    candidates, blocked = learning_queue(MANIFEST, stage0_done)
    assert candidates and all(entry[0] == 1 for entry in candidates + blocked)
    assert all(entry[0] != 2 for entry in candidates)


def test_progress_roundtrip(tmp_path):
    path = tmp_path / "progress.json"
    save_progress({"done": ["G0.1"]}, path)
    assert load_progress(path)["done"] == ["G0.1"]


def test_i18n_report_covers_all_declared_locales():
    lines = "\n".join(i18n_report(MANIFEST))
    for locale in MANIFEST["locales"]:
        assert locale in lines
