# Annotation Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the pure-logic foundation for span-level speech-act annotation: a taxonomy/BIOES label system, an annotation data model, a quote-resolver, a validator, a BIOES tagger, a double-annotation agreement gate, and a span-level F1 evaluator — all unit-tested, with zero dependency on external APIs, GPU, or network.

**Architecture:** A small Python package `atos` under `src/`. Every speech act and label is derived from a single `config/taxonomy.yaml` so the taxonomy can be swapped (once frozen from the papers) without touching code. The annotation unit is a list of non-overlapping character-offset spans, each carrying a speech-act label. All core functions are pure (no I/O) and take primitive inputs (text, offsets, span lists) so tests are hermetic.

**Tech Stack:** Python ≥3.10, `pyyaml` (config), `pytest` (tests), setuptools (editable install). No torch/transformers in this plan — those land in Plan 3 (Training).

---

## Scope

This plan is **Plan 1 of 3** (see `docs/superpowers/specs/2026-06-04-speech-act-span-classifier-design.md`). It delivers a working, tested annotation library. It does NOT include: the MiniMax/Claude generation clients (Plan 2), or BERTimbau fine-tuning/eval CLI (Plan 3). It is fully buildable now regardless of the arXiv rate-limit or GPU availability.

## File Structure

```
atos/
├── pyproject.toml                 # package + deps + pytest config
├── config/
│   └── taxonomy.yaml              # provisional 12-act taxonomy (swap when frozen)
├── src/atos/
│   ├── __init__.py
│   ├── schema.py                  # Span, Annotation dataclasses + JSON (de)serialize
│   ├── taxonomy.py                # load taxonomy → acts, BIOES labels, label↔id maps
│   ├── resolve.py                 # quoted substrings + act → char-offset Annotation
│   ├── validator.py               # check bounds, legality, non-overlap
│   ├── bioes.py                   # (text, spans, token offsets) → per-token BIOES tags
│   ├── agreement.py               # span-set agreement between two annotations + gate
│   └── eval.py                    # span-level precision/recall/F1 + per-act breakdown
└── tests/
    ├── test_schema.py
    ├── test_taxonomy.py
    ├── test_resolve.py
    ├── test_validator.py
    ├── test_bioes.py
    ├── test_agreement.py
    └── test_eval.py
```

**Module responsibilities (interfaces locked here):**

- `schema.Span(start: int, end: int, act: str)` — frozen dataclass, char offsets `[start, end)`.
- `schema.Annotation(text: str, spans: list[Span])` — `.to_json() -> str`, `Annotation.from_json(s) -> Annotation`.
- `taxonomy.load_taxonomy(path) -> Taxonomy` — `.acts: list[str]`, `.definitions: dict[str,str]`.
- `taxonomy.bioes_labels(acts) -> list[str]`; `taxonomy.label_maps(labels) -> (label2id, id2label)`.
- `resolve.resolve_quoted_spans(text, items) -> tuple[Annotation, list[str]]` — `items: list[dict]` with keys `quote`, `act`.
- `validator.validate(ann, taxonomy) -> list[str]` — returns error strings; empty = valid.
- `bioes.char_spans_to_bioes(spans, offsets) -> list[str]` — `offsets: list[tuple[int,int]]`.
- `agreement.span_agreement(a, b) -> float`; `agreement.gate(a, b, threshold) -> str` (`"keep"`/`"adjudicate"`).
- `eval.span_prf1(gold, pred) -> dict`; `eval.per_act_f1(gold, pred) -> dict[str, dict]`.

---

## Task 0: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/atos/__init__.py`
- Modify: `.gitignore` (append)

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "atos"
version = "0.1.0"
description = "Span-level speech-act classification for PT-BR"
requires-python = ">=3.10"
dependencies = ["pyyaml>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create the package marker**

```python
# src/atos/__init__.py
"""atos — span-level speech-act classification for PT-BR."""
```

- [ ] **Step 3: Append to `.gitignore`**

```
# python
__pycache__/
*.pyc
.venv/
*.egg-info/
.pytest_cache/
# generated data
data/
```

- [ ] **Step 4: Create venv and install editable + pytest**

Run:
```bash
cd /Users/lucianfialho/Code/antiachismosocialclub/atos
python3 -m venv .venv
.venv/bin/pip install -q -e ".[dev]"
.venv/bin/pytest -q
```
Expected: pytest runs, collects 0 items, exits 0 (`no tests ran`).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/atos/__init__.py .gitignore
git commit -m "chore: scaffold atos package + pytest"
```

---

## Task 1: Annotation schema (`schema.py`)

**Files:**
- Create: `src/atos/schema.py`
- Test: `tests/test_schema.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_schema.py
from atos.schema import Span, Annotation


def test_span_is_frozen_and_holds_offsets():
    s = Span(start=0, end=8, act="saudar")
    assert (s.start, s.end, s.act) == (0, 8, "saudar")


def test_annotation_roundtrips_through_json():
    ann = Annotation(
        text="Bom dia! Pode enviar?",
        spans=[Span(0, 8, "saudar"), Span(9, 21, "pedir")],
    )
    restored = Annotation.from_json(ann.to_json())
    assert restored == ann


def test_from_json_parses_expected_shape():
    raw = '{"text": "Oi", "spans": [{"start": 0, "end": 2, "act": "saudar"}]}'
    ann = Annotation.from_json(raw)
    assert ann.text == "Oi"
    assert ann.spans == [Span(0, 2, "saudar")]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_schema.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.schema'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/schema.py
from dataclasses import dataclass
from typing import List
import json


@dataclass(frozen=True)
class Span:
    start: int  # char offset, inclusive
    end: int    # char offset, exclusive
    act: str    # speech-act label


@dataclass
class Annotation:
    text: str
    spans: List[Span]

    def to_json(self) -> str:
        return json.dumps(
            {
                "text": self.text,
                "spans": [
                    {"start": s.start, "end": s.end, "act": s.act}
                    for s in self.spans
                ],
            },
            ensure_ascii=False,
        )

    @staticmethod
    def from_json(s: str) -> "Annotation":
        obj = json.loads(s)
        return Annotation(
            text=obj["text"],
            spans=[Span(d["start"], d["end"], d["act"]) for d in obj["spans"]],
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_schema.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/schema.py tests/test_schema.py
git commit -m "feat: annotation schema (Span, Annotation, JSON roundtrip)"
```

---

## Task 2: Taxonomy + BIOES labels (`taxonomy.py`)

**Files:**
- Create: `src/atos/taxonomy.py`
- Create: `config/taxonomy.yaml`
- Test: `tests/test_taxonomy.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_taxonomy.py
from atos.taxonomy import load_taxonomy, bioes_labels, label_maps


def test_load_taxonomy_reads_acts_and_definitions(tmp_path):
    p = tmp_path / "tax.yaml"
    p.write_text(
        "acts:\n"
        "  - name: afirmar\n"
        "    definition: declarar algo como verdadeiro\n"
        "  - name: perguntar\n"
        "    definition: solicitar informacao\n",
        encoding="utf-8",
    )
    tax = load_taxonomy(str(p))
    assert tax.acts == ["afirmar", "perguntar"]
    assert tax.definitions["afirmar"] == "declarar algo como verdadeiro"


def test_bioes_labels_order_is_O_then_BIES_per_act():
    labels = bioes_labels(["afirmar", "perguntar"])
    assert labels == [
        "O",
        "B-afirmar", "I-afirmar", "E-afirmar", "S-afirmar",
        "B-perguntar", "I-perguntar", "E-perguntar", "S-perguntar",
    ]


def test_label_maps_are_inverse_and_contiguous():
    labels = bioes_labels(["afirmar"])
    label2id, id2label = label_maps(labels)
    assert label2id["O"] == 0
    assert id2label[0] == "O"
    assert sorted(label2id.values()) == list(range(len(labels)))
    assert all(id2label[label2id[l]] == l for l in labels)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_taxonomy.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.taxonomy'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/taxonomy.py
from dataclasses import dataclass
from typing import Dict, List, Tuple
import yaml


@dataclass
class Taxonomy:
    acts: List[str]
    definitions: Dict[str, str]


def load_taxonomy(path: str) -> Taxonomy:
    with open(path, "r", encoding="utf-8") as f:
        obj = yaml.safe_load(f)
    acts = [a["name"] for a in obj["acts"]]
    definitions = {a["name"]: a.get("definition", "") for a in obj["acts"]}
    return Taxonomy(acts=acts, definitions=definitions)


def bioes_labels(acts: List[str]) -> List[str]:
    labels = ["O"]
    for act in acts:
        labels += [f"B-{act}", f"I-{act}", f"E-{act}", f"S-{act}"]
    return labels


def label_maps(labels: List[str]) -> Tuple[Dict[str, int], Dict[int, str]]:
    label2id = {l: i for i, l in enumerate(labels)}
    id2label = {i: l for l, i in label2id.items()}
    return label2id, id2label
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_taxonomy.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Create the provisional taxonomy config**

```yaml
# config/taxonomy.yaml
# PROVISIONAL — to be frozen in Phase 1 from the ingested papers.
# Base: Searle's 5 macro-classes expanded with useful ISO 24617-2 acts.
acts:
  - name: afirmar
    definition: Declarar algo como verdadeiro (assertivo).
  - name: perguntar
    definition: Solicitar informacao (diretivo interrogativo).
  - name: pedir
    definition: Requisitar uma acao do interlocutor (diretivo).
  - name: sugerir
    definition: Propor uma acao sem obrigar (diretivo fraco).
  - name: prometer
    definition: Comprometer-se com uma acao futura (compromissivo).
  - name: agradecer
    definition: Expressar gratidao (expressivo).
  - name: concordar
    definition: Manifestar acordo com algo dito (expressivo/assertivo).
  - name: discordar
    definition: Manifestar desacordo com algo dito (expressivo/assertivo).
  - name: saudar
    definition: Iniciar contato social (expressivo).
  - name: despedir
    definition: Encerrar contato social (expressivo).
  - name: informar
    definition: Prover informacao nao solicitada (assertivo).
  - name: expressar_emocao
    definition: Manifestar estado emocional (expressivo).
```

- [ ] **Step 6: Add a test that the shipped config loads and yields 49 labels**

```python
# append to tests/test_taxonomy.py
def test_shipped_config_yields_49_bioes_labels():
    tax = load_taxonomy("config/taxonomy.yaml")
    assert len(tax.acts) == 12
    assert len(bioes_labels(tax.acts)) == 49  # 4 * 12 + 1
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_taxonomy.py -q`
Expected: PASS (4 passed)

- [ ] **Step 8: Commit**

```bash
git add src/atos/taxonomy.py tests/test_taxonomy.py config/taxonomy.yaml
git commit -m "feat: taxonomy loader + BIOES label scheme + provisional 12-act config"
```

---

## Task 3: Resolve quoted spans to offsets (`resolve.py`)

The teacher LLMs return spans as **quoted substrings** + an act, not char offsets. This module converts them to offset-based `Annotation`, enforcing the verbatim check (quote must appear in the text) and left-to-right ordering (each quote is located at or after the previous span's end, which disambiguates repeated substrings and guarantees ordered, non-overlapping spans when inputs are well-formed).

**Files:**
- Create: `src/atos/resolve.py`
- Test: `tests/test_resolve.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_resolve.py
from atos.resolve import resolve_quoted_spans
from atos.schema import Span


def test_resolves_quotes_to_offsets_in_order():
    text = "Bom dia! Pode enviar o relatorio?"
    items = [
        {"quote": "Bom dia!", "act": "saudar"},
        {"quote": "Pode enviar o relatorio?", "act": "pedir"},
    ]
    ann, errors = resolve_quoted_spans(text, items)
    assert errors == []
    assert ann.text == text
    assert ann.spans == [Span(0, 8, "saudar"), Span(9, 33, "pedir")]


def test_repeated_quote_is_located_left_to_right():
    text = "Sim. Sim."
    items = [
        {"quote": "Sim.", "act": "concordar"},
        {"quote": "Sim.", "act": "concordar"},
    ]
    ann, errors = resolve_quoted_spans(text, items)
    assert errors == []
    assert ann.spans == [Span(0, 4, "concordar"), Span(5, 9, "concordar")]


def test_missing_quote_reports_error():
    text = "Bom dia!"
    items = [{"quote": "Boa noite!", "act": "saudar"}]
    ann, errors = resolve_quoted_spans(text, items)
    assert len(errors) == 1
    assert "Boa noite!" in errors[0]
    assert ann.spans == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_resolve.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.resolve'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/resolve.py
from typing import Dict, List, Tuple
from atos.schema import Annotation, Span


def resolve_quoted_spans(
    text: str, items: List[Dict]
) -> Tuple[Annotation, List[str]]:
    spans: List[Span] = []
    errors: List[str] = []
    cursor = 0
    for item in items:
        quote = item["quote"]
        act = item["act"]
        idx = text.find(quote, cursor)
        if idx == -1:
            errors.append(f"quote not found at/after offset {cursor}: {quote!r}")
            continue
        start, end = idx, idx + len(quote)
        spans.append(Span(start, end, act))
        cursor = end
    return Annotation(text=text, spans=spans), errors
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_resolve.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/resolve.py tests/test_resolve.py
git commit -m "feat: resolve quoted spans to char offsets (verbatim + ordered)"
```

---

## Task 4: Annotation validator (`validator.py`)

**Files:**
- Create: `src/atos/validator.py`
- Test: `tests/test_validator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_validator.py
from atos.validator import validate
from atos.schema import Annotation, Span
from atos.taxonomy import Taxonomy

TAX = Taxonomy(acts=["saudar", "pedir"], definitions={"saudar": "", "pedir": ""})


def test_valid_annotation_has_no_errors():
    ann = Annotation("Oi! Pode vir?", [Span(0, 3, "saudar"), Span(4, 13, "pedir")])
    assert validate(ann, TAX) == []


def test_out_of_bounds_span_is_flagged():
    ann = Annotation("Oi", [Span(0, 5, "saudar")])
    errors = validate(ann, TAX)
    assert any("bounds" in e for e in errors)


def test_inverted_span_is_flagged():
    ann = Annotation("Oi tudo bem", [Span(5, 2, "saudar")])
    errors = validate(ann, TAX)
    assert any("bounds" in e for e in errors)


def test_illegal_act_is_flagged():
    ann = Annotation("Oi", [Span(0, 2, "xingar")])
    errors = validate(ann, TAX)
    assert any("illegal act" in e for e in errors)


def test_overlapping_spans_are_flagged():
    ann = Annotation("Oi tudo bem", [Span(0, 7, "saudar"), Span(3, 11, "pedir")])
    errors = validate(ann, TAX)
    assert any("overlap" in e for e in errors)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_validator.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.validator'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/validator.py
from typing import List
from atos.schema import Annotation
from atos.taxonomy import Taxonomy


def validate(ann: Annotation, taxonomy: Taxonomy) -> List[str]:
    errors: List[str] = []
    n = len(ann.text)
    legal = set(taxonomy.acts)

    for s in ann.spans:
        if not (0 <= s.start < s.end <= n):
            errors.append(
                f"span out of bounds: ({s.start}, {s.end}) for text length {n}"
            )
        if s.act not in legal:
            errors.append(f"illegal act: {s.act!r}")

    ordered = sorted(ann.spans, key=lambda s: (s.start, s.end))
    for prev, cur in zip(ordered, ordered[1:]):
        if cur.start < prev.end:
            errors.append(
                f"overlap between ({prev.start},{prev.end}) and ({cur.start},{cur.end})"
            )

    return errors
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_validator.py -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/validator.py tests/test_validator.py
git commit -m "feat: annotation validator (bounds, legal act, non-overlap)"
```

---

## Task 5: BIOES tagging from token offsets (`bioes.py`)

Pure function: given char-offset spans and the per-token char offsets (from a tokenizer's `return_offsets_mapping=True`), emit one BIOES tag per token. A token belongs to a span when its char range is fully contained in the span. Special tokens carry offset `(0, 0)` and map to `O`.

**Files:**
- Create: `src/atos/bioes.py`
- Test: `tests/test_bioes.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_bioes.py
from atos.bioes import char_spans_to_bioes
from atos.schema import Span


def test_single_token_span_gets_S():
    # text "Oi!" -> tokens "Oi" (0,2), "!" (2,3); span covers "Oi" only
    offsets = [(0, 2), (2, 3)]
    spans = [Span(0, 2, "saudar")]
    assert char_spans_to_bioes(spans, offsets) == ["S-saudar", "O"]


def test_multi_token_span_gets_B_I_E():
    # 3 tokens all inside one span
    offsets = [(0, 4), (5, 9), (10, 14)]
    spans = [Span(0, 14, "pedir")]
    assert char_spans_to_bioes(spans, offsets) == ["B-pedir", "I-pedir", "E-pedir"]


def test_two_token_span_gets_B_E_without_I():
    offsets = [(0, 3), (4, 8)]
    spans = [Span(0, 8, "informar")]
    assert char_spans_to_bioes(spans, offsets) == ["B-informar", "E-informar"]


def test_special_tokens_and_gaps_are_O():
    # offset (0,0) = special token; a token outside any span = O
    offsets = [(0, 0), (0, 2), (3, 7), (0, 0)]
    spans = [Span(0, 2, "saudar")]
    assert char_spans_to_bioes(spans, offsets) == ["O", "S-saudar", "O", "O"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_bioes.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.bioes'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/bioes.py
from typing import List, Tuple
from atos.schema import Span


def _token_in_span(tok: Tuple[int, int], span: Span) -> bool:
    start, end = tok
    if start == end:  # special token / empty offset
        return False
    return start >= span.start and end <= span.end


def char_spans_to_bioes(
    spans: List[Span], offsets: List[Tuple[int, int]]
) -> List[str]:
    # token index -> span index (or -1)
    owner = [-1] * len(offsets)
    for si, span in enumerate(spans):
        member = [ti for ti, tok in enumerate(offsets) if _token_in_span(tok, span)]
        for ti in member:
            owner[ti] = si

    tags = ["O"] * len(offsets)
    for si, span in enumerate(spans):
        member = [ti for ti in range(len(offsets)) if owner[ti] == si]
        if not member:
            continue
        if len(member) == 1:
            tags[member[0]] = f"S-{span.act}"
        else:
            tags[member[0]] = f"B-{span.act}"
            tags[member[-1]] = f"E-{span.act}"
            for ti in member[1:-1]:
                tags[ti] = f"I-{span.act}"
    return tags
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_bioes.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/bioes.py tests/test_bioes.py
git commit -m "feat: BIOES tagging from char spans + token offsets"
```

---

## Task 6: Double-annotation agreement gate (`agreement.py`)

Quality gate for the teacher mixture: compare two annotations of the same text (e.g. MiniMax vs Claude) by exact span+act match, return an F1-style agreement score, and decide `keep` (high agreement) vs `adjudicate` (route to Claude).

**Files:**
- Create: `src/atos/agreement.py`
- Test: `tests/test_agreement.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_agreement.py
from atos.agreement import span_agreement, gate
from atos.schema import Annotation, Span


def _ann(spans):
    return Annotation("Bom dia! Pode vir?", spans)


def test_identical_annotations_agree_fully():
    a = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    b = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    assert span_agreement(a, b) == 1.0


def test_disjoint_annotations_agree_zero():
    a = _ann([Span(0, 8, "saudar")])
    b = _ann([Span(9, 18, "pedir")])
    assert span_agreement(a, b) == 0.0


def test_partial_overlap_is_f1():
    # a has 2 spans, b has 2 spans, 1 shared -> P=0.5, R=0.5, F1=0.5
    a = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    b = _ann([Span(0, 8, "saudar"), Span(9, 18, "sugerir")])
    assert span_agreement(a, b) == 0.5


def test_gate_keeps_above_threshold_and_adjudicates_below():
    a = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    b = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    assert gate(a, b, threshold=0.8) == "keep"
    c = _ann([Span(0, 8, "saudar")])
    d = _ann([Span(9, 18, "pedir")])
    assert gate(c, d, threshold=0.8) == "adjudicate"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_agreement.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.agreement'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/agreement.py
from typing import Set, Tuple
from atos.schema import Annotation


def _span_set(ann: Annotation) -> Set[Tuple[int, int, str]]:
    return {(s.start, s.end, s.act) for s in ann.spans}


def span_agreement(a: Annotation, b: Annotation) -> float:
    sa, sb = _span_set(a), _span_set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    tp = len(sa & sb)
    if tp == 0:
        return 0.0
    precision = tp / len(sb)
    recall = tp / len(sa)
    return 2 * precision * recall / (precision + recall)


def gate(a: Annotation, b: Annotation, threshold: float) -> str:
    return "keep" if span_agreement(a, b) >= threshold else "adjudicate"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_agreement.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/agreement.py tests/test_agreement.py
git commit -m "feat: double-annotation agreement gate (span F1 + keep/adjudicate)"
```

---

## Task 7: Span-level evaluator (`eval.py`)

The metric the spec requires (Phase 4): **span-level** precision/recall/F1 (exact start+end+act match) over a dataset of gold vs predicted annotations, plus a per-act F1 breakdown to spot confusable acts.

**Files:**
- Create: `src/atos/eval.py`
- Test: `tests/test_eval.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_eval.py
from atos.eval import span_prf1, per_act_f1
from atos.schema import Annotation, Span


def test_perfect_prediction_scores_one():
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    m = span_prf1(gold, pred)
    assert m == {"precision": 1.0, "recall": 1.0, "f1": 1.0}


def test_half_correct_prediction():
    # gold 2 spans, pred 2 spans, 1 exact match -> P=0.5 R=0.5 F1=0.5
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "sugerir")])]
    m = span_prf1(gold, pred)
    assert m == {"precision": 0.5, "recall": 0.5, "f1": 0.5}


def test_per_act_f1_reports_each_gold_act():
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "sugerir")])]
    by_act = per_act_f1(gold, pred)
    assert by_act["saudar"]["f1"] == 1.0
    assert by_act["pedir"]["f1"] == 0.0  # missed (predicted as sugerir)


def test_empty_dataset_scores_zero():
    assert span_prf1([], []) == {"precision": 0.0, "recall": 0.0, "f1": 0.0}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_eval.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.eval'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/eval.py
from typing import Dict, List, Set, Tuple
from atos.schema import Annotation

Key = Tuple[int, int, int, str]  # (doc_index, start, end, act)


def _keys(anns: List[Annotation]) -> Set[Key]:
    out: Set[Key] = set()
    for i, ann in enumerate(anns):
        for s in ann.spans:
            out.add((i, s.start, s.end, s.act))
    return out


def _prf1(tp: int, n_pred: int, n_gold: int) -> Dict[str, float]:
    precision = tp / n_pred if n_pred else 0.0
    recall = tp / n_gold if n_gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def span_prf1(gold: List[Annotation], pred: List[Annotation]) -> Dict[str, float]:
    g, p = _keys(gold), _keys(pred)
    return _prf1(len(g & p), len(p), len(g))


def per_act_f1(
    gold: List[Annotation], pred: List[Annotation]
) -> Dict[str, Dict[str, float]]:
    g, p = _keys(gold), _keys(pred)
    acts = {k[3] for k in g} | {k[3] for k in p}
    result: Dict[str, Dict[str, float]] = {}
    for act in acts:
        ga = {k for k in g if k[3] == act}
        pa = {k for k in p if k[3] == act}
        result[act] = _prf1(len(ga & pa), len(pa), len(ga))
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_eval.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Run the full suite**

Run: `.venv/bin/pytest -q`
Expected: PASS (all tests across the 7 modules; ~27 passed)

- [ ] **Step 6: Commit**

```bash
git add src/atos/eval.py tests/test_eval.py
git commit -m "feat: span-level PRF1 evaluator + per-act breakdown"
```

---

## Task 8: Wiki bookkeeping

Per `SCHEMA.md`, record this build in the wiki so the knowledge compounds.

**Files:**
- Create: `wiki/concepts/speech-act-label-scheme.md`
- Modify: `log.md` (append one entry)
- Modify: `index.md` (add the new concept under Fine-tuning & Task Adaptation)

- [ ] **Step 1: Create the label-scheme concept page**

```markdown
---
type: concept
tags: [speech-acts, bioes, labels, annotation, atos-project]
sources: 0
updated: 2026-06-04
---

# Speech Act Label Scheme (PT-BR)

## Definition

The BIOES label set for span-level speech-act classification. Derived mechanically from
`config/taxonomy.yaml`: for N acts, labels = `O` plus `{B,I,E,S}×acts` = `4N+1` classes.
Provisional taxonomy (12 acts → 49 labels), to be frozen in Phase 1 from the papers.

## How It Works

`atos.taxonomy.bioes_labels(acts)` emits `O` first, then `B-/I-/E-/S-` per act in config
order. `label_maps` gives contiguous `label2id`/`id2label`. Non-overlapping spans only (v1).

## Provisional acts

afirmar, perguntar, pedir, sugerir, prometer, agradecer, concordar, discordar, saudar,
despedir, informar, expressar_emocao.

## Why It Matters

Same architectural shape as the Privacy Filter BR head (PII → speech acts). Swapping the
taxonomy is a config change, not a code change.

## Related Concepts

- [BIOES Tagging](bioes-tagging.md)
- [Token Classification](token-classification.md)
- [LoRA Fine-tuning Pitfalls](lora-fine-tuning-pitfalls.md)

## Sources

- Design spec: `docs/superpowers/specs/2026-06-04-speech-act-span-classifier-design.md`
```

- [ ] **Step 2: Append to `log.md`**

```markdown
## [2026-06-04] build | Annotation Core (Plan 1)
Implementado o núcleo de anotação do classificador de atos de fala: schema (Span/Annotation), taxonomy + BIOES labels (config-driven), resolve de quotes→offsets, validator, BIOES tagger, agreement gate e span-F1 evaluator. ~27 testes, lógica pura sem APIs/GPU. Taxonomia provisória de 12 atos (49 labels) em config/taxonomy.yaml, a congelar na Fase 1.
```

- [ ] **Step 3: Add the concept to `index.md`** under "### Fine-tuning & Task Adaptation"

```markdown
- [Speech Act Label Scheme](wiki/concepts/speech-act-label-scheme.md) — BIOES label set (O ∪ {B,I,E,S}×atos) derivado de config/taxonomy.yaml; 12 atos provisórios → 49 labels
```

- [ ] **Step 4: Commit**

```bash
git add wiki/concepts/speech-act-label-scheme.md log.md index.md
git commit -m "docs(wiki): record annotation core build + label scheme concept"
```

---

## Self-Review

**1. Spec coverage (Plan 1 portion):**
- BIOES label scheme `O ∪ {B,I,E,S}×atos`, ~49 classes → Task 2. ✓
- Non-overlapping spans (v1) → enforced in `validator` (Task 4) and `resolve` ordering (Task 3). ✓
- Validator: span verbatim + label legality → `resolve` verbatim (Task 3) + `validator` legality/bounds (Task 4). ✓
- Agreement gate (teacher mixture) → Task 6. ✓
- BIOES auto-labeler → Task 5. ✓
- Span-level F1 + per-act breakdown (Phase 4 metric) → Task 7. ✓
- Config-driven taxonomy (swap when frozen) → Task 2 config + loader. ✓
- Wiki integration per SCHEMA.md → Task 8. ✓
- **Deferred to Plan 2:** MiniMax generator, Claude adjudicator, orchestration CLI, resume-from-disk.
- **Deferred to Plan 3:** BERTimbau + LoRA training, HF-tokenizer offset wrapper, Viterbi post-proc, real-text holdout eval CLI.

**2. Placeholder scan:** No "TBD"/"TODO"/"handle edge cases"/vague steps. Every code step shows full code; every run step shows exact command + expected output. ✓

**3. Type consistency:** `Span(start,end,act)` and `Annotation(text,spans)` used identically across Tasks 1,3,4,5,6,7. `Taxonomy(acts,definitions)` consistent in Tasks 2,4. `bioes_labels`/`label_maps` signatures match between Task 2 def and its tests. `char_spans_to_bioes(spans, offsets)` consistent (Task 5). `span_agreement`/`gate` consistent (Task 6). `span_prf1`/`per_act_f1` consistent (Task 7). ✓

---

## Done criteria

`.venv/bin/pytest -q` is green (all modules), `config/taxonomy.yaml` loads to 49 labels, and the wiki records the build. Plan 2 (generation pipeline) can then be written and executed against this library.
