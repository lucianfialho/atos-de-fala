"""Offline pipeline entrypoint. Reads DATABASE_URL. Subcommands:
  export   --dataset PATH --honeypots PATH   build items from JSONL annotations -> DB
  ingest                                      print vote counts per span (sanity)
  aggregate --threshold 0.66 --out PATH       resolve spans -> gold JSONL
  confirm                                      confirm pending paraphrases via DeepSeek
  perception --axis region                     act distribution by demographic axis
"""
import argparse
import json
import os
from chomsky.collect import db
from chomsky.collect.aggregate import resolve_span
from chomsky.collect.perception import act_distribution_by_group, groups_disagree
from chomsky.collect.confirm import confirm_suggestion


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="chomsky.collect", description="Coleta colaborativa — pipeline offline.")
    sub = p.add_subparsers(dest="command", required=True)
    e = sub.add_parser("export")
    e.add_argument("--dataset", default=None)
    e.add_argument("--honeypots", default=None)
    sub.add_parser("ingest")
    a = sub.add_parser("aggregate")
    a.add_argument("--threshold", type=float, default=0.66)
    a.add_argument("--out", default="gold/collected.jsonl")
    sub.add_parser("confirm")
    pc = sub.add_parser("perception")
    pc.add_argument("--axis", default="region")
    return p


def _load_annotations(path):
    from chomsky.train.data import load_jsonl
    return load_jsonl(path)


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    conn = db.connect()
    if args.command == "export":
        if not args.dataset:
            raise SystemExit("export requires --dataset")
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
        out_dir = os.path.dirname(args.out)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
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
