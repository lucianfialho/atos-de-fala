"""Teacher LLM client factory for corpus annotation. Only pass `model` if overriding the
provider default. Clients are lazily imported so unused providers need no deps/keys."""
import os


def make_client(provider: str, model=None):
    kw = {"model": model} if model else {}
    if provider == "claude":
        from atos.gen.claude import ClaudeClient
        return ClaudeClient(**kw)
    if provider == "kimi-code":
        # Kimi Code subscription — Anthropic-compatible endpoint (ClaudeClient speaks it).
        from atos.gen.claude import ClaudeClient
        key = os.environ.get("KIMI_API_KEY") or os.environ.get("MOONSHOT_API_KEY")
        base = os.environ.get("KIMI_BASE_URL", "https://api.kimi.com/coding/v1/messages")
        return ClaudeClient(api_key=key, base_url=base, model=model or "kimi-k2-0905-preview")
    if provider == "kimi":
        from atos.gen.kimi import KimiClient
        return KimiClient(**kw)
    if provider == "deepseek":
        from atos.gen.deepseek import DeepSeekClient
        return DeepSeekClient(**kw)
    if provider == "minimax":
        from atos.gen.minimax import MiniMaxClient
        return MiniMaxClient(**kw)
    raise ValueError(f"unknown provider: {provider}")
