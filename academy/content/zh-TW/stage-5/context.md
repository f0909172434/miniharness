# 上下文工程與 RAG

> 對應 Goal：`G5.7`, `G5.8` ｜ 練習預估 10 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G5.4

## 為什麼學這個

在有限上下文中保留有用證據，並測量取回是否真的有幫助。

## 概念

RAG 先檢索再把證據放進回答上下文。向量檢索依 embedding 相近度找候選，可能漏掉精確編號、否定句或新資訊；高相似不等於支持主張。下面用集合相似度做最小離線基線，便於先驗證評測流程。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
docs = ["python list append", "python dict keys", "lean proof theorem"]
query = set("python list".split())
def score(text):
    words = set(text.split())
    return len(words & query) / len(words | query)
ranked = sorted(enumerate(docs), key=lambda row: (-score(row[1]), row[0]))
print(ranked[0])
```

### 預期結果

首筆是 (0, 'python list append')。這是 lexical Jaccard 基線，沒有宣稱使用向量模型。

## 練習與驗收

設計 10 個 query 與應取回的文件 ID，比較不檢索、此基線、你自行選的摘要或向量檢索。固定相同上下文長度，報告 recall@k、回答支持率與 token 使用量。加入精確編號、否定、無答案各一例。只在評測支持時聲稱收益，否則保留零或负結果。

## 常見坑

只把文件全部塞進 prompt 不是有效壓縮。摘要可能遺漏例外或來源 ID；裁剪後必須仍可回查原文。

## 自測清單

- [ ] `G5.7` 實作摘要壓縮或檢索增強之一，並用評測驗證收益。證據方式：`project`。
- [ ] `G5.8` 能解釋向量檢索的原理與它失效的場景。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://nlp.stanford.edu/IR-book/)。
