# 專案工程化

> 對應 Goal：`G2.9`, `G2.10`, `G2.11` ｜ 練習預估 6 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.20

## 為什麼學這個

讓使用者在乾淨環境重現你的工具，而不依赖你機器上的隱藏套件。

## 概念

建立 src/studylog、tests、README.md 與 pyproject.toml；src/studylog/__init__.py 放套件內容。開發環境與執行環境分開，requirements.txt 是重現開發環境的快照，pyproject.toml 描述套件的直接需求。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```bash
python3 -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install pytest build
python -m pip freeze > requirements.txt
python -m pip install -e .
python -m pytest
python -m build
```

### 預期結果

先依官方 packaging tutorial 補上 pyproject.toml 的 build-system 與 project 欄位；成功後 dist/ 有 wheel 與 sdist，乾淨環境可安裝。

## 練習與驗收

在第二個 venv 從 wheel 安裝，從倉庫外 import studylog，避免意外匯入工作目錄。README 必須含 Python 版本、三步安裝、最短命令、預期輸出與常見錯誤；自己計時跑過一次，真實陌生人五分鐘成功需另有試用紀錄。

## 常見坑

pip freeze 不是跨平台完整鎖定保證；記錄 Python/OS。不要把 .venv 提交進版本庫，也不要將網站或機器學習課套件加入 harness 執行依賴。

## 自測清單

- [ ] `G2.9` 能用 venv 隔離環境並用 requirements.txt 鎖定依賴。證據方式：`self`。
- [ ] `G2.10` 能按 src/tests/README 結構組織一個可安裝的專案。證據方式：`self`。
- [ ] `G2.11` 寫出讓陌生人 5 分鐘內跑起來的 README。證據方式：`project`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://packaging.python.org/en/latest/tutorials/packaging-projects/)。
