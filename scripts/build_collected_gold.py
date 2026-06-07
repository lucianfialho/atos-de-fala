"""Build domain-tagged eval gold from crowd signal collected on the site.

Two sources, merged and tagged by item.source (domain) so it feeds atos.train.multidomain:
  1. votes on model spans  -> resolve_span (weighted majority); kept when the winning act's
     share reaches --threshold. Low threshold = directional (1 endorsing vote already passes).
  2. span_annotation       -> the human-drawn spans from /jogar 're-marcar' and /assistir,
     grouped by (source, context). These OVERRIDE vote-resolved spans for the same text
     (a human redraw beats a judged proposal).

Honeypots are excluded (their gold is the seeded answer, not crowd signal). Spans are made
non-overlapping (BIOES needs that). With a low threshold this is a NOISY directional read,
not the final gold — raise --threshold once consensus fills in.

    python scripts/build_collected_gold.py --threshold 0.5 --out gold/collected-md.jsonl
"""
import argparse
import json
from collections import defaultdict

from atos.collect import db
from atos.collect.aggregate import resolve_span
from atos.collect.models import Vote


def _non_overlapping(spans):
    spans = sorted(set(spans), key=lambda t: (t[0], -(t[1] - t[0])))
    out, last = [], -1
    for cs, ce, act in spans:
        if cs < last:
            continue
        out.append((cs, ce, act))
        last = ce
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="build_collected_gold")
    p.add_argument("--threshold", type=float, default=0.5, help="winning-act share to count as gold")
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    conn = db.connect()

    # 1. votes -> resolved gold per item, with text/offsets/source
    rows = conn.execute(
        "select s.id, s.ai_act, i.id, i.text, s.char_start, s.char_end, i.source, "
        "       v.verdict, v.corrected_act, coalesce(ps.reliability, 0.5) "
        "from item_span s join vote v on v.item_span_id = s.id "
        "join item i on i.id = s.item_id "
        "join participant p on p.id = v.participant_id "
        "left join participant_stats ps on ps.participant_id = p.id "
        "where i.is_honeypot = false"
    ).fetchall()
    meta, votes = {}, defaultdict(list)
    for sid, ai, iid, txt, cs, ce, src, verdict, corr, rel in rows:
        meta[sid] = (ai, txt, cs, ce, src)
        votes[sid].append(Vote(sid, verdict, corr, float(rel)))

    gold = {}  # (source, text) -> [(cs, ce, act)]
    for sid, vs in votes.items():
        ai, txt, cs, ce, src = meta[sid]
        r = resolve_span(ai, vs, args.threshold)
        if r.is_gold and r.act:
            gold.setdefault((src, txt), []).append((cs, ce, r.act))

    # 2. span_annotation (human redraw) overrides vote-resolved for the same (source, text)
    ann = defaultdict(list)
    for a in db.fetch_span_annotations(conn):
        ann[(a["source"], a["context"])].append((a["char_start"], a["char_end"], a["act"]))
    for key, sp in ann.items():
        gold[key] = sp

    by_dom = defaultdict(int)
    n = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for (src, txt), sp in gold.items():
            sp = _non_overlapping(sp)
            if not sp:
                continue
            f.write(json.dumps(
                {"text": txt, "spans": [{"start": a, "end": b, "act": c} for a, b, c in sp],
                 "domain": src or "geral"}, ensure_ascii=False) + "\n")
            n += 1
            by_dom[src or "geral"] += 1
    print(json.dumps({"items": n, "by_domain": dict(by_dom), "threshold": args.threshold}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
