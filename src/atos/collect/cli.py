"""Offline pipeline entrypoint. Reads DATABASE_URL. Subcommands:
  export   --dataset PATH --honeypots PATH   build items from JSONL annotations -> DB
  ingest                                      print vote counts per span (sanity)
  aggregate --threshold 0.66 --out PATH       resolve spans -> gold JSONL
  export-spans --out PATH --min-votes 1        transcript corrections (/assistir) -> training JSONL
  export-holdout --out PATH                     collected human gold (jogar + assistir) -> eval JSONL
  prioritize --w-dis 1.0 --w-rar 0.5           active-learning triage -> write item.priority
  confirm                                      confirm pending paraphrases via DeepSeek
  perception --axis region                     act distribution by demographic axis
"""
import argparse
import json
import os
from atos.collect import db
from atos.collect.aggregate import resolve_span
from atos.collect.perception import act_distribution_by_group, groups_disagree
from atos.collect.confirm import confirm_suggestion


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="atos.collect", description="Coleta colaborativa — pipeline offline.")
    sub = p.add_subparsers(dest="command", required=True)
    e = sub.add_parser("export")
    e.add_argument("--dataset", default=None)
    e.add_argument("--honeypots", default=None)
    e.add_argument("--source", default="synthetic",
                   help="domain tag for the seeded items (review/sac/entrevista/...)")
    sub.add_parser("ingest")
    a = sub.add_parser("aggregate")
    a.add_argument("--threshold", type=float, default=0.66)
    a.add_argument("--out", default="gold/collected.jsonl")
    es = sub.add_parser("export-spans")
    es.add_argument("--out", default="gold/collected-spans.jsonl")
    es.add_argument("--min-votes", type=int, default=1)
    es.add_argument("--source", default=None)
    eh = sub.add_parser("export-holdout")
    eh.add_argument("--out", default="gold/holdout-collected.jsonl")
    eh.add_argument("--domain", default="entrevista",
                    help="tag each line with this domain for multi-domain eval "
                         "(jogar/assistir gold is FAPESP interviews -> entrevista)")
    pr = sub.add_parser("prioritize")
    pr.add_argument("--w-dis", type=float, default=1.0, help="weight on human disagreement")
    pr.add_argument("--w-rar", type=float, default=0.5, help="weight on act rarity")
    pr.add_argument("--threshold", type=float, default=0.66)
    sub.add_parser("confirm")
    pc = sub.add_parser("perception")
    pc.add_argument("--axis", default="region")
    return p


def _load_annotations(path):
    from atos.train.data import load_jsonl
    return load_jsonl(path)


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    conn = db.connect()
    if args.command == "export":
        if not args.dataset:
            raise SystemExit("export requires --dataset")
        from atos.collect.select import build_items
        anns = _load_annotations(args.dataset)
        hps = _load_annotations(args.honeypots) if args.honeypots else []
        ids = db.insert_items(conn, build_items(anns, hps, args.source))
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
    elif args.command == "export-spans":
        from atos.collect.export_spans import build_annotations
        rows = db.fetch_span_annotations(conn, args.source)
        anns = build_annotations(rows, args.min_votes)
        out_dir = os.path.dirname(args.out)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            for a in anns:
                f.write(a.to_json() + "\n")
        print(json.dumps({"examples": len(anns), "spans": sum(len(a.spans) for a in anns)}))
    elif args.command == "export-holdout":
        from atos.collect.export_spans import gold_to_annotations, build_annotations
        jogar = gold_to_annotations(db.fetch_gold_spans(conn))
        assistir = build_annotations(db.fetch_span_annotations(conn))
        anns = jogar + assistir
        out_dir = os.path.dirname(args.out)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            for a in anns:
                obj = json.loads(a.to_json())
                obj["domain"] = args.domain
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        print(json.dumps({"jogar": len(jogar), "assistir": len(assistir),
                          "total": len(anns), "domain": args.domain}))
    elif args.command == "prioritize":
        from atos.collect.prioritize import compute_priorities
        spans = db.fetch_spans_with_items(conn)
        votes_by_span = {sid: tup[1] for sid, tup in db.fetch_votes_by_span(conn).items()}
        priorities = compute_priorities(spans, votes_by_span, args.w_dis, args.w_rar, args.threshold)
        n = db.update_item_priorities(conn, priorities)
        print(json.dumps({"items_scored": n}))
    elif args.command == "confirm":
        from atos.gen.deepseek import DeepSeekClient
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
