"""上下文管理（對應課程 docs/04-context.md）。

上下文窗口是 agent 最稀缺的資源：它同時裝著系統提示詞、任務、
模型的思考和工具的輸出。跑得越久，歷史越長，於是——

1. 貴：每次 generate 都要把整段歷史重發一遍；
2. 稀釋：中間的老信息會被「擠出去」（lost in the middle）。

MiniHarness 的策略足夠簡單，一屏能看完：
- 工具輸出在 tools.py 創建時就已截斷（第一道閘）；
- 超出預算時，從最舊的 (助手調用, 工具結果) 對開始丟棄，
  留下一條佔位說明告訴模型「歷史被裁過」（第二道閘）；
- 系統提示詞與最初的任務消息永不丟棄。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ContextManager:
    """按字符數（token 數的廉價代理）管理歷史長度。

    用字符而不是真 token：教學實現不值得引入分詞器依賴，
    字符數 ÷ 3~4 就是很夠用的估計。
    """

    max_chars: int = 24000
    truncation_note: str = (
        "[……更早的對話已被 harness 裁剪以節省上下文；"
        "相關結論請以你之前的思考和最終產物為準……]"
    )

    @staticmethod
    def _size(messages: List[dict]) -> int:
        return sum(len(m["content"]) for m in messages)

    def fit(self, messages: List[dict]) -> List[dict]:
        """返回一份裁剪後的歷史（不改動原列表）。"""
        if self._size(messages) <= self.max_chars:
            return list(messages)

        system, task = messages[0], messages[1]
        # loop.py 的循環不變量：messages[2:] 是一對對 (assistant, user)。
        # 必須成對丟棄，否則歷史裡會出現「沒有結果的工具調用」。
        budget = self.max_chars - len(system["content"]) - len(task["content"])
        body = messages[2:]

        kept: List[dict] = []
        used = 0
        index = len(body)
        while index >= 2:  # 從最新的一對往回收集
            pair = body[index - 2: index]
            pair_size = sum(len(m["content"]) for m in pair)
            if used + pair_size > budget:
                break
            kept = pair + kept
            used += pair_size
            index -= 2

        dropped_pairs = index // 2
        result = [system, task]
        if dropped_pairs > 0:
            result.append({"role": "user", "content": self.truncation_note})
        result.extend(kept)
        return result
