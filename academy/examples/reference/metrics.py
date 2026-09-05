"""以二元分類與索引切分示範可核對的評估契約。"""
def binary_metrics(truth, pred):
    if len(truth) != len(pred) or not truth or any(x not in (0, 1) for x in truth+pred):
        raise ValueError('invalid binary labels')
    tp = sum(a == b == 1 for a, b in zip(truth, pred))
    fp = sum(a == 0 and b == 1 for a, b in zip(truth, pred))
    fn = sum(a == 1 and b == 0 for a, b in zip(truth, pred))
    p = tp/(tp+fp) if tp+fp else 0.
    r = tp/(tp+fn) if tp+fn else 0.
    return {'precision':p, 'recall':r, 'f1':2*p*r/(p+r) if p+r else 0.}

def split_folds(n, k):
    if not 2 <= k <= n:
        raise ValueError('require 2 <= k <= n')
    return [([i for i in range(n) if i % k != fold],
             [i for i in range(n) if i % k == fold]) for fold in range(k)]
