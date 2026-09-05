# 第一支程式

> 對應 Goal：`G0.5`, `G0.6`, `G0.7`, `G0.8`, `G0.9` ｜ 練習預估 4 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G0.2

## 為什麼學這個

讓電腦執行你存下的程式，並知道報錯該從哪裡開始看。

## 概念

從 python.org 安裝 Python 3.9 以上版本；終端機執行 `python3 --version`（Windows 可用 `py --version`）。本課以下以 `python3` 表示你的 Python 指令。在文字編輯器建立 `hello.py`，不要存成 `hello.py.txt`。程式從頂端開始執行；`input` 會等輸入，回傳的是字串。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
print("Hello, World")
name = input("你的名字：")
print("你好，" + name)
print("程式結束")
```

### 預期結果

在檔案所在目錄執行 `python3 hello.py`。先出現 Hello, World，再等你輸入名字，最後才印出問候與結束訊息。

## 練習與驗收

先不執行，在紙上寫下輸入 Kai 後的四段顯示順序。把最後一個 name 故意改成 nmae，執行並保存 NameError，根據 traceback 的檔名和行號修正；再從另一個目錄用完整路徑執行一次。

## 常見坑

不要在 Python 的 `>>>` 提示符內輸入終端機指令。離開互動環境可用 `exit()`。讀取 NameError 最後一行，再往上找自己的檔案；不要把它誤當 Python 安裝失敗。

## 自測清單

- [ ] `G0.5` 能安裝 Python 並用 python3 --version（或 python --version）驗證。證據方式：`self`。
- [ ] `G0.6` 能建立 .py 檔並在終端機執行，輸出 Hello, World。證據方式：`self`。
- [ ] `G0.7` 能用 print 與 input 寫一個問答小程式。證據方式：`self`。
- [ ] `G0.8` 能說出「程式是被電腦逐行執行的文字」並預測三行程式碼的輸出順序。證據方式：`self`。
- [ ] `G0.9` 能讀懂一個 NameError 並修復拼錯的變數名。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/tutorial/introduction.html)。
