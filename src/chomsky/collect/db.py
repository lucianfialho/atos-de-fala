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
