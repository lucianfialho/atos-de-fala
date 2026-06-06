from chomsky.collect.confirm import build_paraphrase_check_prompt, confirm_suggestion


class FakeClient:
    def __init__(self, reply):
        self.reply = reply
        self.last_messages = None

    def complete(self, messages):
        self.last_messages = messages
        return self.reply


def test_prompt_includes_act_original_and_paraphrase():
    msgs = build_paraphrase_check_prompt("pedir", "Pode me enviar?", "Me manda aí?")
    blob = " ".join(m["content"] for m in msgs)
    assert "pedir" in blob and "Pode me enviar?" in blob and "Me manda aí?" in blob


def test_confirm_true_when_model_says_preserves():
    client = FakeClient('{"preserves": true}')
    assert confirm_suggestion(client, "pedir", "Pode me enviar?", "Me manda aí?") is True


def test_confirm_false_when_model_says_not_preserves():
    client = FakeClient('{"preserves": false}')
    assert confirm_suggestion(client, "pedir", "Pode me enviar?", "Bom dia!") is False


def test_confirm_false_when_key_missing():
    client = FakeClient("{}")
    assert confirm_suggestion(client, "pedir", "x", "y") is False
