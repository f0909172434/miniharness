# PyTorch 與自動微分

> 對應 Goal：`G4.1`, `G4.2`, `G4.3` ｜ 練習預估 10 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G3.19

## 為什麼學這個

用自動微分核對手推梯度，再訓練一個最小網路。

## 概念

tensor 可記錄梯度；requires_grad=True 的葉節點累積 .grad。backward 沿計算圖套用鏈式法則。nn.Module 管理可訓練參數，optimizer 根據梯度更新；每一步先清除前一步的梯度。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import torch
from torch import nn
torch.manual_seed(42)
x = torch.tensor(2.0, requires_grad=True)
y = (3*x + 1)**2
y.backward()
print(x.grad.item())
model = nn.Sequential(nn.Linear(1,8), nn.Tanh(), nn.Linear(8,1))
X = torch.linspace(-1,1,32).reshape(-1,1)
opt = torch.optim.Adam(model.parameters(), lr=0.03)
for _ in range(150):
    opt.zero_grad()
    loss = ((model(X)-2*X)**2).mean()
    loss.backward()
    opt.step()
print(float(loss.detach()))
```

### 預期結果

第一個梯度是 42。第二段在玩具關係 y=2x 上降低 MSE；輸出實際 loss，而非預設「收斂成功」。

## 練習與驗收

先畫 (3x+1)² 的計算圖並手算 42。把 optimizer.zero_grad 移除，比較曲線；以初始 loss 和最後 loss 判斷是否降低，並測網路在訓練範圍外 x=3 的輸出。

## 常見坑

不要在 backward 前用 .item() 把 loss 轉成 Python 數字；這會失去計算圖。收斂於訓練資料不等於泛化。

## 自測清單

- [ ] `G4.1` 能用 tensor 完成前向計算並呼叫 backward 得到梯度。證據方式：`self`。
- [ ] `G4.2` 能解釋 autograd 計算圖與手推鏈式法則的對應關係。證據方式：`self`。
- [ ] `G4.3` 能用 nn.Module 搭建多層感知機並在玩具資料上訓練收斂。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)。
