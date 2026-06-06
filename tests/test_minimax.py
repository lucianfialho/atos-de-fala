import pytest
from atos.gen.minimax import MiniMaxClient


def test_extract_content_pulls_message_text():
    resp = {
        "choices": [
            {"message": {"role": "assistant", "content": '{"text":"Oi","spans":[]}'}}
        ]
    }
    assert MiniMaxClient._extract_content(resp) == '{"text":"Oi","spans":[]}'


def test_extract_content_raises_on_empty_choices():
    with pytest.raises(ValueError):
        MiniMaxClient._extract_content({"choices": []})


def test_complete_posts_and_returns_content(monkeypatch):
    captured = {}

    class FakeResp:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": "ola"}}]}

        def raise_for_status(self):
            pass

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResp()

    monkeypatch.setattr("atos.gen.minimax.requests.post", fake_post)
    client = MiniMaxClient(api_key="KEY", model="MiniMax-Text-01")
    out = client.complete([{"role": "user", "content": "oi"}])
    assert out == "ola"
    assert captured["headers"]["Authorization"] == "Bearer KEY"
    assert captured["json"]["model"] == "MiniMax-Text-01"
    assert captured["json"]["messages"] == [{"role": "user", "content": "oi"}]


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    with pytest.raises(ValueError):
        MiniMaxClient()
