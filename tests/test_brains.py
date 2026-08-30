"""大腦層測試：四種大腦接同一個 harness、同一套評測的行為釘死。"""
from miniharness import Agent, run_eval
from miniharness.brains import (
    NgramBrain,
    PolicyBrain,
    RuleBrain,
    balance_parens,
    build_corpus,
    collect_trajectories,
    featurize,
)
from miniharness.tasks import TASKS, mock_script
from miniharness.tools import make_builtin_tools


def _factory(brain, max_steps=10):
    def build(task, workspace):
        return Agent(brain, make_builtin_tools(workspace), verbose=False, max_steps=max_steps)
    return build


def _rate(brain, tasks=TASKS, max_steps=10, root=None):
    return run_eval(_factory(brain, max_steps), tasks, root=root)


# ---- 技能庫 ------------------------------------------------------

def test_balance_parens_fixes_broken_source():
    from miniharness.tasks import BROKEN_SOURCE
    import ast
    fixed = balance_parens(BROKEN_SOURCE)
    ast.parse(fixed)  # 修完必須能過語法樹


# ---- NgramBrain --------------------------------------------------

def test_ngram_brain_trains_and_samples():
    corpus = build_corpus(TASKS, mock_script)
    brain = NgramBrain(order=5, seed=0).fit(corpus)
    text = brain.sample(200)
    assert len(text) == 200
    again = NgramBrain(order=5, seed=0).fit(corpus).sample(200)
    assert text == again  # 固定種子 → 可復現


def test_ngram_brain_fails_eval_but_harness_survives(tmp_path):
    rate = _rate(NgramBrain(order=5, seed=0).fit(build_corpus(TASKS, mock_script)), root=tmp_path)
    assert rate == 0.0  # 不會說協議語言 → 顆粒無收（且 harness 沒有崩）


# ---- RuleBrain ---------------------------------------------------

def test_rule_brain_passes_full_eval(tmp_path):
    assert _rate(RuleBrain(), root=tmp_path) == 1.0


# ---- PolicyBrain -------------------------------------------------

def test_featurize_flags():
    feats = featurize("找出 TODO 並寫入 REPORT.md", "./app/core.py:5: TODO x", "run_bash")
    assert feats["task=report"] == 1.0
    assert feats["prev=run_bash"] == 1.0
    assert feats["obs=grep_hits"] == 1.0


def test_policy_brain_learns_and_passes_eval(tmp_path):
    samples = collect_trajectories(TASKS, mock_script)
    assert len(samples) >= 10  # 三份專家軌跡
    brain = PolicyBrain().fit(samples)
    assert _rate(brain, root=tmp_path) == 1.0  # 在自家考試集上復現專家


def test_policy_brain_weights_roundtrip(tmp_path):
    samples = collect_trajectories(TASKS, mock_script)
    brain = PolicyBrain().fit(samples)
    path = tmp_path / "weights.json"
    brain.save(str(path))
    loaded = PolicyBrain.load(str(path))
    assert loaded.weights == brain.weights
