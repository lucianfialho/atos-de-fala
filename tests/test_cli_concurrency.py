import itertools
import json
from chomsky.gen import cli
from chomsky.gen.dataset import load_done_annotations


def _fake_post_factory():
    """Returns a thread-safe fake requests.post yielding a unique valid example each call."""
    counter = itertools.count()

    def fake_post(url, headers=None, json=None, timeout=None):
        i = next(counter)
        content = json_dumps_example(i)

        class R:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": content}}]}

        return R()

    return fake_post


def json_dumps_example(i: int) -> str:
    text = f"frase numero {i} aqui"
    return json.dumps({"text": text, "spans": [{"quote": text, "act": "informar"}]})


def test_run_reaches_n_with_concurrency(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "x")
    monkeypatch.setattr("chomsky.gen.deepseek.requests.post", _fake_post_factory())

    out = tmp_path / "ds.jsonl"
    args = cli.build_arg_parser().parse_args([
        "--n", "5", "--out", str(out),
        "--provider", "deepseek", "--adjudicator", "none",
        "--no-balance", "--cross-check-rate", "0", "--concurrency", "4",
    ])
    rc = cli.run(args)
    assert rc == 0

    anns = load_done_annotations(str(out))
    assert len(anns) == 5
    # all unique texts (dedup held), all the legal act
    assert len({a.text for a in anns}) == 5
    assert all(a.spans[0].act == "informar" for a in anns)


def test_run_resumes_from_existing(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "x")
    monkeypatch.setattr("chomsky.gen.deepseek.requests.post", _fake_post_factory())
    out = tmp_path / "ds.jsonl"
    # pre-seed 2 accepted
    out.write_text(
        '{"text": "ja existe 1", "spans": [{"start": 0, "end": 11, "act": "informar"}]}\n'
        '{"text": "ja existe 2", "spans": [{"start": 0, "end": 11, "act": "informar"}]}\n',
        encoding="utf-8",
    )
    args = cli.build_arg_parser().parse_args([
        "--n", "5", "--out", str(out),
        "--provider", "deepseek", "--adjudicator", "none",
        "--no-balance", "--cross-check-rate", "0", "--concurrency", "3",
    ])
    rc = cli.run(args)
    assert rc == 0
    anns = load_done_annotations(str(out))
    assert len(anns) == 5  # resumed from 2, added 3 more
