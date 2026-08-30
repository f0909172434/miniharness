# 05 · 記憶與計劃：為什麼頂級 agent 都在寫 todo

> 對應代碼：`tools.py` 裡的 `todo` 工具 + `demos/demo_mock.py` 的使用方式。

## 一個反直覺的事實

模型有「上下文記憶」，為什麼還需要把計劃寫進文件？
因為上下文記憶有三個致命弱點（回顧 [04 章](04-context.md)）：

1. 會被**裁剪**——跑了十幾步後，最初的計劃可能已經不完整；
2. 會被**稀釋**——十幾條工具輸出之間，模型對「我原本打算做什麼」
   的注意力急劇衰減；
3. 會隨任務**清零**——新任務開始，上一輪的經驗全丟。

而文件不一樣：它是環境的一部分，agent 隨時可以**重新讀取**；
它比「記在心裡」更省上下文（只佔需要的那幾行）；它還天然持久。
這就是業界所說的 **agentic memory** 的第一原則：

> **文件即記憶（files as memory）。** 與其讓模型「記住」，不如讓它「寫下來」。

## MiniHarness 的兩個記憶件

### todo 工具：工作記憶外置

```python
t_todo(action="write", content="[ ] 查看目錄\n[ ] 搜索 TODO\n[ ] 寫報告")
t_todo(action="show")   # 隨時回讀
```

它只是讀寫工作區裡的 `.todo.md`，没有任何魔法。但注意 demo 裡的用法：
**第一步先寫計劃，收工前再看一眼**。這個習慣（plan → work → review）
是把三步任務做成三步的關鍵——沒有它，模型經常「做完第二步就宣布勝利」。

### 產物文件：長期記憶

demo 裡 agent 把報告寫進 `REPORT.md`。看似只是任務要求，
其實同時是一種記憶策略：結論落在文件裡，之後任何一輪（甚至下一次運行）
都可以 `read_file` 拿回全部細節，歷史裡只需要一個指針。

## 從玩具到生產：同一個光譜

| 層級 | 機制 | 代表 |
| --- | --- | --- |
| 本課程 | todo / 產物文件 | —— |
| 編碼 agent | 記憶文件（每次會話自動注入的項目筆記） | Claude Code 的 CLAUDE.md、各種 AGENTS.md |
| 會話記憶 | 跨會話的用戶偏好與事實 | ChatGPT memory、Claude memory |
| 檢索記憶 | 向量庫按語義召回歷史片段 | RAG 系統、MemGPT/Letta |

值得點破的是：**前三層都是「文件/文本 + 注入」**，只有最後一層才需要
向量庫。教學項目常常一上來就 RAG，那是在解決大多數人還沒有的問題。
判斷標準很簡單：當「要記的東西多到無法全文注入」時，才需要檢索。

## 常見失敗模式

- **計劃寫完就忘**：模型寫了 todo 但再也不 show。修法：在系統提示詞的
  回合規則裡加「每完成一項，更新 todo 並勾選」；
- **todo 變成小說**：計劃寫了 2000 字。todo 應該是清單不是散文，
  它要反覆進上下文，越短越便宜；
- **把記憶當數據庫**：往 todo 塞結構化狀態。結構化狀態請寫專門的
  `state.json` 工具，讀寫分工清晰。

## 練習

1. 把 demo 的 mock 劇本改壞：刪掉第一步的 todo write，觀察任務仍然成功——
   然後想一個 todo 真正救場的任務（提示：步驟 > 7 步、或中途被裁剪歷史）；
2. 實現 `notes` 工具：`append`/`read` 模式，只增不刪；
   在系統提示詞裡要求「每個重要結論先記 notes 再繼續」；
3. （進階）讓 `Agent.run()` 開始時自動把 `.todo.md` 內容注入任務消息，
   實現「跨 run 接續」。

## 延伸閱讀

- [Anthropic: Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) 的 Agentic Memory 一節；
- [Letta（MemGPT）論文](https://arxiv.org/abs/2310.08560)——把上下文當操作系統內存管理的先驅；
- Claude Code 最佳實踐裡關於 CLAUDE.md 的章節——「文件即記憶」的工業級樣板。
