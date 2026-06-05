import pytest
from chomsky.gen.claude import ClaudeClient


def test_extract_content_joins_text_blocks():
    resp = {"content": [{"type": "text", "text": '{"text":"Oi",'}, {"type": "text", "text": '"spans":[]}'}]}
    assert ClaudeClient._extract_content(resp) == '{"text":"Oi","spans":[]}'


def test_extract_content_raises_on_empty():
    with pytest.raises(ValueError):
        ClaudeClient._extract_content({"content": []})


def test_complete_posts_system_separately(monkeypatch):
    captured = {}

    class FakeResp:
        status_code = 200

        def json(self):
            return {"content": [{"type": "text", "text": "ola"}]}

        def raise_for_status(self):
            pass

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResp()

    monkeypatch.setattr("chomsky.gen.claude.requests.post", fake_post)
    client = ClaudeClient(api_key="KEY", model="claude-sonnet-4-6")
    msgs = [
        {"role": "system", "content": "SYS"},
        {"role": "user", "content": "oi"},
    ]
    out = client.complete(msgs)
    assert out == "ola"
    assert captured["headers"]["x-api-key"] == "KEY"
    assert captured["headers"]["anthropic-version"] == "2023-06-01"
    # system goes to the top-level 'system' field, not into messages
    assert captured["json"]["system"] == "SYS"
    assert captured["json"]["messages"] == [{"role": "user", "content": "oi"}]
    assert captured["json"]["max_tokens"] > 0


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError):
        ClaudeClient()
