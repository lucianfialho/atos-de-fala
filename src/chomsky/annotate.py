"""Visual web annotator for the human gold set (zero extra deps, stdlib only).

Runs on the box; you reach it from the laptop browser over Tailscale. You select a
text fragment with the mouse, click an act (13 buttons or number keys), and it saves
a quote-based span. The working file is the same quote-JSONL that `chomsky.gold compile`
consumes, so the flow is: annotate here -> `gold compile` -> `gold score`/eval.

    python -m chomsky.annotate --file gold/to_annotate.jsonl --port 8765 --host 0.0.0.0
    # then open http://lucian-desktop.tailbb1a78.ts.net:8765  (or the 100.x tailnet IP)

No auth — bind to the tailnet IP (or keep it on a trusted box). Edits autosave to --file.
"""
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List
from chomsky.taxonomy import load_taxonomy
from chomsky.gold import compile_gold
from chomsky._annotate_ui import HTML as _HTML

_FILE = ""
_ACTS: List[str] = []
_TAXONOMY = None


def read_rows(path: str) -> List[Dict]:
    """Read the working quote-JSONL: [{text, spans:[{quote,act}]}]. Missing file -> []."""
    if not os.path.exists(path):
        return []
    rows: List[Dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            rows.append({"text": obj.get("text", ""), "spans": obj.get("spans", [])})
    return rows


def write_rows(path: str, rows: List[Dict]) -> None:
    """Persist rows as quote-JSONL, keeping only {quote,act} per span."""
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            spans = [{"quote": s["quote"], "act": s["act"]} for s in r.get("spans", [])]
            f.write(json.dumps({"text": r.get("text", ""), "spans": spans}, ensure_ascii=False) + "\n")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):  # quiet
        pass

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            self._send(200, _HTML, "text/html; charset=utf-8")
        elif self.path == "/api/state":
            self._send(200, json.dumps({"acts": _ACTS, "rows": read_rows(_FILE)}, ensure_ascii=False))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path != "/api/save":
            self._send(404, json.dumps({"error": "not found"}))
            return
        n = int(self.headers.get("Content-Length", 0))
        rows = json.loads(self.rfile.read(n) or b"{}").get("rows", [])
        write_rows(_FILE, rows)
        anns, errors = compile_gold(rows, _TAXONOMY)
        self._send(200, json.dumps({"ok": True, "valid": len(anns), "errors": errors}, ensure_ascii=False))


def main(argv=None) -> int:
    global _FILE, _ACTS, _TAXONOMY
    p = argparse.ArgumentParser(prog="chomsky.annotate", description="Visual web annotator for the gold set.")
    p.add_argument("--file", required=True, help="working quote-JSONL (e.g. gold/to_annotate.jsonl)")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--host", default="0.0.0.0", help="bind host (use the 100.x tailnet IP for tailnet-only)")
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args(argv)
    _FILE = args.file
    _TAXONOMY = load_taxonomy(args.taxonomy)
    _ACTS = _TAXONOMY.acts
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"annotator on http://{args.host}:{args.port}  (file: {_FILE}, {len(_ACTS)} acts)")
    print("open it from the laptop via the tailnet hostname; Ctrl-C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
