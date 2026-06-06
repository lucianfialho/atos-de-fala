import os
import pytest

DSN = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DSN, reason="set TEST_DATABASE_URL to run DB integration tests")


# Requer um Postgres DESCARTÁVEL em TEST_DATABASE_URL: aplica o schema (idempotente) e não faz teardown.
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
