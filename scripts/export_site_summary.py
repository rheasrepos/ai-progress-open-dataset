#!/usr/bin/env python3
"""Summarize data/models.csv for the raddotcom Progress? page (rheamad.vercel.app/ai-problems).

    python3 scripts/export_site_summary.py [out.json]     (default: build/site_summary.json)

Writes, with no judgement added:
  totals     models, with compute, open weights (open + open_restricted), frontier
  by_year    models released per year, and the largest training compute that year
  by_task    for every task label: models, open-weight models, first and latest year, newest model
  by_domain  the same per domain
The raddotcom sync copies it to static/ai-progress.json.
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def main(out=str(ROOT / "build" / "site_summary.json")):
    rows = list(csv.DictReader(open(ROOT / "data" / "models.csv", encoding="utf-8")))
    openw = lambda r: r["weights"] in ("open", "open_restricted")
    year = lambda r: int(r["release_date"][:4]) if r["release_date"][:4].isdigit() else None
    by_year = defaultdict(lambda: {"models": 0, "max_compute_flop": None})
    def bucket(): return {"models": 0, "open_weights": 0, "first_year": None, "latest_year": None, "newest": "", "_d": ""}
    by_task, by_domain = defaultdict(bucket), defaultdict(bucket)
    for r in rows:
        y, c = year(r), num(r["training_compute_flop"])
        if y:
            by_year[y]["models"] += 1
            if c and (by_year[y]["max_compute_flop"] or 0) < c: by_year[y]["max_compute_flop"] = c
        for key, table in (("task", by_task), ("domain", by_domain)):
            for v in {s.strip() for s in (r[key] or "").split(";") if s.strip()}:
                b = table[v]; b["models"] += 1; b["open_weights"] += openw(r)
                if y:
                    b["first_year"] = y if b["first_year"] is None else min(b["first_year"], y)
                    b["latest_year"] = y if b["latest_year"] is None else max(b["latest_year"], y)
                if r["release_date"] > b["_d"]: b["_d"], b["newest"] = r["release_date"], r["model_name"]
    clean = lambda t: {k: {kk: vv for kk, vv in v.items() if kk != "_d"} for k, v in sorted(t.items())}
    summary = {
        "source": "https://github.com/rheasrepos/ai-progress-open-dataset (seeded from Epoch AI's AI Models database)",
        "totals": {"models": len(rows), "with_compute": sum(1 for r in rows if num(r["training_compute_flop"])),
                   "open_weights": sum(openw(r) for r in rows), "frontier": sum(r["frontier"] == "true" for r in rows)},
        "by_year": {y: by_year[y] for y in sorted(by_year)},
        "by_task": clean(by_task), "by_domain": clean(by_domain)}
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(summary, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {out}: {len(rows)} models, {len(by_task)} tasks, {len(by_domain)} domains")

if __name__ == "__main__":
    main(*sys.argv[1:])
