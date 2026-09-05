# MiniAcademy 課程索引

6 階段、38 個模組、110 個目標皆已對應繁體中文教材。每課含概念、動手例子、預期結果、練習與驗收；八步 harness 動手營保留逐步行為檢查。這是可用的教學基線，尚未聲稱真人教學成效或學習者完成。英文目前有標題，正文覆蓋以 `i18n` 輸出為準。

[工具與進度](TOOLS.md) · [作業規格](submissions/README.md) · [專案清單](ASSESSMENT.md) · [導師手冊](MENTOR.md) · [參與方式](../CONTRIBUTING.md)

```bash
python3 tools/academy.py map
python3 tools/academy.py next
python3 tools/academy.py quiz --stage 0
python3 tools/academy.py verify
python3 tools/academy.py gaps
```

`done` 只記錄自評，不能替代檢查器、人工驗收或外部回饋。時數是包含專案的練習估計，學習節奏可調整。

## 0 · 零基礎起步

- [終端機與檔案系統](content/zh-TW/stage-0/terminal-first-steps.md) · G0.1, G0.2, G0.3, G0.4
- [第一支程式](content/zh-TW/stage-0/python.md) · G0.5, G0.6, G0.7, G0.8, G0.9
- [如何學會學習](content/zh-TW/stage-0/howto.md) · G0.10, G0.11, G0.12

階段驗收：G0.5, G0.9, G0.12。

## 1 · Python 程式核心

- [變數、型別與控制流](content/zh-TW/stage-1/core.md) · G1.1, G1.2, G1.3, G1.4
- [資料結構](content/zh-TW/stage-1/data.md) · G1.5, G1.6, G1.7
- [函式與模組](content/zh-TW/stage-1/func.md) · G1.8, G1.9, G1.10, G1.11
- [錯誤、異常與除錯](content/zh-TW/stage-1/debug.md) · G1.12, G1.13, G1.14, G1.15
- [文字檔案處理](content/zh-TW/stage-1/files.md) · G1.16, G1.17
- [Git 生存](content/zh-TW/stage-1/git.md) · G1.18, G1.19
- [專案：命令行小工具](content/zh-TW/stage-1/project.md) · G1.20, G1.21

階段驗收：G1.6, G1.14, G1.20。

## 2 · 工程與系統基礎

- [網際網路如何工作](content/zh-TW/stage-2/internet.md) · G2.1, G2.2, G2.3
- [資料格式](content/zh-TW/stage-2/data.md) · G2.4, G2.5
- [測試與除錯方法論](content/zh-TW/stage-2/testing.md) · G2.6, G2.7, G2.8
- [專案工程化](content/zh-TW/stage-2/eng.md) · G2.9, G2.10, G2.11
- [演算法與複雜度入門](content/zh-TW/stage-2/algo.md) · G2.12, G2.13, G2.14
- [SQL 入門](content/zh-TW/stage-2/db.md) · G2.15, G2.16
- [協作與自動化](content/zh-TW/stage-2/collab.md) · G2.17, G2.18, G2.19
- [專案：資料看板](content/zh-TW/stage-2/project.md) · G2.20

階段驗收：G2.6, G2.11, G2.20。

## 3 · 數學與機器學習

- [線性代數](content/zh-TW/stage-3/linalg.md) · G3.1, G3.2, G3.3, G3.4
- [微積分要素](content/zh-TW/stage-3/calc.md) · G3.5, G3.6, G3.7
- [機率與統計](content/zh-TW/stage-3/prob.md) · G3.8, G3.9, G3.10
- [資料科學工具鏈](content/zh-TW/stage-3/numpy.md) · G3.11, G3.12, G3.13
- [機器學習核心概念](content/zh-TW/stage-3/ml.md) · G3.14, G3.15, G3.16, G3.17, G3.18
- [專案：完整 ML 流水線](content/zh-TW/stage-3/project.md) · G3.19, G3.20

階段驗收：G3.7, G3.17, G3.19。

## 4 · 深度學習與大語言模型

- [PyTorch 與自動微分](content/zh-TW/stage-4/torch.md) · G4.1, G4.2, G4.3
- [訓練全流程](content/zh-TW/stage-4/training.md) · G4.4, G4.5, G4.6
- [架構巡禮](content/zh-TW/stage-4/arch.md) · G4.7, G4.8
- [Transformer 精讀](content/zh-TW/stage-4/transformer.md) · G4.9, G4.10, G4.11
- [Tokenizer 與資料](content/zh-TW/stage-4/token.md) · G4.12, G4.13
- [訓練自己的小模型](content/zh-TW/stage-4/lm.md) · G4.14, G4.15, G4.16
- [評估與基準](content/zh-TW/stage-4/eval.md) · G4.17, G4.18, G4.19

階段驗收：G4.10, G4.14, G4.19。

## 5 · Agent 工程與研究方法

- [LLM API 工程](content/zh-TW/stage-5/api.md) · G5.1, G5.2
- [Agent Harness（MiniHarness 全套）](../docs/00-overview.md) · G5.3, G5.4, G5.5, G5.6
- [上下文工程與 RAG](content/zh-TW/stage-5/context.md) · G5.7, G5.8
- [Agent 評測與安全](content/zh-TW/stage-5/safety.md) · G5.9, G5.10
- [研究方法](content/zh-TW/stage-5/research.md) · G5.11, G5.12, G5.13, G5.14
- [開源與影響](content/zh-TW/stage-5/oss.md) · G5.15, G5.16
- [前沿地圖（選讀）](content/zh-TW/stage-5/frontier.md) · G5.17, G5.18

階段驗收：G5.3, G5.12, G5.14, G5.15。

## 環境

核心：Python 3.9+；開發驗收：pytest。Stage 3/4 範例：Python 3.12 與 `python -m pip install -r academy/requirements-ml.txt`，可在獨立 venv 執行。CPU 可跑迷你模型；GPU 操作仍需可用硬體。未承諾免費雲端 GPU 或任何付費 API。
