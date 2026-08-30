"""LLM 層：harness 眼中的「大腦」只有一個方法——generate(messages) -> str（docs/01）。

提供兩個實現：
- MockLLM：腳本化大腦，按順序吐出預設回覆。零 API Key 即可跑通整個 harness，
  是 demo 與測試的基礎設施；
- OpenAICompatLLM：任何 OpenAI 兼容端點（OpenAI / DeepSeek / 智譜 / Moonshot /
  Ollama / vLLM …）都能接。只用 stdlib 的 urllib，刻意不引入 SDK 依賴——
  讓你親眼看到「一次 LLM 調用其實就是一個 HTTP POST」。
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable, List, Union

# 一條消息就是一個 {"role": ..., "content": ...} 字典——
# 與各家 API 的消息格式一致，序列化時不需要任何轉換。
Message = dict


class BaseLLM:
    """所有大腦的介面。harness 的其餘部分只認識這個方法。"""

    name: str = "base"

    def generate(self, messages: List[Message]) -> str:
        raise NotImplementedError


class MockLLM(BaseLLM):
    """腳本化大腦：按順序「背台詞」。

    script 的每一項是一輪回覆：
    - 字符串：原樣返回；
    - 可調用對象：接收完整消息歷史，返回字符串——用來寫
      「看到 grep 結果再決定寫什麼報告」這種**反應式**劇本，
      正好演示循環賦予模型的能動性。

    劇本耗盡後返回一句兜底回答，保證 demo 永遠能收尾。
    """

    name = "mock"

    def __init__(self, script: List[Union[str, Callable[[List[Message]], str]]]):
        self._script = list(script)
        self._cursor = 0

    def generate(self, messages: List[Message]) -> str:
        if self._cursor >= len(self._script):
            return "（MockLLM 劇本已耗盡）任務完成。"
        item = self._script[self._cursor]
        self._cursor += 1
        return item(messages) if callable(item) else item

    @property
    def remaining(self) -> int:
        return len(self._script) - self._cursor


def validate_endpoint(base_url: str, allow_http: bool = False) -> str:
    """對 LLM 端點做最低限度的校驗：協議白名單 + 主機名非空。

    端點來自環境變量/命令行（操作者自己配置的），不是遠端用戶輸入，
    但 harness 仍然不該對任意 URL 發請求：這裡只放行 https，
    以及明確的本地開發端點（Ollama / vLLM 監聽 127.0.0.1 的場景）。
    """
    parsed = urllib.parse.urlparse(base_url)
    host = parsed.hostname or ""
    loopback = host in ("localhost", "127.0.0.1", "::1")
    if parsed.scheme == "https":
        pass
    elif parsed.scheme == "http" and (allow_http or loopback):
        pass
    else:
        raise ValueError(
            f"不支持的 LLM 端點 '{base_url}'：僅允許 https，"
            "或本地 http（localhost/127.0.0.1，或顯式設置 MINIHARNESS_ALLOW_HTTP=1）"
        )
    if not host:
        raise ValueError(f"LLM 端點缺少主機名：'{base_url}'")
    return base_url.rstrip("/")


class OpenAICompatLLM(BaseLLM):
    """任何 OpenAI 兼容的 /chat/completions 端點。

    用法（也是 demo_cli.py 的默認行為）：
        llm = OpenAICompatLLM.from_env()
    環境變量：
        MINIHARNESS_API_KEY / OPENAI_API_KEY   —— 鑰匙
        MINIHARNESS_BASE_URL / OPENAI_BASE_URL —— 端點（默認 OpenAI 官方）
        MINIHARNESS_MODEL                      —— 模型名
    """

    name = "openai-compat"

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        temperature: float = 0.0,
        timeout: int = 180,
        allow_http: bool = False,
    ):
        self.model = model
        self.api_key = api_key
        # 端點在構造時校驗一次，之後 generate 只用這個固定值。
        self.base_url = validate_endpoint(base_url, allow_http=allow_http)
        self.temperature = temperature
        self.timeout = timeout

    @classmethod
    def from_env(cls, **overrides) -> "OpenAICompatLLM":
        api_key = (
            overrides.get("api_key")
            or os.environ.get("MINIHARNESS_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        if not api_key:
            raise RuntimeError(
                "未找到 API Key。請設置環境變量 OPENAI_API_KEY（或 MINIHARNESS_API_KEY）。"
            )
        base_url = (
            overrides.get("base_url")
            or os.environ.get("MINIHARNESS_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        )
        model = overrides.get("model") or os.environ.get("MINIHARNESS_MODEL") or "gpt-4o-mini"
        allow_http = overrides.get(
            "allow_http", os.environ.get("MINIHARNESS_ALLOW_HTTP") == "1"
        )
        return cls(model=model, api_key=api_key, base_url=base_url, allow_http=allow_http)

    def generate(self, messages: List[Message]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        request = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:400]
            raise RuntimeError(f"LLM API 返回 HTTP {exc.code}：{detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"無法連接 LLM API（{self.base_url}）：{exc.reason}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                "LLM API 返回了意料之外的結構：" + json.dumps(data, ensure_ascii=False)[:400]
            ) from exc
        return content or ""
