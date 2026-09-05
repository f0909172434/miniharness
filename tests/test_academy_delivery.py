"""驗證缺作業、失敗檢查與無效匯入不會被當作成功完成。"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import pytest
from tools.academy import ROOT, load_manifest, main, quiz_questions
from tools.academy_checks import metrics, wordcount


def test_quiz_covers_knowledge_and_does_not_mark_progress(tmp_path):
    manifest = load_manifest()
    questions = quiz_questions(manifest)
    assert {q['goal'] for q in questions} == {g['id'] for g in manifest['goals'] if g['level']=='know'}
    assert len({q['goal'] for q in questions}) == len(questions)
    for q in questions:
        assert len(set(q['choices'])) == 3 and 0 <= q['answer'] < 3 and q['explanation']
    answers = tmp_path/'answers.json'
    answers.write_text(json.dumps({q['goal']:q['answer']+1 for q in questions}))
    progress = tmp_path/'progress.json'
    assert main(['quiz','--answers',str(answers),'--progress',str(progress)]) == 0
    assert not progress.exists()
    answers.write_text('{}')
    assert main(['quiz','--answers',str(answers),'--progress',str(progress)]) == 1


def test_progress_import_rejects_corruption_and_preserves_existing(tmp_path):
    manifest = load_manifest()
    progress = tmp_path/'progress.json';progress.write_text('{"done":["G0.1"]}')
    incoming = tmp_path/'incoming.json'
    invalid = {'format':'miniacademy-progress/v1','manifest_version':manifest['version'],'done':['G999.1']}
    incoming.write_text(json.dumps(invalid))
    original = progress.read_bytes()
    assert main(['import',str(incoming),'--progress',str(progress)]) == 1
    assert progress.read_bytes() == original
    invalid['done']=['G0.2'];incoming.write_text(json.dumps(invalid))
    assert main(['import',str(incoming),'--progress',str(progress)]) == 0
    assert json.loads(progress.read_text())['done'] == ['G0.1','G0.2']
    out=tmp_path/'snapshot.json'
    assert main(['export',str(out),'--progress',str(progress)]) == 0
    assert main(['export',str(out),'--progress',str(progress)]) == 1


def test_wordcount_checker_rejects_missing_tie_rule():
    class Broken:
        @staticmethod
        def word_counts(text): return [('bee',2),('ant',2),('cat',1)] if text else []
    with pytest.raises(ValueError): wordcount(Broken)


def test_metrics_checker_rejects_fold_leakage():
    path=ROOT/'academy/examples/reference/metrics.py'
    spec=importlib.util.spec_from_file_location('metrics_reference',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    metrics(module)
    module.split_folds=lambda n,k:[(list(range(n)),[i]) for i in range(k)]
    with pytest.raises(ValueError,match='重疊'): metrics(module)


def test_workshop_failure_has_nonzero_exit(tmp_path):
    bad=tmp_path/'unfinished.py';bad.write_text('"""尚未實作。"""\n')
    result=subprocess.run([sys.executable,str(ROOT/'tutorial/check.py'),'--submission',str(bad)],
                          text=True,capture_output=True,timeout=30)
    assert result.returncode == 1
    assert '当前卡在' in result.stdout
    assert bad.read_text() == '"""尚未實作。"""\n'


def test_ready_lesson_goals_are_present():
    for stage in load_manifest()['stages']:
        for module in stage['modules']:
            if module['status'] != 'ready': continue
            text='\n'.join((ROOT/p).read_text() for p in module['content']['zh-TW'])
            # harness 的既有概念文檔另由總覽對應到 Goal。
            if module['id']=='s5-harness': continue
            for goal in module['goals']: assert goal in text
            assert '自測清單' in text
