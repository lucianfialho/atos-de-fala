# Coleta Colaborativa — Plano 1: Pipeline Python (`chomsky.collect`) + Schema

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o pipeline offline que prepara lotes pra anotar e ingere/agrega os votos coletados em gold + paráfrases + análise de percepção, mais o schema Postgres que é o contrato com o web app.

**Architecture:** Lógica pura (seleção, agregação ponderada, pontuação, percepção, confirmação de paráfrase) em funções testáveis sem banco, no estilo do `agreement.py`/`eval.py` existentes. Um adaptador fino `db.py` (psycopg) faz o I/O e é testado por integração (pulado sem `$TEST_DATABASE_URL`). O schema vive em `db/schema.sql`, aplicado pelo web app e lido pelo Python.

**Tech Stack:** Python 3.10, pytest, psycopg 3, Postgres (Neon), reuso de `chomsky.schema`/`chomsky.agreement`/`chomsky.gen` (DeepSeek adjudicador).

---

## File Structure

- `db/schema.sql` — **contrato compartilhado**: tabelas participant, item, item_span, span_gold, vote, suggestion, participant_stats.
- `src/chomsky/collect/__init__.py` — pacote.
- `src/chomsky/collect/models.py` — dataclasses de interchange (`Vote`, `SpanResolution`).
- `src/chomsky/collect/select.py` — puro: `build_items()` (Annotation → linhas item/span; marca honeypot+gold).
- `src/chomsky/collect/score.py` — puro: `streak_multiplier`, `points_for_vote`, `update_reliability`, constantes de pontos.
- `src/chomsky/collect/aggregate.py` — puro: `resolve_span()` (voto majoritário ponderado por confiabilidade → ato + concordância + is_gold).
- `src/chomsky/collect/perception.py` — puro: `act_distribution_by_group()`, `groups_disagree()`.
- `src/chomsky/collect/confirm.py` — orquestra confirmação de paráfrase via DeepSeek (`build_paraphrase_check_prompt`, `confirm_suggestion`).
- `src/chomsky/collect/db.py` — adaptador psycopg fino (I/O).
- `src/chomsky/collect/cli.py` — subcomandos export/ingest/aggregate/confirm/perception.
- `tests/test_collect_*.py` — testes unitários puros.
- `tests/integration/test_collect_db.py` — integração (skip sem `$TEST_DATABASE_URL`).

Cada arquivo fica bem abaixo do gate de 150 linhas. Rode os testes com `.venv/bin/python -m pytest` (o python do sistema não tem o pacote `chomsky`).

---

### Task 1: Schema Postgres (contrato compartilhado)

**Files:**
- Create: `db/schema.sql`
- Test: `tests/integration/test_collect_db.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/integration/test_collect_db.py
import os
import pytest

DSN = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DSN, reason="set TEST_DATABASE_URL to run DB integration tests")


def _apply_schema(conn):
    with open("db/schema.sql", encoding="utf-8") as f:
        conn.execute(f.read())
    conn.commit()


def test_schema_creates_expected_tables():
    import psycopg
    with psycopg.connect(DSN) as conn:
        _apply_schema(conn)
        rows = conn.execute(
            "select table_name from information_schema.tables where table_schema='public'"
        ).fetchall()
    names = {r[0] for r in rows}
    assert {"participant", "item", "item_span", "span_gold", "vote",
            "suggestion", "participant_stats"} <= names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/integration/test_collect_db.py -v`
Expected: SKIPPED (no `TEST_DATABASE_URL`) — that is the expected state in CI. To actually exercise it, set `TEST_DATABASE_URL` to a throwaway Postgres and it must FAIL with "No such file or directory: 'db/schema.sql'".

- [ ] **Step 3: Write the schema**

```sql
-- db/schema.sql — contrato compartilhado (web app aplica via migration; Python lê/escreve).
create table if not exists participant (
  id           uuid primary key,
  age_band     text not null,
  gender       text not null,
  region       text not null,          -- UF
  education    text not null,
  created_at   timestamptz not null default now()
);

create table if not exists item (
  id           bigserial primary key,
  text         text not null,
  source       text not null default 'synthetic',   -- 'synthetic' | 'news'
  is_honeypot  boolean not null default false,
  created_at   timestamptz not null default now()
);

create table if not exists item_span (
  id            bigserial primary key,
  item_id       bigint not null references item(id) on delete cascade,
  char_start    int not null,
  char_end      int not null,
  ai_act        text not null,
  display_order int not null
);

create table if not exists span_gold (
  item_span_id  bigint primary key references item_span(id) on delete cascade,
  gold_act      text not null
);

create table if not exists vote (
  id             bigserial primary key,
  participant_id uuid not null references participant(id) on delete cascade,
  item_span_id   bigint not null references item_span(id) on delete cascade,
  verdict        text not null,         -- 'agree' | 'disagree'
  corrected_act  text,
  created_at     timestamptz not null default now(),
  unique (participant_id, item_span_id)
);

create table if not exists suggestion (
  id             bigserial primary key,
  participant_id uuid not null references participant(id) on delete cascade,
  item_span_id   bigint not null references item_span(id) on delete cascade,
  text           text not null,
  status         text not null default 'pending',   -- 'pending'|'confirmed'|'rejected'
  created_at     timestamptz not null default now()
);

create table if not exists participant_stats (
  participant_id uuid primary key references participant(id) on delete cascade,
  points         int not null default 0,
  streak         int not null default 0,
  reliability    double precision not null default 0.5,
  items_done     int not null default 0
);

create index if not exists idx_vote_span on vote(item_span_id);
create index if not exists idx_span_item on item_span(item_id);
create index if not exists idx_suggestion_status on suggestion(status);
```

- [ ] **Step 4: Run test to verify it passes (or skips)**

Run: `.venv/bin/python -m pytest tests/integration/test_collect_db.py -v`
Expected: SKIPPED without `TEST_DATABASE_URL`; PASS when set against a fresh Postgres.

- [ ] **Step 5: Commit**

```bash
git add db/schema.sql tests/integration/test_collect_db.py
git commit -m "feat(collect): shared Postgres schema (collection contract)"
```

---

### Task 2: Pacote + modelos de interchange

**Files:**
- Create: `src/chomsky/collect/__init__.py`, `src/chomsky/collect/models.py`
- Test: `tests/test_collect_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_collect_models.py
from chomsky.collect.models import Vote, SpanResolution


def test_vote_is_frozen_and_holds_fields():
    v = Vote(span_id=1, verdict="disagree", corrected_act="sugerir", reliability=0.8)
    assert v.span_id == 1 and v.corrected_act == "sugerir" and v.reliability == 0.8


def test_span_resolution_holds_fields():
    r = SpanResolution(span_id=1, act="pedir", agreement=0.75, is_gold=True)
    assert r.act == "pedir" and r.is_gold is True and r.agreement == 0.75
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_collect_models.py -v`
Expected: FAIL with "No module named 'chomsky.collect'".

- [ ] **Step 3: Write the package and models**

```python
# src/chomsky/collect/__init__.py
```

```python
# src/chomsky/collect/models.py
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Vote:
    span_id: int
    verdict: str                  # "agree" | "disagree"
    corrected_act: Optional[str]  # the act the voter prefers when disagreeing
    reliability: float            # voter weight, 0..1 (from honeypots)


@dataclass(frozen=True)
class SpanResolution:
    span_id: int
    act: Optional[str]            # winning act; None if no act reached consensus
    agreement: float              # weighted share of the winning act, 0..1
    is_gold: bool                 # agreement >= threshold
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_collect_models.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/chomsky/collect/__init__.py src/chomsky/collect/models.py tests/test_collect_models.py
git commit -m "feat(collect): interchange dataclasses (Vote, SpanResolution)"
```

---

### Task 3: Construção de lote (`select.build_items`)

**Files:**
- Create: `src/chomsky/collect/select.py`
- Test: `tests/test_collect_select.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_collect_select.py
from chomsky.collect.select import build_items
from chomsky.schema import Annotation, Span


def test_build_items_maps_annotation_to_item_with_spans():
    anns = [Annotation("Oi! Vai?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    rows = build_items(anns, [])
    assert len(rows) == 1
    row = rows[0]
    assert row["text"] == "Oi! Vai?" and row["is_honeypot"] is False and row["source"] == "synthetic"
    assert row["spans"][0] == {"char_start": 0, "char_end": 3, "ai_act": "saudar", "display_order": 0}
    assert "gold_act" not in row["spans"][0]


def test_build_items_marks_honeypot_spans_with_gold_act():
    hp = [Annotation("Bom dia!", [Span(0, 8, "saudar")])]
    rows = build_items([], hp)
    assert rows[0]["is_honeypot"] is True
    assert rows[0]["spans"][0]["gold_act"] == "saudar"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_collect_select.py -v`
Expected: FAIL with "No module named 'chomsky.collect.select'".

- [ ] **Step 3: Write the implementation**

```python
# src/chomsky/collect/select.py
"""Turn AI-annotated texts (and honeypot gold) into item rows for the collection DB.

A normal item carries the model's spans/acts for players to judge. A honeypot item is a
high-agreement gold annotation whose span.act IS the known answer used to score voter
reliability — so each honeypot span also emits `gold_act`. Pure transform: no DB here."""
from typing import Dict, List
from chomsky.schema import Annotation


def _item_row(ann: Annotation, is_honeypot: bool) -> Dict:
    spans: List[Dict] = []
    for order, s in enumerate(ann.spans):
        span = {"char_start": s.start, "char_end": s.end, "ai_act": s.act, "display_order": order}
        if is_honeypot:
            span["gold_act"] = s.act
        spans.append(span)
    return {"text": ann.text, "source": "synthetic", "is_honeypot": is_honeypot, "spans": spans}


def build_items(annotations: List[Annotation], honeypots: List[Annotation]) -> List[Dict]:
    """`annotations`: model output to be judged. `honeypots`: gold whose acts are known."""
    return [_item_row(a, False) for a in annotations] + [_item_row(h, True) for h in honeypots]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_collect_select.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/chomsky/collect/select.py tests/test_collect_select.py
git commit -m "feat(collect): build_items (annotations + honeypots -> item rows)"
```

---

### Task 4: Pontuação (`score`)

**Files:**
- Create: `src/chomsky/collect/score.py`
- Test: `tests/test_collect_score.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_collect_score.py
from chomsky.collect.score import (
    streak_multiplier, points_for_vote, update_reliability,
    POINTS_SUGGESTION, POINTS_SUGGESTION_CONFIRMED,
)


def test_streak_multiplier_tiers():
    assert streak_multiplier(0) == 1.0
    assert streak_multiplier(4) == 1.0
    assert streak_multiplier(5) == 1.5
    assert streak_multiplier(9) == 1.5
    assert streak_multiplier(10) == 2.0


def test_points_for_vote_applies_multiplier():
    assert points_for_vote(0) == 10
    assert points_for_vote(5) == 15
    assert points_for_vote(10) == 20


def test_suggestion_point_constants():
    assert POINTS_SUGGESTION == 20 and POINTS_SUGGESTION_CONFIRMED == 50


def test_update_reliability_rises_on_correct_and_falls_on_wrong():
    assert update_reliability(0.5, True) == 0.55       # 0.5 + 0.1*0.5
    assert update_reliability(0.5, False) == 0.4       # 0.5 * 0.8


def test_update_reliability_is_clamped():
    assert update_reliability(1.0, True) == 1.0
    assert update_reliability(0.0, False) == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_collect_score.py -v`
Expected: FAIL with "No module named 'chomsky.collect.score'".

- [ ] **Step 3: Write the implementation**

```python
# src/chomsky/collect/score.py
"""Scoring + reliability. Suggestions are an OPTIONAL bonus and never penalize. The only
downward pressure is the honeypot: getting a known-answer item wrong lowers reliability,
which is the WEIGHT a voter's votes get in aggregation (see aggregate.resolve_span)."""

POINTS_VOTE_BASE = 10
POINTS_SUGGESTION = 20            # provisional, on submit
POINTS_SUGGESTION_CONFIRMED = 50  # retroactive, when the adjudicator confirms it


def streak_multiplier(streak: int) -> float:
    if streak < 5:
        return 1.0
    if streak < 10:
        return 1.5
    return 2.0


def points_for_vote(streak: int, base: int = POINTS_VOTE_BASE) -> int:
    return round(base * streak_multiplier(streak))


def update_reliability(reliability: float, honeypot_correct: bool) -> float:
    """EMA toward 1.0 on a correct honeypot; multiplicative decay on a wrong one. Clamped."""
    r = reliability + 0.1 * (1.0 - reliability) if honeypot_correct else reliability * 0.8
    return max(0.0, min(1.0, r))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_collect_score.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add src/chomsky/collect/score.py tests/test_collect_score.py
git commit -m "feat(collect): scoring + honeypot-driven reliability"
```

---

### Task 5: Agregação ponderada (`aggregate.resolve_span`)

**Files:**
- Create: `src/chomsky/collect/aggregate.py`
- Test: `tests/test_collect_aggregate.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_collect_aggregate.py
from chomsky.collect.aggregate import resolve_span
from chomsky.collect.models import Vote


def test_unanimous_agree_resolves_to_ai_act_as_gold():
    votes = [Vote(1, "agree", None, 1.0), Vote(1, "agree", None, 1.0)]
    r = resolve_span("pedir", votes, threshold=0.66)
    assert r.act == "pedir" and r.agreement == 1.0 and r.is_gold is True


def test_weighted_correction_can_overturn_ai_act():
    # one low-trust agree vs two high-trust corrections -> corrected act wins
    votes = [Vote(1, "agree", None, 0.2),
             Vote(1, "disagree", "sugerir", 0.9),
             Vote(1, "disagree", "sugerir", 0.9)]
    r = resolve_span("pedir", votes)
    assert r.act == "sugerir"
    assert round(r.agreement, 3) == round(1.8 / 2.0, 3)  # 0.9
    assert r.is_gold is True


def test_disagree_without_correction_lowers_agreement_below_gold():
    votes = [Vote(1, "agree", None, 1.0), Vote(1, "disagree", None, 1.0)]
    r = resolve_span("pedir", votes, threshold=0.66)
    assert r.act == "pedir" and r.agreement == 0.5 and r.is_gold is False


def test_no_votes_returns_empty_resolution():
    r = resolve_span("pedir", [])
    assert r.act is None and r.is_gold is False and r.agreement == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_collect_aggregate.py -v`
Expected: FAIL with "No module named 'chomsky.collect.aggregate'".

- [ ] **Step 3: Write the implementation**

```python
# src/chomsky/collect/aggregate.py
"""Weighted majority over the act each vote endorses, weighting by voter reliability.

agree -> endorses the AI's act. disagree+corrected -> endorses the corrected act.
disagree without a correction -> endorses NO act (adds to the total weight, so it lowers
the winning act's share). A span becomes gold when the winning act's weighted share
reaches `threshold`."""
from typing import Dict, List
from chomsky.collect.models import Vote, SpanResolution


def resolve_span(ai_act: str, votes: List[Vote], threshold: float = 0.66) -> SpanResolution:
    if not votes:
        return SpanResolution(span_id=-1, act=None, agreement=0.0, is_gold=False)
    span_id = votes[0].span_id
    tally: Dict[str, float] = {}
    total = 0.0
    for v in votes:
        total += v.reliability
        act = ai_act if v.verdict == "agree" else v.corrected_act
        if act is not None:
            tally[act] = tally.get(act, 0.0) + v.reliability
    if not tally:
        return SpanResolution(span_id=span_id, act=None, agreement=0.0, is_gold=False)
    act, weight = max(tally.items(), key=lambda kv: kv[1])
    agreement = weight / total if total else 0.0
    return SpanResolution(span_id=span_id, act=act, agreement=agreement, is_gold=agreement >= threshold)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_collect_aggregate.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/chomsky/collect/aggregate.py tests/test_collect_aggregate.py
git commit -m "feat(collect): reliability-weighted span resolution + gold gate"
```

---

### Task 6: Análise de percepção (`perception`)

**Files:**
- Create: `src/chomsky/collect/perception.py`
- Test: `tests/test_collect_perception.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_collect_perception.py
from chomsky.collect.perception import act_distribution_by_group, groups_disagree


def test_distribution_counts_acts_per_group():
    records = [
        {"act": "pedir", "region": "SP"},
        {"act": "pedir", "region": "SP"},
        {"act": "sugerir", "region": "BA"},
    ]
    dist = act_distribution_by_group(records, "region")
    assert dist == {"SP": {"pedir": 2}, "BA": {"sugerir": 1}}


def test_groups_disagree_true_when_modal_act_differs():
    dist = {"SP": {"pedir": 5, "sugerir": 1}, "BA": {"sugerir": 4, "pedir": 1}}
    assert groups_disagree(dist) is True


def test_groups_disagree_false_when_modal_act_matches():
    dist = {"SP": {"pedir": 5}, "BA": {"pedir": 3, "sugerir": 1}}
    assert groups_disagree(dist) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_collect_perception.py -v`
Expected: FAIL with "No module named 'chomsky.collect.perception'".

- [ ] **Step 3: Write the implementation**

```python
# src/chomsky/collect/perception.py
"""The research output: do different demographic groups perceive different acts on the
SAME contested span? `records` are per-vote chosen acts tagged with a demographic axis
value (built from votes + participant rows). Pure functions over plain dicts."""
from typing import Dict, List


def act_distribution_by_group(records: List[Dict], axis: str) -> Dict[str, Dict[str, int]]:
    """records: [{'act': str, <axis>: group_value}]. Returns group -> {act: count}."""
    out: Dict[str, Dict[str, int]] = {}
    for r in records:
        group, act = r[axis], r["act"]
        bucket = out.setdefault(group, {})
        bucket[act] = bucket.get(act, 0) + 1
    return out


def groups_disagree(dist: Dict[str, Dict[str, int]]) -> bool:
    """True if the most-voted act differs across groups — a perception split worth a look."""
    modes = set()
    for counts in dist.values():
        if counts:
            modes.add(max(counts.items(), key=lambda kv: kv[1])[0])
    return len(modes) > 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_collect_perception.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/chomsky/collect/perception.py tests/test_collect_perception.py
git commit -m "feat(collect): perception analysis (act distribution by demographic)"
```

---

### Task 7: Confirmação de paráfrase via DeepSeek (`confirm`)

**Files:**
- Create: `src/chomsky/collect/confirm.py`
- Test: `tests/test_collect_confirm.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_collect_confirm.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_collect_confirm.py -v`
Expected: FAIL with "No module named 'chomsky.collect.confirm'".

- [ ] **Step 3: Write the implementation**

```python
# src/chomsky/collect/confirm.py
"""Confirm that a player's paraphrase preserves the span's speech act, using the same LLM
adjudicator family as generation. `client` is any object with .complete(messages)->str
(e.g. chomsky.gen.deepseek.DeepSeekClient), so tests inject a fake."""
from typing import Callable, Dict, List
from chomsky.gen.prompts import parse_llm_json


def build_paraphrase_check_prompt(act: str, original: str, paraphrase: str) -> List[Dict]:
    system = (
        "Você verifica se uma reescrita preserva o ATO DE FALA de um trecho em PT-BR. "
        'Responda SÓ com JSON: {"preserves": true|false}.'
    )
    user = (
        f"Ato: {act}\nOriginal: {original}\nReescrita: {paraphrase}\n"
        "A reescrita realiza o MESMO ato de fala que o original? Responda o JSON."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def confirm_suggestion(
    client, act: str, original: str, paraphrase: str,
    parse: Callable[[str], Dict] = parse_llm_json,
) -> bool:
    raw = client.complete(build_paraphrase_check_prompt(act, original, paraphrase))
    return bool(parse(raw).get("preserves", False))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_collect_confirm.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/chomsky/collect/confirm.py tests/test_collect_confirm.py
git commit -m "feat(collect): paraphrase confirmation via DeepSeek adjudicator"
```

---

### Task 8: Adaptador de banco (`db`) + dependência psycopg

**Files:**
- Create: `src/chomsky/collect/db.py`
- Modify: `pyproject.toml` (add `psycopg[binary]>=3.1,<4` to dependencies)
- Test: `tests/integration/test_collect_db.py` (extend from Task 1)

- [ ] **Step 1: Add the dependency**

In `pyproject.toml`, under `[project] dependencies` (the list that already holds `requests`, `pyyaml`, etc.), add the line:

```toml
    "psycopg[binary]>=3.1,<4",
```

Then install into the venv:

Run: `.venv/bin/python -m pip install "psycopg[binary]>=3.1,<4"`
Expected: "Successfully installed psycopg...".

- [ ] **Step 2: Write the failing integration test (append to the Task 1 file)**

```python
# append to tests/integration/test_collect_db.py
def test_insert_items_and_fetch_votes_roundtrip():
    import uuid
    import psycopg
    from chomsky.collect.db import insert_items, fetch_votes_by_span
    from chomsky.collect.select import build_items
    from chomsky.schema import Annotation, Span

    with psycopg.connect(DSN) as conn:
        _apply_schema(conn)
        conn.execute("truncate participant, item, item_span, span_gold, vote, suggestion, "
                     "participant_stats restart identity cascade")
        rows = build_items([Annotation("Oi! Vai?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])], [])
        span_ids = insert_items(conn, rows)            # returns flat list of created span ids
        pid = uuid.uuid4()
        conn.execute("insert into participant (id, age_band, gender, region, education) "
                     "values (%s,'25-34','m','SP','superior')", (pid,))
        conn.execute("insert into vote (participant_id, item_span_id, verdict, corrected_act) "
                     "values (%s,%s,'agree',null)", (pid, span_ids[1]))
        conn.commit()
        by_span = fetch_votes_by_span(conn)

    assert span_ids[1] in by_span
    ai_act, votes = by_span[span_ids[1]]
    assert ai_act == "pedir" and votes[0].verdict == "agree"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/integration/test_collect_db.py -v`
Expected: SKIPPED without `TEST_DATABASE_URL`; with it set, FAIL with "No module named 'chomsky.collect.db'".

- [ ] **Step 4: Write the implementation**

```python
# src/chomsky/collect/db.py
"""Thin psycopg adapter — the only module that touches Postgres. Keep SQL here so the
logic modules stay pure and unit-testable. Connection comes from DATABASE_URL."""
import os
from typing import Dict, List, Optional, Tuple
import psycopg
from chomsky.collect.models import Vote


def connect(dsn: Optional[str] = None):
    return psycopg.connect(dsn or os.environ["DATABASE_URL"])


def insert_items(conn, rows: List[Dict]) -> List[int]:
    """Insert item + item_span (+ span_gold for honeypots). Returns created span ids in order."""
    span_ids: List[int] = []
    for row in rows:
        item_id = conn.execute(
            "insert into item (text, source, is_honeypot) values (%s,%s,%s) returning id",
            (row["text"], row["source"], row["is_honeypot"]),
        ).fetchone()[0]
        for sp in row["spans"]:
            sid = conn.execute(
                "insert into item_span (item_id, char_start, char_end, ai_act, display_order) "
                "values (%s,%s,%s,%s,%s) returning id",
                (item_id, sp["char_start"], sp["char_end"], sp["ai_act"], sp["display_order"]),
            ).fetchone()[0]
            if "gold_act" in sp:
                conn.execute("insert into span_gold (item_span_id, gold_act) values (%s,%s)",
                             (sid, sp["gold_act"]))
            span_ids.append(sid)
    conn.commit()
    return span_ids


def fetch_votes_by_span(conn) -> Dict[int, Tuple[str, List[Vote]]]:
    """span_id -> (ai_act, [Vote]). Vote.reliability comes from participant_stats."""
    rows = conn.execute(
        "select s.id, s.ai_act, v.verdict, v.corrected_act, "
        "coalesce(ps.reliability, 0.5) "
        "from item_span s join vote v on v.item_span_id = s.id "
        "join participant p on p.id = v.participant_id "
        "left join participant_stats ps on ps.participant_id = p.id"
    ).fetchall()
    out: Dict[int, Tuple[str, List[Vote]]] = {}
    for span_id, ai_act, verdict, corrected, reliability in rows:
        bucket = out.setdefault(span_id, (ai_act, []))
        bucket[1].append(Vote(span_id, verdict, corrected, float(reliability)))
    return out


def fetch_perception_records(conn, axis: str) -> List[Dict]:
    """One record per vote on a span: the chosen act + the voter's demographic `axis` value."""
    allowed = {"age_band", "gender", "region", "education"}
    if axis not in allowed:
        raise ValueError(f"axis must be one of {allowed}")
    rows = conn.execute(
        f"select case when v.verdict='agree' then s.ai_act else v.corrected_act end, p.{axis} "
        "from vote v join item_span s on s.id = v.item_span_id "
        "join participant p on p.id = v.participant_id "
        "where (v.verdict='agree' or v.corrected_act is not null)"
    ).fetchall()
    return [{"act": act, axis: group} for act, group in rows]


def fetch_pending_suggestions(conn) -> List[Dict]:
    rows = conn.execute(
        "select sg.id, s.ai_act, i.text, sg.text "
        "from suggestion sg join item_span s on s.id = sg.item_span_id "
        "join item i on i.id = s.item_id where sg.status='pending'"
    ).fetchall()
    return [{"id": sid, "act": act, "original": orig, "paraphrase": para}
            for sid, act, orig, para in rows]


def set_suggestion_status(conn, suggestion_id: int, status: str) -> None:
    conn.execute("update suggestion set status=%s where id=%s", (status, suggestion_id))
    conn.commit()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/integration/test_collect_db.py -v`
Expected: SKIPPED without `TEST_DATABASE_URL`; PASS with it set against a fresh Postgres.

- [ ] **Step 6: Commit**

```bash
git add src/chomsky/collect/db.py tests/integration/test_collect_db.py pyproject.toml
git commit -m "feat(collect): psycopg DB adapter (insert items, fetch votes/perception/suggestions)"
```

---

### Task 9: CLI (`cli`) ligando tudo

**Files:**
- Create: `src/chomsky/collect/cli.py`, `src/chomsky/collect/__main__.py`
- Test: `tests/test_collect_cli.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_collect_cli.py
from chomsky.collect.cli import build_arg_parser


def test_parser_exposes_all_subcommands():
    p = build_arg_parser()
    for cmd in ["export", "ingest", "aggregate", "confirm", "perception"]:
        args = p.parse_args([cmd])
        assert args.command == cmd


def test_aggregate_has_threshold_default():
    args = build_arg_parser().parse_args(["aggregate"])
    assert args.threshold == 0.66


def test_perception_requires_axis_with_default():
    args = build_arg_parser().parse_args(["perception"])
    assert args.axis == "region"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_collect_cli.py -v`
Expected: FAIL with "No module named 'chomsky.collect.cli'".

- [ ] **Step 3: Write the implementation**

```python
# src/chomsky/collect/cli.py
"""Offline pipeline entrypoint. Reads DATABASE_URL. Subcommands:
  export   --dataset PATH --honeypots PATH   build items from JSONL annotations -> DB
  ingest                                      print vote counts per span (sanity)
  aggregate --threshold 0.66 --out PATH       resolve spans -> gold JSONL + contested JSONL
  confirm                                      confirm pending paraphrases via DeepSeek
  perception --axis region                     act distribution by demographic axis
"""
import argparse
import json
from chomsky.collect import db
from chomsky.collect.aggregate import resolve_span
from chomsky.collect.perception import act_distribution_by_group, groups_disagree
from chomsky.collect.confirm import confirm_suggestion


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="chomsky.collect", description="Coleta colaborativa — pipeline offline.")
    sub = p.add_subparsers(dest="command", required=True)
    e = sub.add_parser("export"); e.add_argument("--dataset", required=True); e.add_argument("--honeypots", default=None)
    sub.add_parser("ingest")
    a = sub.add_parser("aggregate"); a.add_argument("--threshold", type=float, default=0.66); a.add_argument("--out", default="gold/collected.jsonl")
    sub.add_parser("confirm")
    pc = sub.add_parser("perception"); pc.add_argument("--axis", default="region")
    return p


def _load_annotations(path):
    from chomsky.train.data import load_jsonl
    return load_jsonl(path)


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    conn = db.connect()
    if args.command == "export":
        from chomsky.collect.select import build_items
        anns = _load_annotations(args.dataset)
        hps = _load_annotations(args.honeypots) if args.honeypots else []
        ids = db.insert_items(conn, build_items(anns, hps))
        print(json.dumps({"inserted_spans": len(ids)}))
    elif args.command == "ingest":
        by_span = db.fetch_votes_by_span(conn)
        print(json.dumps({"spans_with_votes": len(by_span)}))
    elif args.command == "aggregate":
        by_span = db.fetch_votes_by_span(conn)
        gold = 0
        with open(args.out, "w", encoding="utf-8") as f:
            for span_id, (ai_act, votes) in by_span.items():
                r = resolve_span(ai_act, votes, args.threshold)
                if r.is_gold:
                    gold += 1
                    f.write(json.dumps({"span_id": span_id, "act": r.act, "agreement": r.agreement}, ensure_ascii=False) + "\n")
        print(json.dumps({"gold_spans": gold}))
    elif args.command == "confirm":
        from chomsky.gen.deepseek import DeepSeekClient
        client = DeepSeekClient()
        n_ok = 0
        for s in db.fetch_pending_suggestions(conn):
            ok = confirm_suggestion(client, s["act"], s["original"], s["paraphrase"])
            db.set_suggestion_status(conn, s["id"], "confirmed" if ok else "rejected")
            n_ok += int(ok)
        print(json.dumps({"confirmed": n_ok}))
    elif args.command == "perception":
        records = db.fetch_perception_records(conn, args.axis)
        dist = act_distribution_by_group(records, args.axis)
        print(json.dumps({"axis": args.axis, "disagree": groups_disagree(dist), "distribution": dist}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# src/chomsky/collect/__main__.py
from chomsky.collect.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_collect_cli.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Run the whole suite**

Run: `.venv/bin/python -m pytest -q`
Expected: all green (existing 108 + the new unit tests; DB integration SKIPPED without `TEST_DATABASE_URL`).

- [ ] **Step 6: Commit**

```bash
git add src/chomsky/collect/cli.py src/chomsky/collect/__main__.py tests/test_collect_cli.py
git commit -m "feat(collect): CLI (export/ingest/aggregate/confirm/perception)"
```

---

## Self-Review

**Spec coverage:**
- export_batch → Task 3 (`build_items`) + Task 8 (`insert_items`) + Task 9 (`export`). ✓
- ingest → Task 8 (`fetch_votes_by_span`) + Task 9 (`ingest`). ✓
- aggregate (weighted by reliability, gold threshold) → Task 5 + Task 9. ✓
- confirm_suggestions (DeepSeek) → Task 7 + Task 9 (`confirm`). ✓
- perception (by demographic) → Task 6 + Task 8 (`fetch_perception_records`) + Task 9. ✓
- honeypots + reliability → Task 1 (`span_gold`) + Task 4 (`update_reliability`) + Task 5 (weighting). ✓
- scoring (points/streak/suggestion bonus) → Task 4. ✓
- Postgres schema (contract) → Task 1. ✓
- Reuse of `chomsky` (schema/agreement/gen) → schema.Annotation/Span in Tasks 3/5/8; gen.prompts.parse_llm_json + gen.deepseek in Task 7/9. (Note: `agreement.span_agreement` is available for an optional richer report but not required by these tasks; the weighted act-vote in Task 5 is the v1 metric.)

**Serving / next-item:** intentionally NOT here — it is per-request logic that lives in the web app (Plan 2). This plan exposes the data the app needs (`is_honeypot`, `span_gold`) and ingests what it writes.

**Placeholder scan:** no TBD/TODO; every code step is complete; no "handle edge cases" hand-waving.

**Type consistency:** `Vote(span_id, verdict, corrected_act, reliability)` and `SpanResolution(span_id, act, agreement, is_gold)` used identically in Tasks 2/5/8. `build_items` row shape (`text/source/is_honeypot/spans[{char_start,char_end,ai_act,display_order,gold_act?}]`) consumed unchanged by `insert_items` (Task 8). `resolve_span(ai_act, votes, threshold)` signature identical in Tasks 5/9. `confirm_suggestion(client, act, original, paraphrase, parse=...)` identical in Tasks 7/9.

---

## Próximo plano (separado)

**Plano 2 — Web app (Next.js/Vercel + Neon):** onboarding anônimo (4 campos + consentimento), loop do jogo (✓/✗ + sugestão), API routes (`next-item` com injeção de honeypot a cada ~7 e dedup por participante, `vote`, `suggestion`, `me`), pontuação no cliente/servidor usando as mesmas regras do `score.py`, e seed do banco a partir do `db/schema.sql`. Aplica o mesmo schema desta Task 1 como migration.
