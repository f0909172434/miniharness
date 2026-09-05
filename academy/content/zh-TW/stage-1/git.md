# Git 生存

> 對應 Goal：`G1.18`, `G1.19` ｜ 練習預估 4 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.10

## 為什麼學這個

保留能解釋的歷史，讓錯誤修改可以安全撤回。

## 概念

在新的練習目錄操作。工作目錄、暫存區、提交是不同狀態：add 選擇要記錄的內容，commit 建立快照。revert 以新提交反做舊提交，適合已分享的歷史。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```bash
git init
# 在編輯器建立 README.md，寫入用途
git add README.md
git commit -m "Describe the tool"
# 在 README.md 故意加入錯誤用法
git diff
git add README.md
git commit -m "Add an incorrect example"
git log --oneline
git revert HEAD
git log --oneline
```

### 預期結果

最後多一筆 revert 提交，README 回到修正前的內容；歷史保留了錯誤與撤回。若 Git 要求身分，設定自己的姓名與郵件後再提交。

## 練習與驗收

對照每一步的 git status；保存兩次 log 與 revert 前後 diff。加入 .gitignore 排除 .venv、密鑰和產物。練習只 add 指定檔案，解釋為何不應把私人資料放進公開 Git 歷史。

## 常見坑

不要用 reset --hard 或 force push 當入門撤回方式。尚未提交的工作不一定能從 Git 復原；先確認 diff，再作改動。

## 自測清單

- [ ] `G1.18` 能用 git init/add/commit 管理一個小專案的完整歷史。證據方式：`self`。
- [ ] `G1.19` 能讀懂 git log/diff 並安全地回退一次錯誤提交。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things)。
