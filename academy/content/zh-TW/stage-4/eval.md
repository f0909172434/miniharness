# 評估與基準

> 對應 Goal：`G4.17`, `G4.18`, `G4.19` ｜ 練習預估 10 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G4.14

## 為什麼學這個

用相同資料和計分規則，才有可比較的基準數字。

## 概念

困惑度 exp(平均 token 負對數似然) 依 tokenizer、資料與平均方式而變；不同 tokenizer 的 perplexity 不能直接排名。下游任務分數另查回答是否正確。基準污染可能來自訓練資料、提示例子或開發過程反覆查看測試答案。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import math
losses = [0.2, 0.4, 0.6]
print(round(math.exp(sum(losses)/len(losses)), 4))
correct = [True, False, True]
print(sum(correct), len(correct), sum(correct)/len(correct))
```

### 預期結果

困惑度約 1.4918，任務正確 2/3。它們回答不同問題，不能把兩個數字相加當總分。

## 練習與驗收

選一個有公開程式、資料版本與已知數字的基準，先寫重現契約：revision、模型、tokenizer、split、prompt、seed、指標和容許誤差，再執行。達不到時報告差異和環境，不更改容許誤差來宣稱成功。課內 tiny_lm 可練習流程，但不算重現外部基準的證據。

## 常見坑

有訓練污染就不應稱作泛化。比較兩個模型需相同題目和逐題輸出；只保留平均值會看不到失敗類型。

## 自測清單

- [ ] `G4.17` 能解釋 perplexity 與下游任務評估的差別。證據方式：`self`。
- [ ] `G4.18` 能識別基準資料污染並設計避坑方案。證據方式：`self`。
- [ ] `G4.19` 復現一個公開基準上的已知數字（在合理誤差內）。證據方式：`project`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://huggingface.co/docs/transformers/perplexity)。
