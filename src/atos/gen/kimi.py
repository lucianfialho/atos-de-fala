"""Kimi K2 (Moonshot) teacher client. OpenAI-compatible, same wire shape as DeepSeek/MiniMax
(Bearer auth, choices[0].message.content), so it reuses DeepSeekClient.complete().

Reads KIMI_API_KEY (or MOONSHOT_API_KEY). Base URL + model overridable via env/arg — Moonshot
has .ai (international) and .cn endpoints, and the K2 model id changes over time.
"""
import os
from typing import Optional

from atos.gen.deepseek import DeepSeekClient

DEFAULT_BASE_URL = "https://api.moonshot.ai/v1/chat/completions"
DEFAULT_MODEL = "kimi-k2-0905-preview"


class KimiClient(DeepSeekClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: Optional[str] = None,
        timeout: int = 120,
    ):
        key = api_key or os.environ.get("KIMI_API_KEY") or os.environ.get("MOONSHOT_API_KEY")
        if not key:
            raise ValueError("KIMI_API_KEY (or MOONSHOT_API_KEY) not set and no api_key passed")
        url = base_url or os.environ.get("KIMI_BASE_URL", DEFAULT_BASE_URL)
        super().__init__(api_key=key, model=model, base_url=url, timeout=timeout)
