# Transformer 精讀

> 對應 Goal：`G4.9`, `G4.10`, `G4.11` ｜ 練習預估 16 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G4.7

## 為什麼學這個

從張量形狀與遮罩看懂 Transformer 的核心運算。

## 概念

Attention(Q,K,V)=softmax(QKᵀ/√d)V。Q 是查詢、K 是可比對的鍵、V 是取回的資訊。多頭把特徵分成不同子空間；位置編碼提供順序。Residual 讓訊息有直接路徑，LayerNorm 穩定每個 token 的特徵尺度。自回歸遮罩必須擋住未來位置。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import torch, math
Q = torch.tensor([[1.,0.],[0.,1.]])
K = Q.clone()
V = torch.tensor([[2.,0.],[0.,4.]])
scores = Q @ K.T / math.sqrt(2)
scores = scores.masked_fill(torch.triu(torch.ones(2,2,dtype=torch.bool),1), float("-inf"))
weights = scores.softmax(-1)
print(weights)
print(weights @ V)
```

### 預期結果

第一列權重是 [1,0]，不能看未來；第二列兩個非負權重加總為 1。先算 exp(0) 與 exp(1/√2) 的比例再核對。

## 練習與驗收

讀 academy/examples/tiny_lm.py 的 Attention 與 TinyLM，關閉範例後自行實作多頭、位置 embedding、residual 與 LayerNorm。驗收 (B,T) 輸入到 (B,T,Vocab) 輸出；改動最後一個 token，前面 logits 應不變。測 dim 無法整除 heads 時拒絕；同時驗證梯度存在。

## 常見坑

只有形狀正確仍可能洩漏未來 token。因果性測試要把模型切到 eval，避免 dropout 造成比較雜訊。

## 自測清單

- [ ] `G4.9` 能手推 scaled dot-product attention 並說明 Q/K/V 各自的作用。證據方式：`self`。
- [ ] `G4.10` 從零實作迷你 Transformer（含 multi-head 與位置編碼）並通過形狀測試。證據方式：`project`。
- [ ] `G4.11` 能解釋 residual 連接與 layer norm 在深層網路中的作用。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html)。

## 互動實驗

用 [TokenScope 實驗路線](../../../../docs/tokenscope-labs.md)先預測、再操作與核對數值，匯出後重載重播。這是補充練習，不會自動標記本課學習目標完成。
