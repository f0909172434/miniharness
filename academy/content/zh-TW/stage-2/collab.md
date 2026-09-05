# 協作與自動化

> 對應 Goal：`G2.17`, `G2.18`, `G2.19` ｜ 練習預估 6 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G2.7, G2.9

## 為什麼學這個

讓修改有可檢閱的差異，讓每次提交自動得到測試回饋。

## 概念

分支承載一個明確變更；PR 說明問題、結果、驗證與限制。review 的每條意見應回應或修改。CI 執行你本機相同的測試入口，權限保持最小。正則適合有清楚模式的文字，不適合取代完整 HTML 或 JSON 解析器。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import re
text = "job=alpha duration=120ms; job=beta duration=8ms"
rows = re.findall(r"job=([a-z]+) duration=(\d+)ms", text)
print([(name, int(ms)) for name, ms in rows])
```

### 預期結果

得到 [('alpha', 120), ('beta', 8)]；單位與欄位位置是此正則的輸入契約。

## 練習與驗收

在練習 repo 建 branch，改一個可重現的小問題，附測試提 PR。以本倉庫 .github/workflows/ 的 Python 測試段落為起點，加入 push/pull_request 觸發與 contents: read。故意讓測試失敗，確認 CI 變紅，再修正。真實 review 往返才可完成 G2.17；自行扮演 reviewer 只能算演練。

## 常見坑

先把外部文字當資料；從 log 抽出的內容不能當 shell 指令執行。不要讓 pull_request 的不可信程式取得發布憑證。

## 自測清單

- [ ] `G2.17` 用 branch + 提交一個 PR 並處理 review 意見。證據方式：`portfolio`。
- [ ] `G2.18` 能用正則從非結構化文字中抽取目標資訊。證據方式：`self`。
- [ ] `G2.19` 寫一個排程腳本或 CI 步驟自動執行測試。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.github.com/en/actions/writing-workflows/quickstart)。
