# Generation Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the synthetic-data generation pipeline that turns the teacher LLMs (MiniMax bulk + Claude adjudicator) into a validated, gold-quality JSONL dataset of PT-BR texts annotated with speech-act spans — reusing the Plan-1 annotation core.

**Architecture:** API I/O lives only in thin client wrappers (`minimax.py`, `claude.py`) whose response *parsing* is unit-tested; the orchestration (`pipeline.py`) is a pure function that takes *injected annotator callables*, so the full generate→resolve→validate→agreement→adjudicate→accept flow is testable offline with fakes. Output is char-offset annotations (`{text, spans:[{start,end,act}]}`) as JSONL — tokenization + BIOES is deferred to Plan 3 (training), where the tokenizer lives. Everything stays config-driven on `config/taxonomy.yaml` + `config/rubric.md`.

**Tech Stack:** Python ≥3.10, `requests` (HTTP to MiniMax + Anthropic), the existing `atos` package (schema, taxonomy, resolve, validator, agreement), `pytest` (tests monkeypatch `requests`, no live calls).

---

## Scope

This is **Plan 2 of 3** (see `docs/superpowers/specs/2026-06-04-speech-act-span-classifier-design.md`). It delivers the generation pipeline + CLI that produces `data/dataset.jsonl`. It does NOT include BERTimbau fine-tuning or eval CLI (Plan 3).

**Dependency note:** The pipeline is taxonomy-agnostic (reads `config/taxonomy.yaml`). The only Fase-0-dependent artifact is `config/rubric.md` (act definitions + few-shot examples), which is data, not code. The code here can be built and tested now with the provisional taxonomy; the rubric is finalized after Fase 0 freezes the taxonomy.

**API testing:** Live MiniMax/Claude calls are NOT unit-tested. Client HTTP is exercised via monkeypatched `requests`; correctness of the live integration is checked by a manual smoke step (Task 6, Step 6).

## File Structure

```
atos/
├── pyproject.toml                  # MODIFY: add optional 'gen' deps (requests)
├── config/
│   └── rubric.md                   # CREATE: provisional annotation rubric + few-shot
├── src/atos/gen/
│   ├── __init__.py
│   ├── prompts.py                  # build prompts + parse_llm_json (robust JSON extraction)
│   ├── minimax.py                  # MiniMaxClient: HTTP + _extract_content
│   ├── claude.py                   # ClaudeClient: HTTP + _extract_content
│   ├── pipeline.py                 # process_example (pure orchestration, injected callables)
│   ├── dataset.py                  # JSONL append+flush, resume (load_done_texts)
│   └── cli.py                      # wire real clients, loop to N, resume
├── data/                           # output (gitignored, already in .gitignore)
└── tests/
    ├── test_prompts.py
    ├── test_minimax.py
    ├── test_claude.py
    ├── test_pipeline_gen.py
    └── test_dataset.py
```

**Interfaces locked here:**
- `prompts.parse_llm_json(raw: str) -> dict` → `{"text": str, "spans": [{"quote": str, "act": str}]}`; raises `ValueError` if unparseable. The `spans` items are exactly the input shape for `atos.resolve.resolve_quoted_spans`.
- `prompts.build_generation_prompt(rubric: str, n: int) -> list[dict]` and `prompts.build_annotation_prompt(rubric: str, text: str) -> list[dict]` → chat `messages`.
- `minimax.MiniMaxClient(api_key=None, model=..., base_url=...).complete(messages) -> str`; static `_extract_content(resp: dict) -> str`.
- `claude.ClaudeClient(api_key=None, model=..., base_url=...).complete(messages) -> str`; static `_extract_content(resp: dict) -> str`.
- `pipeline.process_example(text, items_primary, *, taxonomy, cross_annotate=None, adjudicate=None, threshold=0.8) -> ExampleResult` where `ExampleResult(annotation: Annotation|None, status: str, reason: str, agreement: float|None)`.
- `dataset.append_annotation(path, ann) -> None`; `dataset.load_done_texts(path) -> set[str]`.

---

## Task 0: gen subpackage scaffold + deps

**Files:**
- Modify: `pyproject.toml`
- Create: `src/atos/gen/__init__.py`

- [ ] **Step 1: Add the `gen` optional dependency group to `pyproject.toml`**

Find the `[project.optional-dependencies]` block (currently has `dev = ["pytest>=8.0"]`) and add a `gen` line so it reads:

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0"]
gen = ["requests>=2.31"]
```

- [ ] **Step 2: Create the subpackage marker**

```python
# src/atos/gen/__init__.py
"""atos.gen — synthetic speech-act dataset generation pipeline."""
```

- [ ] **Step 3: Install the new extras into the existing venv**

Run:
```bash
cd /Users/lucianfialho/Code/antiachismosocialclub/atos
.venv/bin/pip install -q -e ".[dev,gen]"
.venv/bin/python -c "import requests; print('requests', requests.__version__)"
```
Expected: prints a requests version (e.g. `requests 2.31.0` or newer).

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml src/atos/gen/__init__.py
git commit -m "chore: scaffold atos.gen subpackage + requests dep"
```

---

## Task 1: Prompt builders + robust JSON parsing (`prompts.py`)

LLMs wrap JSON in prose or ```json fences. `parse_llm_json` must extract the JSON object and validate its shape.

**Files:**
- Create: `src/atos/gen/prompts.py`
- Test: `tests/test_prompts.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_prompts.py
import pytest
from atos.gen.prompts import (
    parse_llm_json,
    build_generation_prompt,
    build_annotation_prompt,
)


def test_parses_bare_json():
    raw = '{"text": "Oi!", "spans": [{"quote": "Oi!", "act": "saudar"}]}'
    obj = parse_llm_json(raw)
    assert obj["text"] == "Oi!"
    assert obj["spans"] == [{"quote": "Oi!", "act": "saudar"}]


def test_parses_json_inside_markdown_fence():
    raw = 'Claro! Aqui:\n```json\n{"text": "Oi!", "spans": []}\n```\nEspero ajudar.'
    obj = parse_llm_json(raw)
    assert obj["text"] == "Oi!"
    assert obj["spans"] == []


def test_parses_json_with_surrounding_prose():
    raw = 'Resposta: {"text": "Vem?", "spans": [{"quote": "Vem?", "act": "pedir"}]} fim'
    obj = parse_llm_json(raw)
    assert obj["text"] == "Vem?"


def test_raises_on_no_json():
    with pytest.raises(ValueError):
        parse_llm_json("desculpe, nao consigo responder")


def test_raises_on_missing_keys():
    with pytest.raises(ValueError):
        parse_llm_json('{"text": "Oi"}')  # no spans


def test_build_generation_prompt_includes_rubric_and_count():
    msgs = build_generation_prompt("RUBRICA_AQUI", 5)
    assert isinstance(msgs, list) and msgs[-1]["role"] == "user"
    joined = " ".join(m["content"] for m in msgs)
    assert "RUBRICA_AQUI" in joined
    assert "5" in joined


def test_build_annotation_prompt_includes_text():
    msgs = build_annotation_prompt("RUBRICA", "Bom dia!")
    joined = " ".join(m["content"] for m in msgs)
    assert "RUBRICA" in joined
    assert "Bom dia!" in joined
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_prompts.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.gen.prompts'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/gen/prompts.py
from typing import Dict, List
import json
import re

_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def parse_llm_json(raw: str) -> Dict:
    """Extract and validate a {text, spans:[{quote,act}]} object from an LLM reply.

    Tries, in order: a ```json fenced block, then the first balanced-looking
    object via the outermost braces. Raises ValueError if nothing parses or the
    required shape is missing.
    """
    candidate = None
    m = _FENCE.search(raw)
    if m:
        candidate = m.group(1)
    else:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = raw[start : end + 1]
    if candidate is None:
        raise ValueError(f"no JSON object found in LLM reply: {raw[:120]!r}")
    try:
        obj = json.loads(candidate)
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON in LLM reply: {e}") from e
    if not isinstance(obj, dict) or "text" not in obj or "spans" not in obj:
        raise ValueError(f"missing 'text'/'spans' keys: {obj!r}")
    return obj


_SYSTEM = (
    "Voce e um anotador linguistico especialista em atos de fala do portugues "
    "brasileiro. Voce sempre responde APENAS com um objeto JSON valido."
)


def build_generation_prompt(rubric: str, n: int) -> List[Dict]:
    user = (
        f"{rubric}\n\n"
        f"Gere {n} exemplo(s). Para CADA exemplo, escreva um texto curto e natural "
        f"em portugues brasileiro e anote os spans de atos de fala. Responda com UM "
        f'objeto JSON por exemplo no formato: '
        f'{{"text": "...", "spans": [{{"quote": "trecho exato do texto", "act": "<ato>"}}]}}. '
        f"Os 'quote' devem ser substrings EXATAS e contiguas do 'text'."
    )
    return [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}]


def build_annotation_prompt(rubric: str, text: str) -> List[Dict]:
    user = (
        f"{rubric}\n\n"
        f"Anote os atos de fala do texto a seguir. NAO altere o texto. Responda com "
        f'um objeto JSON: {{"text": "<o texto original, inalterado>", '
        f'"spans": [{{"quote": "trecho exato", "act": "<ato>"}}]}}.\n\n'
        f"TEXTO:\n{text}"
    )
    return [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_prompts.py -q`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/gen/prompts.py tests/test_prompts.py
git commit -m "feat(gen): prompt builders + robust LLM JSON parsing"
```

---

## Task 2: MiniMax client (`minimax.py`)

Thin HTTP wrapper. Only the response-content extraction is unit-tested; the live POST is monkeypatched in tests.

**Files:**
- Create: `src/atos/gen/minimax.py`
- Test: `tests/test_minimax.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_minimax.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_minimax.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.gen.minimax'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/gen/minimax.py
from typing import Dict, List, Optional
import os
import requests

DEFAULT_BASE_URL = "https://api.minimax.io/v1/text/chatcompletion_v2"
DEFAULT_MODEL = "MiniMax-Text-01"


class MiniMaxClient:
    """Minimal HTTP client for MiniMax chat completions.

    Uses raw HTTP (not an SDK) on purpose — see wiki concept multi-provider-generation
    for the documented gotchas (reasoning models burn max_tokens on thinking, errors
    are easy to swallow). Non-2xx responses raise via raise_for_status.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 120,
    ):
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY")
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY not set and no api_key passed")
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    @staticmethod
    def _extract_content(resp: Dict) -> str:
        choices = resp.get("choices") or []
        if not choices:
            raise ValueError(f"no choices in MiniMax response: {resp!r}")
        content = choices[0].get("message", {}).get("content")
        if not content:
            raise ValueError(f"empty content in MiniMax response: {resp!r}")
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_minimax.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/gen/minimax.py tests/test_minimax.py
git commit -m "feat(gen): MiniMax HTTP client + content extraction"
```

---

## Task 3: Claude client (`claude.py`)

Thin HTTP wrapper for the Anthropic Messages API. Same testing approach.

**Files:**
- Create: `src/atos/gen/claude.py`
- Test: `tests/test_claude.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_claude.py
import pytest
from atos.gen.claude import ClaudeClient


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

    monkeypatch.setattr("atos.gen.claude.requests.post", fake_post)
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_claude.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.gen.claude'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/gen/claude.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_claude.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/gen/claude.py tests/test_claude.py
git commit -m "feat(gen): Claude (Anthropic Messages) HTTP client + content extraction"
```

---

## Task 4: Pure orchestration (`pipeline.py`)

The heart of the teacher mixture, as a pure function with injected annotator callables. No network here.

**Files:**
- Create: `src/atos/gen/pipeline.py`
- Test: `tests/test_pipeline_gen.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pipeline_gen.py
from atos.gen.pipeline import process_example, ExampleResult
from atos.schema import Span
from atos.taxonomy import Taxonomy

TAX = Taxonomy(
    acts=["saudar", "pedir", "sugerir"],
    definitions={"saudar": "", "pedir": "", "sugerir": ""},
)
TEXT = "Bom dia! Pode vir?"
GOOD = [{"quote": "Bom dia!", "act": "saudar"}, {"quote": "Pode vir?", "act": "pedir"}]


def test_valid_primary_no_crosscheck_is_accepted():
    res = process_example(TEXT, GOOD, taxonomy=TAX)
    assert res.status == "accepted"
    assert res.annotation.spans == [Span(0, 8, "saudar"), Span(9, 18, "pedir")]
    assert res.agreement is None


def test_invalid_primary_without_adjudicator_is_rejected():
    bad = [{"quote": "Bom dia!", "act": "xingar"}]  # illegal act
    res = process_example(TEXT, bad, taxonomy=TAX)
    assert res.status == "rejected"
    assert res.annotation is None


def test_invalid_primary_is_fixed_by_adjudicator():
    bad = [{"quote": "naoexiste", "act": "saudar"}]  # quote not in text

    def adjudicate(text, problems):
        return GOOD

    res = process_example(TEXT, bad, taxonomy=TAX, adjudicate=adjudicate)
    assert res.status == "adjudicated"
    assert res.annotation.spans[0] == Span(0, 8, "saudar")


def test_high_agreement_crosscheck_accepts_primary():
    def cross(text):
        return GOOD  # identical -> agreement 1.0

    res = process_example(TEXT, GOOD, taxonomy=TAX, cross_annotate=cross, threshold=0.8)
    assert res.status == "accepted"
    assert res.agreement == 1.0


def test_low_agreement_routes_to_adjudicator():
    def cross(text):
        return [{"quote": "Pode vir?", "act": "sugerir"}]  # disagrees

    def adjudicate(text, problems):
        return GOOD

    res = process_example(
        TEXT, GOOD, taxonomy=TAX, cross_annotate=cross, adjudicate=adjudicate, threshold=0.9
    )
    assert res.status == "adjudicated"
    assert res.agreement is not None and res.agreement < 0.9


def test_low_agreement_without_adjudicator_is_rejected():
    def cross(text):
        return [{"quote": "Pode vir?", "act": "sugerir"}]

    res = process_example(
        TEXT, GOOD, taxonomy=TAX, cross_annotate=cross, threshold=0.9
    )
    assert res.status == "rejected"
    assert res.agreement is not None and res.agreement < 0.9
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_pipeline_gen.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.gen.pipeline'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/gen/pipeline.py
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from atos.schema import Annotation
from atos.taxonomy import Taxonomy
from atos.resolve import resolve_quoted_spans
from atos.validator import validate
from atos.agreement import span_agreement

Items = List[Dict]
Annotator = Callable[[str], Items]
Adjudicator = Callable[[str, List[str]], Items]


@dataclass
class ExampleResult:
    annotation: Optional[Annotation]
    status: str  # "accepted" | "adjudicated" | "rejected"
    reason: str
    agreement: Optional[float]


def _resolve_and_validate(text: str, items: Items, taxonomy: Taxonomy):
    ann, errs = resolve_quoted_spans(text, items)
    errs = list(errs) + validate(ann, taxonomy)
    return ann, errs


def process_example(
    text: str,
    items_primary: Items,
    *,
    taxonomy: Taxonomy,
    cross_annotate: Optional[Annotator] = None,
    adjudicate: Optional[Adjudicator] = None,
    threshold: float = 0.8,
) -> ExampleResult:
    """Run one example through the teacher-mixture pipeline (pure; inject callables).

    Flow: resolve+validate primary -> (if invalid) adjudicate or reject ->
    (if cross_annotate) measure agreement -> keep if >= threshold else adjudicate
    or reject. Returns the accepted/adjudicated Annotation or a rejection.
    """
    ann, errs = _resolve_and_validate(text, items_primary, taxonomy)
    if errs:
        if adjudicate is None:
            return ExampleResult(None, "rejected", f"invalid primary: {errs}", None)
        fixed, ferrs = _resolve_and_validate(text, adjudicate(text, errs), taxonomy)
        if ferrs:
            return ExampleResult(None, "rejected", f"invalid after adjudication: {ferrs}", None)
        return ExampleResult(fixed, "adjudicated", "fixed invalid primary", None)

    if cross_annotate is None:
        return ExampleResult(ann, "accepted", "primary valid, no cross-check", None)

    ann_b, _ = resolve_quoted_spans(text, cross_annotate(text))
    score = span_agreement(ann, ann_b)
    if score >= threshold:
        return ExampleResult(ann, "accepted", "high agreement", score)
    if adjudicate is None:
        return ExampleResult(None, "rejected", f"low agreement {score:.3f}", score)
    fixed, ferrs = _resolve_and_validate(text, adjudicate(text, [f"agreement {score:.3f}"]), taxonomy)
    if ferrs:
        return ExampleResult(None, "rejected", f"invalid adjudication: {ferrs}", score)
    return ExampleResult(fixed, "adjudicated", "low agreement adjudicated", score)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_pipeline_gen.py -q`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/gen/pipeline.py tests/test_pipeline_gen.py
git commit -m "feat(gen): pure teacher-mixture orchestration (process_example)"
```

---

## Task 5: JSONL dataset writer + resume (`dataset.py`)

Append-each-with-flush (resume-from-disk discipline from the Privacy Filter BR lessons) and a loader that returns already-written texts so the CLI can resume without duplicates.

**Files:**
- Create: `src/atos/gen/dataset.py`
- Test: `tests/test_dataset.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_dataset.py
from atos.gen.dataset import append_annotation, load_done_texts
from atos.schema import Annotation, Span


def test_load_done_texts_missing_file_is_empty(tmp_path):
    assert load_done_texts(str(tmp_path / "nope.jsonl")) == set()


def test_append_then_load_roundtrip(tmp_path):
    p = str(tmp_path / "out.jsonl")
    append_annotation(p, Annotation("Oi!", [Span(0, 3, "saudar")]))
    append_annotation(p, Annotation("Vem?", [Span(0, 4, "pedir")]))
    assert load_done_texts(p) == {"Oi!", "Vem?"}


def test_each_record_is_one_json_line(tmp_path):
    p = str(tmp_path / "out.jsonl")
    append_annotation(p, Annotation("Oi!", [Span(0, 3, "saudar")]))
    append_annotation(p, Annotation("Vem?", []))
    with open(p, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    assert len(lines) == 2
    import json
    assert json.loads(lines[0])["text"] == "Oi!"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_dataset.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.gen.dataset'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/gen/dataset.py
import json
import os
from typing import Set
from atos.schema import Annotation


def append_annotation(path: str, ann: Annotation) -> None:
    """Append one Annotation as a JSON line and flush immediately (crash-safe resume)."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(ann.to_json() + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_done_texts(path: str) -> Set[str]:
    """Return the set of texts already written, so generation can resume w/o dupes."""
    if not os.path.exists(path):
        return set()
    done: Set[str] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            done.add(json.loads(line)["text"])
    return done
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_dataset.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/gen/dataset.py tests/test_dataset.py
git commit -m "feat(gen): JSONL writer with fsync + resume loader"
```

---

## Task 6: CLI wiring (`cli.py`) + provisional rubric

Wires real clients into the pipeline. Generation is an integration concern; the unit check is that the module imports and `--help` works. A manual smoke step exercises the live path with 1 example.

**Files:**
- Create: `src/atos/gen/cli.py`
- Create: `config/rubric.md`
- Test: `tests/test_cli_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli_smoke.py
import subprocess
import sys


def test_cli_help_runs():
    r = subprocess.run(
        [sys.executable, "-m", "atos.gen.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert "--n" in r.stdout
    assert "--out" in r.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_cli_smoke.py -q`
Expected: FAIL (module `atos.gen.cli` has no `__main__` / import error)

- [ ] **Step 3: Create the provisional rubric**

```markdown
<!-- config/rubric.md -->
<!-- PROVISIONAL — finalize after Fase 0 freezes the taxonomy (paper7 ingestion). -->
# Rúbrica de Anotação — Atos de Fala (PT-BR)

Você anota **atos de fala** em texto português. Cada span é um trecho contíguo do
texto que realiza um ato. Spans NÃO se sobrepõem. Use apenas os atos abaixo.

## Atos

- **afirmar**: declarar algo como verdadeiro. Ex.: "O relatório está pronto."
- **perguntar**: solicitar informação. Ex.: "Que horas são?"
- **pedir**: requisitar uma ação. Ex.: "Me envia o arquivo?"
- **sugerir**: propor sem obrigar. Ex.: "Talvez seja melhor esperar."
- **prometer**: comprometer-se com ação futura. Ex.: "Eu te aviso amanhã."
- **agradecer**: expressar gratidão. Ex.: "Muito obrigado!"
- **concordar**: manifestar acordo. Ex.: "Sim, exatamente."
- **discordar**: manifestar desacordo. Ex.: "Não acho isso."
- **saudar**: iniciar contato. Ex.: "Bom dia!"
- **despedir**: encerrar contato. Ex.: "Até logo!"
- **informar**: prover informação não solicitada. Ex.: "A reunião mudou para as 15h."
- **expressar_emocao**: manifestar emoção. Ex.: "Que alívio!"

## Exemplo anotado

Texto: "Oi! Pode me mandar o relatório? Prometo revisar hoje."
```json
{"text": "Oi! Pode me mandar o relatório? Prometo revisar hoje.",
 "spans": [
   {"quote": "Oi!", "act": "saudar"},
   {"quote": "Pode me mandar o relatório?", "act": "pedir"},
   {"quote": "Prometo revisar hoje.", "act": "prometer"}
 ]}
```
```

- [ ] **Step 4: Write the CLI implementation**

```python
# src/atos/gen/cli.py
import argparse
import os
import sys
from typing import List, Dict
from atos.taxonomy import load_taxonomy
from atos.gen.prompts import (
    parse_llm_json,
    build_generation_prompt,
    build_annotation_prompt,
)
from atos.gen.minimax import MiniMaxClient
from atos.gen.claude import ClaudeClient
from atos.gen.pipeline import process_example
from atos.gen.dataset import append_annotation, load_done_texts


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atos.gen.cli",
        description="Generate a synthetic speech-act span dataset (MiniMax bulk + Claude adjudicator).",
    )
    p.add_argument("--n", type=int, required=True, help="number of accepted examples to reach")
    p.add_argument("--out", required=True, help="output JSONL path (append + resume)")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--rubric", default="config/rubric.md")
    p.add_argument("--cross-check-rate", type=float, default=0.15,
                   help="fraction of examples also annotated by Claude for agreement")
    p.add_argument("--threshold", type=float, default=0.8)
    p.add_argument("--debug", action="store_true")
    return p


def run(args) -> int:
    taxonomy = load_taxonomy(args.taxonomy)
    rubric = _read(args.rubric)
    mm = MiniMaxClient()
    cl = ClaudeClient()

    def mm_generate_one() -> Dict:
        raw = mm.complete(build_generation_prompt(rubric, 1))
        return parse_llm_json(raw)

    def cl_annotate(text: str) -> List[Dict]:
        raw = cl.complete(build_annotation_prompt(rubric, text))
        return parse_llm_json(raw)["spans"]

    def adjudicate(text: str, problems: List[str]) -> List[Dict]:
        raw = cl.complete(build_annotation_prompt(rubric, text))
        return parse_llm_json(raw)["spans"]

    done = load_done_texts(args.out)
    accepted = len(done)
    # deterministic cross-check selection: every Kth example (avoids RNG, resume-stable)
    every = max(1, round(1 / args.cross_check_rate)) if args.cross_check_rate > 0 else 0
    seen = 0
    while accepted < args.n:
        seen += 1
        try:
            obj = mm_generate_one()
        except Exception as e:  # noqa: BLE001 — log and continue (don't crash the run)
            if args.debug:
                print(f"[gen-error] {e}", file=sys.stderr)
            continue
        text = obj["text"]
        if text in done:
            continue
        cross = cl_annotate if (every and seen % every == 0) else None
        res = process_example(
            text, obj["spans"], taxonomy=taxonomy,
            cross_annotate=cross, adjudicate=adjudicate, threshold=args.threshold,
        )
        if args.debug:
            print(f"[{res.status}] agree={res.agreement} {res.reason} :: {text[:60]!r}",
                  file=sys.stderr)
        if res.annotation is not None:
            append_annotation(args.out, res.annotation)
            done.add(text)
            accepted += 1
            print(f"accepted {accepted}/{args.n}")
    return 0


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_cli_smoke.py -q`
Expected: PASS (1 passed)

- [ ] **Step 6: Manual live smoke test (requires MINIMAX_API_KEY + ANTHROPIC_API_KEY)**

This step is NOT automated. With both keys exported, generate 3 examples into a scratch file:
```bash
MINIMAX_API_KEY=... ANTHROPIC_API_KEY=... \
  .venv/bin/python -m atos.gen.cli --n 3 --out data/smoke.jsonl --cross-check-rate 1.0 --debug
```
Expected: 3 lines in `data/smoke.jsonl`, each valid JSON with non-empty `spans`, and debug lines showing `[accepted]`/`[adjudicated]`. Inspect a couple by hand to confirm the spans are sane PT-BR speech acts. If MiniMax reasoning eats the token budget (empty content), see wiki `multi-provider-generation` and set a non-reasoning model. `data/` is gitignored — do not commit `smoke.jsonl`.

- [ ] **Step 7: Run the full suite**

Run: `.venv/bin/pytest -q`
Expected: PASS (all Plan-1 + Plan-2 tests; ~55 passed)

- [ ] **Step 8: Commit**

```bash
git add src/atos/gen/cli.py config/rubric.md tests/test_cli_smoke.py
git commit -m "feat(gen): generation CLI + provisional annotation rubric"
```

---

## Task 7: Wiki bookkeeping

**Files:**
- Create: `wiki/concepts/teacher-mixture-pipeline.md`
- Modify: `log.md` (append)
- Modify: `index.md` (add concept under "Datasets & Data Generation")

- [ ] **Step 1: Create the concept page**

```markdown
---
type: concept
tags: [synthetic-data, teacher-student, distillation, speech-acts, atos-project]
sources: 0
updated: 2026-06-04
---

# Teacher-Mixture Generation Pipeline

## Definition

The synthetic-data pipeline for the speech-act classifier: MiniMax (bulk teacher) generates
PT-BR text + span annotations; Claude (adjudicator) re-annotates a sampled fraction and fixes
disagreements/invalid cases. Only validated, high-agreement-or-adjudicated examples reach the
training JSONL. The student (BERTimbau, Plan 3) distills the result.

## How It Works

Per example (pure function `atos.gen.pipeline.process_example`): resolve quotes→offsets →
validate against the taxonomy → if invalid, Claude adjudicates or the example is rejected →
on a sampled fraction, Claude cross-annotates and span-F1 agreement is measured → keep if
≥ threshold, else adjudicate or reject. API I/O is isolated in thin clients; orchestration is
pure (injected callables), so it is fully unit-tested offline.

## Why It Matters

Teacher quality is the ceiling on the student. The agreement gate + adjudication protect label
quality at low cost: cheap bulk from MiniMax, expensive Claude only where it matters. Reuses the
Privacy Filter BR lessons (resume-from-disk with fsync; MiniMax reasoning gotchas).

## Related Concepts

- [Synthetic Data Generation](synthetic-data-generation.md)
- [Multi-Provider Generation](multi-provider-generation.md)
- [Speech Act Label Scheme](speech-act-label-scheme.md)

## Sources

- Design spec: `docs/superpowers/specs/2026-06-04-speech-act-span-classifier-design.md`
- Plan: `docs/superpowers/plans/2026-06-04-generation-pipeline.md`
```

- [ ] **Step 2: Append to `log.md`**

```markdown
## [2026-06-04] build | Generation Pipeline (Plan 2)
Implementado o pipeline de geração sintética: prompts + parse robusto de JSON do LLM, clients HTTP MiniMax e Claude (parsing testável), orquestração pura da mistura teacher (process_example com callables injetados), writer JSONL com fsync + resume, e CLI. Rúbrica provisória de anotação em config/rubric.md. Testes offline com requests monkeypatched + smoke manual. Taxonomia/rúbrica a finalizar após Fase 0.
```

- [ ] **Step 3: Add to `index.md`** under "### Datasets & Data Generation" (as the last bullet of that section):

```markdown
- [Teacher-Mixture Generation Pipeline](wiki/concepts/teacher-mixture-pipeline.md) — MiniMax bulk + Claude adjudicador, agreement gate, orquestração pura; produz JSONL gold pra destilação
```

- [ ] **Step 4: Commit**

```bash
git add wiki/concepts/teacher-mixture-pipeline.md log.md index.md
git commit -m "docs(wiki): record generation pipeline build + concept"
```

---

## Self-Review

**1. Spec coverage (Plan 2 portion of the design spec):**
- Teacher = mixture (Claude rubric/gold + adjudication, MiniMax bulk) → Tasks 2,3,6 (clients) + Task 4 (orchestration roles). ✓
- LLM generates quoted-substring annotations → `prompts.build_generation_prompt` + `parse_llm_json` (Task 1). ✓
- resolve → validate → agreement gate → adjudicate → accept → `process_example` (Task 4). ✓
- Agreement gate on a sampled fraction (`--cross-check-rate`) → Task 6 CLI. ✓
- Validator (verbatim + label legality) reused from Plan 1 → Task 4 `_resolve_and_validate`. ✓
- Resume-from-disk with flush → Task 5 `append_annotation` (fsync) + `load_done_texts`. ✓
- MiniMax gotchas documented/referenced → Task 2 docstring + Task 6 smoke note + wiki (Task 7). ✓
- Output is char-offset annotations JSONL; tokenization/BIOES deferred to Plan 3 → stated in Architecture + dataset.py. ✓
- Config-driven taxonomy + rubric (swap after Fase 0) → Tasks 6,7 + Scope note. ✓
- **Deferred to Plan 3:** BERTimbau LoRA training, tokenizer offset wrapper + bioes at train time, span-F1 eval CLI on a model, real-text holdout.

**2. Placeholder scan:** No "TBD"/"handle errors"/vague steps. Every code step has full code; every run step has command + expected output. The rubric and CLI prints are concrete. The one explicitly non-automated step (Task 6 Step 6, live smoke) is clearly labeled as manual and has exact command + expected outcome. ✓

**3. Type consistency:** `parse_llm_json` returns `{text, spans:[{quote,act}]}`; `process_example(text, items_primary,...)` consumes `items` = `[{quote,act}]` (matches `resolve_quoted_spans` input from Plan 1). `ExampleResult(annotation, status, reason, agreement)` used consistently in tests + CLI. Client `complete(messages) -> str` + static `_extract_content(resp) -> str` consistent across minimax.py/claude.py and their tests. `append_annotation(path, ann)` / `load_done_texts(path)` consistent (Task 5 + CLI). CLI uses `obj["text"]`, `obj["spans"]` — matches `parse_llm_json` contract. ✓

---

## Done criteria

`.venv/bin/pytest -q` green (Plan 1 + Plan 2, ~55 tests), `python -m atos.gen.cli --help` works, and the manual live smoke (Task 6 Step 6) produces sane PT-BR speech-act annotations. After Fase 0 freezes the taxonomy, only `config/taxonomy.yaml` + `config/rubric.md` change; code and tests are unaffected. Plan 3 (training) then consumes `data/dataset.jsonl`.
