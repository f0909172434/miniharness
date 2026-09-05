"""執行五個固定的學習契約；不把參考實作或自評寫成學習者完成。"""
from __future__ import annotations
import argparse
import importlib.util
import math
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKERS = {'G1.6': 'wordcount.py', 'G1.21': 'test_cli.py',
            'G2.6': 'test_numeric.py', 'G3.17': 'metrics.py',
            'G5.3': 'tutorial/my_harness.py'}

def read_module(path):
    if not path.is_file():
        raise ValueError(f'尚未提供作業：{path.relative_to(ROOT)}')
    spec = importlib.util.spec_from_file_location('learner_' + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def wordcount(module):
    cases = [('', []), ('Bee ant bee CAT ant', [('ant',2),('bee',2),('cat',1)]),
             ('a\nA\t b', [('a',2),('b',1)]), ('x! x', [('x',1),('x!',1)])]
    for text, expected in cases:
        actual = module.word_counts(text)
        if actual != expected:
            raise ValueError(f'word_counts({text!r})：期望 {expected!r}，得到 {actual!r}')

def metrics(module):
    for truth, pred, expected in [([1,1,1,1,0],[1,1,0,0,1],(2/3,.5,4/7)),
                                  ([0,0],[0,0],(0.,0.,0.)),
                                  ([1,0],[1,0],(1.,1.,1.))]:
        actual = module.binary_metrics(truth, pred)
        for key, value in zip(('precision','recall','f1'), expected):
            if not math.isfinite(actual[key]) or abs(actual[key]-value) > 1e-9:
                raise ValueError(f'{key} 計算錯誤：{actual[key]}，期望 {value}')
    try:
        module.binary_metrics([1], [])
    except ValueError:
        pass
    else:
        raise ValueError('長度不一致必須拒絕')
    for n, k in [(7,3), (10,5), (3,3)]:
        folds = module.split_folds(n, k)
        if len(folds) != k:
            raise ValueError('折數不符')
        held_out = []
        for train, test in folds:
            if not train or not test or set(train) & set(test):
                raise ValueError('訓練與驗證折為空或重疊')
            if set(train) | set(test) != set(range(n)):
                raise ValueError('每折必須涵蓋全部樣本')
            held_out.extend(test)
        if sorted(held_out) != list(range(n)):
            raise ValueError('每筆資料必須恰好驗證一次')

def run(gid, reference=False):
    base = ROOT / 'academy' / ('examples/reference' if reference else 'submissions')
    if gid == 'G5.3':
        target = ROOT / ('tutorial/solutions/my_harness_full.py' if reference else CHECKERS[gid])
        return subprocess.run([sys.executable, str(ROOT/'tutorial/check.py'), '--submission', str(target)],
                              cwd=ROOT, timeout=90, check=False).returncode
    sys.path.insert(0, str(base))
    target = base / CHECKERS[gid]
    if not target.is_file():
        raise ValueError(f'尚未提供作業：{target.relative_to(ROOT)}')
    if gid == 'G1.21':
        suite = unittest.defaultTestLoader.loadTestsFromModule(read_module(target))
        if suite.countTestCases() < 5:
            raise ValueError('需要至少 5 個 unittest 測試案例')
        return 0 if unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful() else 1
    if gid == 'G2.6':
        import pytest
        return int(pytest.main(['-q', str(target)+'::test_normal',
                               str(target)+'::test_boundary',str(target)+'::test_error']))
    module = read_module(target)
    (wordcount if gid == 'G1.6' else metrics)(module)
    print(f'{gid}: 契約通過')
    return 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('goal', choices=CHECKERS)
    parser.add_argument('--reference', action='store_true')
    args = parser.parse_args()
    try:
        return run(args.goal, args.reference)
    except (ValueError, AttributeError, ImportError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f'{args.goal}: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
