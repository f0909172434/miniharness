# 09 · 從 0 造腦：連模型都沒有的時候

> 對應代碼：`miniharness/brains.py`。跑起來：`python3 demos/demo_from_zero.py`
> 場景設定：沒有 API Key、沒有預訓練模型、沒有第三方庫——只有 Python 標準庫。

## 這一章回答的問題

Part 1 默認大腦是 LLM。但「大腦」這個插槽裡到底**必須**放什麼？
把 LLM 拿掉，agent 還成立嗎？答案是成立——而且把大腦從笨到聰明換一遍，
恰好能把「harness / 模型 / 智能」三者的關係徹底看清：

> Agent = harness + 大腦。harness 是常量，大腦是變量。

三個自製大腦，全部遵守與 LLM 相同的介面（`generate(messages) -> str`），
輸出全部遵守同一份 [02 章](02-protocol.md)協議——所以 `loop.py` 一行不改。

## 第一站：RuleBrain —— 沒有模型，也有 agent

```python
class RuleBrain(BaseLLM):
    def generate(self, messages):
        prev = _prev_call(messages)          # 上一步做了什麼
        if prev is None:      return SKILLS["plan"](messages)
        if prev.name == "todo":   return SKILLS["list_all"](messages) ...
```

一個 if-elif 長鏈：看「上一步動作 + 任務文本」，從 13 個動作裡選下一個。
它在本倉庫的三個任務上**滿分**（`tests/test_brains.py` 釘死了這個事實）。

這證明了一件容易被 LLM 光環遮住的事：**agent 的主體是 harness**。
「維持循環、執行工具、驗收產物」這些讓任務被完成的機器，跟智能無關。
RuleBrain 的智能是零，但 agent 是完整的。

它也演示了天花板：規則是**為熟題手寫的**，換一道新題立刻歸零。
這就是「為什麼值得訓練模型」的第一直覺。

## 第二站：NgramBrain —— 自己訓練一個語言模型

「連模型都沒有」那就造一個。字符級 n-元模型是最小的真語言模型：
數一遍語料裡每個 5 字符上下文後面跟著哪個字符，生成時按頻率採樣——
十行核心代碼、幾毫秒訓練、純 stdlib（`NgramBrain.fit/sample`）。

把它對準專家軌跡語料訓練，它確實學會了「說話」：

```text
{"tool": "todo", "args": {"command": "grep -rn \"TODO\" --in
```

看起來有模有樣——然後上崗，**評測 0/3**。原因值得咀嚼：

- 它可能生成出協議格式的**碎片**，但幾乎不可能拼出合法 JSON；
- 就算它輸出純文本，循環規則「沒有 toolcall = 最終回答」會讓它
  第一步就交卷一段胡話。

教學點：**語言能力 ≠ 指令跟隨能力。** Harness 敢把模型接進循環，
前提是模型「懂規矩」；這份懂規矩（指令跟隨/對齊）不是語言建模送來的，
是額外訓練出來的——這就是 ChatGPT 之類「聊天模型」存在的意義。
0 分的 NgramBrain 和 100 分的 LLM 之間，隔著整個後訓練（post-training）產業。

## 第三站：PolicyBrain —— 決策可以被學出來

第二個自訓模型換一個思路：不學「說話」，只學「選擇」。

**數據**：`collect_trajectories()` 讓專家（MockLLM 劇本）重考一遍，
錄下每一步 `(任務, 觀察, 上一步) → 動作`，得到 13 條模仿學習樣本。

**模型**：softmax 回歸（多項邏輯回歸），純 Python 手寫梯度下降，
`PolicyBrain.fit()` 約 20 行。輸入是 `featurize()` 打的粗粒度標誌
（任務含不含 REPORT/token/修復？觀察是不是 grep 命中？上一步是什麼工具？），
輸出是 13 個動作上的概率。

**推理**：`generate()` 貪心選動作，再交給技能庫組裝出協議文本。
成績：**3/3，與專家一致**。

兩個誠實的註腳：

1. **決策與生成分工了。** PolicyBrain 只學「選哪個動作」，動作的參數
   （報告內容、補括號、抽 token）由 `SKILLS` 技能庫機械完成。
   真 LLM 的稀缺性正在於它把決策**和**生成一起學了；
2. **它在自家考試集上滿分，換新題就露餡**（練習 2 會讓你親眼看到）。
   泛化才是大規模預訓練買到的東西。

## 四種大腦成績單（demo 的真實輸出）

```text
大腦                          成績   一句話
--------------------------------------------------------------
NgramBrain（自訓語言模型）      0%   語言能力 ≠ 指令跟隨能力
RuleBrain（手寫規則）        100%   熟題滿分，永不會新題
PolicyBrain（模仿學習）      100%   決策可學習；泛化才是稀缺品
--------------------------------------------------------------
結論：harness 是常量，大腦是變量。真 LLM 的價值，
      是一個『什麼任務都見過』的泛化大腦——插槽已經留好。
```

把這張表和 Rich Sutton 的[苦澀教訓（The Bitter Lesson）](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)對照著讀：
手寫知識（RuleBrain）總會被學習（PolicyBrain）打敗，
小規模學習又會被大規模學習（LLM）打敗——但**無論哪種大腦，
都要先有一副讓它能幹活的馬具**。這就是本課程存在的原因。

## 練習

1. 給 `SKILLS` 加一個新動作（例如 `search`），手工擴充 RuleBrain 的規則鏈，
   體會「每加一個動作要改多少處」——這就是規則系統的維護成本；
2. 給評測集加一道新題（[07 章](07-eval.md)練習 1 的 refactor），**不**重新訓練，
   分別跑 RuleBrain 與 PolicyBrain，記錄成績——親眼看到「不會泛化」；
3. 把 `featurize()` 改成字符 bigram 特徵，觀察訓練時間與在自家任務上的
   成績變化，並解釋為什麼「更強的特徵」反而可能更脆；
4. （挑戰）實現 `ActiveBrain`：PolicyBrain 對下一步不確定時（最大概率 < 0.6）
   主动輸出 `give_up`——給策略加上「知道自己不會」的能力，
   然後想想真實 agent 裡對應的機制叫什麼（human-in-the-loop / 置信度熔斷）。

## 延伸閱讀

- [minimind](https://github.com/jingyaogong/minimind) —— 想造**更強的**大腦？
  下一站是真正的神經網絡 LM：這裡的 NgramBrain 是它的「0 號機」；
- [nanoGPT](https://github.com/karpathy/nanoGPT) / [nanochat](https://github.com/karpathy/nanochat)——
  從字符級模型到可聊天模型的完整階梯；
- [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)（Rich Sutton, 2019）；
- [ReAct](https://arxiv.org/abs/2210.03629)——論文裡的對照實驗正是「同樣的循環，換不同大腦」。
