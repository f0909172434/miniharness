# 專案交付與驗收

每個 build Goal 都需作品、重跑方式、預期與實際結果、故障案例和限制；以下連到逐課的具體交付規格。自動檢查不能代替人工判斷或外部事件。

|Goal|交付目標|具體規格|
|---|---|---|
|G1.20|獨立完成 ≥100 行的命令行小工具，含 README 與 3 個使用範例|[課程驗收](content/zh-TW/stage-1/project.md)；證據 `project`|
|G1.21|為自己的工具寫 ≥5 個 assert 自測並全部通過|[課程驗收](content/zh-TW/stage-1/project.md)；證據 `checker`|
|G2.20|完成「呼叫公開 API → 清洗 → 儲存 → 呈現」的小專案（含測試）|[課程驗收](content/zh-TW/stage-2/project.md)；證據 `project`|
|G3.19|完成「載入→清洗→特徵→訓練→評估→報告」的端到端 ML 專案|[課程驗收](content/zh-TW/stage-3/project.md)；證據 `project`|
|G3.20|完成一次單變因對照實驗並正確解讀結果|[課程驗收](content/zh-TW/stage-3/project.md)；證據 `project`|
|G4.10|從零實作迷你 Transformer（含 multi-head 與位置編碼）並通過形狀測試|[課程驗收](content/zh-TW/stage-4/transformer.md)；證據 `project`|
|G4.14|從零預訓練一個字元級/詞級小 LM 並生成可辨認的樣本|[課程驗收](content/zh-TW/stage-4/lm.md)；證據 `project`|
|G4.15|用 LoRA 或全量微調完成一次風格/任務遷移|[課程驗收](content/zh-TW/stage-4/lm.md)；證據 `project`|
|G4.16|建立小型 benchmark 並報告困惑度與任務分數|[課程驗收](content/zh-TW/stage-4/lm.md)；證據 `project`|
|G4.19|復現一個公開基準上的已知數字（在合理誤差內）|[課程驗收](content/zh-TW/stage-4/eval.md)；證據 `project`|
|G5.3|完成動手營 8 步，寫出 my_harness.py 並通過全部檢查|[課程驗收](../docs/00-overview.md)；證據 `checker`|
|G5.6|完成「從 0 造腦」對比實驗（RuleBrain/NgramBrain/PolicyBrain）並解讀|[課程驗收](../docs/00-overview.md)；證據 `project`|
|G5.10|建立 ≥10 任務的 agent 評測集並報告通過率與失敗模式分析|[課程驗收](content/zh-TW/stage-5/safety.md)；證據 `project`|
|G5.12|復現一篇論文的核心實驗（或其明確標註的縮小版）|[課程驗收](content/zh-TW/stage-5/research.md)；證據 `project`|
|G5.13|設計並執行一次消融實驗，用恰當的統計方法報告差異|[課程驗收](content/zh-TW/stage-5/research.md)；證據 `project`|
|G5.14|寫出可復現的技術報告（代碼+資料+結論+局限）並公開|[課程驗收](content/zh-TW/stage-5/research.md)；證據 `portfolio`|
|G5.15|向開源專案提交一個被合併的 PR，或發布自己的開源專案|[課程驗收](content/zh-TW/stage-5/oss.md)；證據 `portfolio`|
|G5.16|發布一篇技術博客或一次演講並收集真實回饋|[課程驗收](content/zh-TW/stage-5/oss.md)；證據 `portfolio`|

接受條件：可從乾淨環境重跑；逐項符合教材契約；結果含分母與失敗路徑；作者能解釋核心程式；人工/外部證據真實存在。否則記錄缺口後繼續練習。
