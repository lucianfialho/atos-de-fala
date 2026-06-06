from typing import Dict, List, Optional
import os
import requests

DEFAULT_BASE_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"


class DeepSeekClient:
    """Minimal HTTP client for DeepSeek chat completions (OpenAI-compatible).

    Same request/response shape as MiniMax (choices[0].message.content, Bearer auth),
    so it drops into the pipeline as an alternative bulk teacher. DeepSeek pricing is
    very low and the rubric is static (cache-hit), making bulk generation cheap — see
    wiki concept multi-provider-generation. Non-2xx responses raise via raise_for_status.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 120,
    ):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not set and no api_key passed")
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    @staticmethod
    def _extract_content(resp: Dict) -> str:
        choices = resp.get("choices") or []
        if not choices:
            raise ValueError(f"no choices in DeepSeek response: {resp!r}")
        content = choices[0].get("message", {}).get("content")
        if not content:
            raise ValueError(f"empty content in DeepSeek response: {resp!r}")
        return content

    def complete(self, messages: List[Dict]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": messages}
        r = requests.post(
            self.base_url, headers=headers, json=payload, timeout=self.timeout
        )
        r.raise_for_status()
        return self._extract_content(r.json())
