# 訓練全流程

> 對應 Goal：`G4.4`, `G4.5`, `G4.6` ｜ 練習預估 12 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G4.3

## 為什麼學這個

讓一次訓練可解釋、可重跑，並在適當時機停止。

## 概念

optimizer 更新參數；scheduler 改學習率。dropout 在訓練時隨機遮掉特徵，weight decay 約束權重，early stopping 根據驗證集選停止點。驗證用 model.eval() 與 no_grad()，評估後記得回到 train()。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import torch, platform
print({"python": platform.python_version(), "torch": torch.__version__,
       "cuda": torch.cuda.is_available(),
       "mps": torch.backends.mps.is_available()})
# 可用裝置才啟用；CPU 是完整的教學回退路徑
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(device)
```

### 預期結果

只報告目前主機實際可用的裝置，不保證有免費 GPU。CPU 可完成 tiny_lm 的示例；G4.5 的 GPU 操作仍需要實際可用的 GPU 與紀錄。

## 練習與驗收

在前課加 StepLR、AdamW 的 weight_decay=0.01 和 Dropout(0.1)。每十步驗證一次，只按驗證 loss 保存最佳 checkpoint；耐心 5 次未改善就停止。分開比較各項改動，保存 seed、版本、device、參數、資料雜湊與每步 loss。在可用 GPU 上將模型與資料一起移動並記錄耗時。

## 常見坑

固定 seed 不保證跨硬體位元一致。不要把最終一輪權重當成最佳權重，也不要在 test 集早停。

## 自測清單

- [ ] `G4.4` 能配置 optimizer/scheduler 並從 loss 曲線診斷訓練狀態。證據方式：`self`。
- [ ] `G4.5` 能使用 GPU（含 Colab）加速訓練並記錄可復現的實驗元資料。證據方式：`self`。
- [ ] `G4.6` 能用 dropout/weight decay/early stopping 改善泛化並說明各自原理。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://pytorch.org/docs/stable/notes/randomness.html)。
