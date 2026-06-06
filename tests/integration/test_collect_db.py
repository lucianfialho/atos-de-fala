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
