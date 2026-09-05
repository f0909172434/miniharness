# 訓練自己的小模型

> 對應 Goal：`G4.14`, `G4.15`, `G4.16` ｜ 練習預估 18 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G4.10, G4.12

## 為什麼學這個

把 attention 模組接成真的會更新參數與生成字元的小模型。

## 概念

使用本倉庫自行撰寫的短句 fixture 做 next-character prediction。輸入 x 與目標 y 相差一個字元；cross entropy 衡量真實下一字元的負對數機率。此練習用完整參數微調做一次句型遷移，沒有下載模型或需要付費 API。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```bash
python3 academy/examples/tiny_lm.py --steps 240
python3 academy/examples/tiny_lm.py --steps 240 --adapt-steps 80
```

### 預期結果

程式實際輸出初始與最後 loss、保留短句的 perplexity、固定提示生成結果，以及微調前後的任務分數。以實測為準；短句過擬合不代表通用語言能力。

## 練習與驗收

先跑形狀與因果遮罩檢查。關閉參考程式，自行實作訓練迴圈與 generator；保留原模型，再用新的句型全量微調，報告前後 perplexity 和精確任務分數。列出生成中的重複、拼寫錯誤和未改善案例。交付固定 seed、原始 fixture、版本與可重跑命令。

## 常見坑

不要用訓練短句當保留測試集。生成可辨認樣本需要人工閱讀，loss 下降本身不能替代；若未達到就調查並保留未完成狀態。

## 自測清單

- [ ] `G4.14` 從零預訓練一個字元級/詞級小 LM 並生成可辨認的樣本。證據方式：`project`。
- [ ] `G4.15` 用 LoRA 或全量微調完成一次風格/任務遷移。證據方式：`project`。
- [ ] `G4.16` 建立小型 benchmark 並報告困惑度與任務分數。證據方式：`project`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)。
