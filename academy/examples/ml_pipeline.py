"""以固定切分示範開發交叉驗證、單變因選擇與保留集評估。"""
import json
import platform
import sklearn
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, confusion_matrix

def main():
    X, y = load_breast_cancer(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, stratify=y, random_state=42)
    cv = StratifiedKFold(3, shuffle=True, random_state=42)
    scores = {}
    for c in [.1, 1.0]:
        model = make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=1000))
        scores[c] = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_macro').tolist()
    best = max(scores, key=lambda c: sum(scores[c])/len(scores[c]))
    model = make_pipeline(StandardScaler(), LogisticRegression(C=best, max_iter=1000))
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    report = {'dataset':'sklearn breast_cancer; educational use', 'python':platform.python_version(),
              'sklearn':sklearn.__version__, 'seed':42, 'train_n':len(y_train),'test_n':len(y_test),
              'training_cv_macro_f1':scores,'selected_C':best,
              'test_macro_f1':float(f1_score(y_test,pred,average='macro')),
              'test_confusion_matrix':confusion_matrix(y_test,pred).tolist(),
              'limit':'One fixed split on a small bundled dataset; no clinical or general superiority claim.'}
    print(json.dumps(report,indent=2))
    return report

if __name__=='__main__': main()
