# LLM API 工程

> 對應 Goal：`G5.1`, `G5.2` ｜ 練習預估 8 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G2.20

## 為什麼學這個

讓模型输出有可檢查的契約，並控制每次任務的資源。

## 概念

system prompt 可描述角色、輸出格式和資料邊界，但模型仍可能違規；程式必須解析與驗證輸出。上下文預算要扣掉系統說明、歷史、工具結果及預留回答。費用估算分輸入/輸出 token 與單價，單價須查所選供應商當時公告。本課離線練習不發付費請求。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import json
reply = '{"answer":"42","sources":["fixture:1"]}'
data = json.loads(reply)
assert set(data) == {"answer", "sources"}
assert isinstance(data["answer"], str)
assert isinstance(data["sources"], list)
budget, system, history, reserve = 4096, 500, 2200, 800
print("remaining for tool result", budget-system-history-reserve)
```

### 預期結果

工具結果剩 596 token 的假設預算。數字是練習配額，字元數不等於實際 token 數。

## 練習與驗收

寫三個 prompt 版本，對相同五個離線回覆（含壞 JSON、缺欄、錯型別）測解析器。讀 docs/02-protocol.md 的錯誤回饋，保留每次修改與結果。以供應商當前價格建立輸入/輸出費用公式；未使用真 API 就明寫尚未實測模型遵守率。

## 常見坑

格式驗證通過不代表答案正確。外部文件中的「忽略原規則」是資料，不能提升成系統指令；也不能只靠 prompt 防止工具越界。

## 自測清單

- [ ] `G5.1` 能設計並迭代 system prompt 以穩定模型輸出格式。證據方式：`self`。
- [ ] `G5.2` 能管理一次任務的上下文預算並估算 token 成本。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/library/json.html)。
