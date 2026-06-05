from typing import Dict, List, Optional
import os
import requests

DEFAULT_BASE_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-6"
ANTHROPIC_VERSION = "2023-06-01"


class ClaudeClient:
    """Minimal HTTP client for the Anthropic Messages API.

    The Anthropic API takes 'system' as a top-level field (not a message role),
    so complete() splits any system message out of the messages list.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        max_tokens: int = 2048,
        timeout: int = 120,
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set and no api_key passed")
        self.model = model
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.timeout = timeout

    @staticmethod
    def _extract_content(resp: Dict) -> str:
        blocks = resp.get("content") or []
        texts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
        joined = "".join(texts)
        if not joined:
            raise ValueError(f"empty content in Claude response: {resp!r}")
        return joined

    def complete(self, messages: List[Dict]) -> str:
        system = None
        convo = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                convo.append(m)
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": convo,
        }
        if system is not None:
            payload["system"] = system
        r = requests.post(
            self.base_url, headers=headers, json=payload, timeout=self.timeout
        )
        r.raise_for_status()
        return self._extract_content(r.json())
