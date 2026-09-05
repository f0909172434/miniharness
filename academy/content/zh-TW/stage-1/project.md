# 專案：命令行小工具

> 對應 Goal：`G1.20`, `G1.21` ｜ 練習預估 4 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.17, G1.18

## 為什麼學這個

把散落的練習組成別人能執行的命令行工具。

## 概念

題目是「學習紀錄統計器」：接受 UTF-8 CSV（date,topic,minutes），驗證分鐘是非負整數，依 topic 加總，可輸出 JSON。分開 parse、summarize、render 和 main；CLI 用 argparse，失敗走 stderr 與非零退出碼。先交付能跑的最小版本，再擴充。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```bash
python3 studylog.py --help
python3 studylog.py sample.csv
python3 studylog.py sample.csv --format json
python3 -m unittest discover -s academy/submissions -p test_cli.py
```

### 預期結果

對 sample.csv 的兩筆 Python 30、Python 20 應得到總和 50；壞分鐘或缺少欄位應失敗。範例是你的交付介面，不是倉庫已提供 studylog.py。

## 練習與驗收

交付至少 100 行有用途的 Python 程式（不靠註解或空行湊數）、README 與三個可重跑範例。將至少 5 個 unittest 放入 academy/submissions/test_cli.py，涵蓋正常、空資料、壞數字、缺欄與 CLI 退出碼，再跑 `python3 tools/academy.py verify --goal G1.21`。

## 常見坑

檢查器只能確認測試真的執行，不能保證你的測試足夠好。把加總故意改成計數，至少一個測試必須失敗；保存這次反向驗證作為驗收證據。

## 自測清單

- [ ] `G1.20` 獨立完成 ≥100 行的命令行小工具，含 README 與 3 個使用範例。證據方式：`project`。
- [ ] `G1.21` 為自己的工具寫 ≥5 個 assert 自測並全部通過。證據方式：`checker`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/library/argparse.html)。
