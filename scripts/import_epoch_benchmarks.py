"""Import Epoch's Benchmarking Hub data (benchmark_data.zip) into data/evals.csv.

Epoch's zip layout isn't documented, so step 1 is to look at it:

    python scripts/import_epoch_benchmarks.py --inspect [path/to/benchmark_data.zip]

That prints every CSV in the zip with its columns. Fill in MAPPING below
from that output, then run without --inspect. Models are matched to
models.csv by model name, so import models first.
"""
import csv, io, re, sys, zipfile, datetime, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from schema import EVALS, header

URL = "https://epoch.ai/data/benchmark_data.zip"
DATA = Path(__file__).parent.parent / "data"
TODAY = datetime.date.today().isoformat()

# TODO(after --inspect): one entry per CSV in the zip you want to import.
# "file.csv": {"benchmark": "<name to store>", "model": "<model column>",
#              "score": "<score column>", "unit": "fraction|percent|elo|other",
#              "setting": "<column or None>", "source": "<url column or None>"}
# The ECI file, if present, goes in ECI instead (fills models.csv eci).
MAPPING = {}
ECI = None  # e.g. {"file": "eci.csv", "model": "...", "score": "..."}

def slugify(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def open_zip(src):
    data = Path(src).read_bytes() if src else urllib.request.urlopen(URL, timeout=120).read()
    return zipfile.ZipFile(io.BytesIO(data))

def read(z, name):
    return list(csv.DictReader(io.StringIO(z.read(name).decode("utf-8"))))

def main(*args):
    inspect = "--inspect" in args
    src = next((a for a in args if not a.startswith("--")), None)
    z = open_zip(src)
    if inspect or not MAPPING:
        for n in z.namelist():
            if n.endswith(".csv"):
                rows = read(z, n)
                print(f"\n{n}  ({len(rows)} rows)\n  columns: {list(rows[0].keys()) if rows else []}")
        if not MAPPING: print("\nMAPPING is empty: fill it in from the columns above, then re-run.")
        return

    models = list(csv.DictReader(open(DATA / "models.csv", encoding="utf-8")))
    by_name = {slugify(m["model_name"]): m["model_id"] for m in models}
    existing = list(csv.DictReader(open(DATA / "evals.csv", encoding="utf-8")))
    out = [r for r in existing if r["origin"] == "community"]
    unmatched = set()
    for fname, m in MAPPING.items():
        for r in read(z, fname):
            mid = by_name.get(slugify(r[m["model"]]))
            if not mid or not r[m["score"]].strip():
                unmatched.add(r[m["model"]]); continue
            out.append({"model_id": mid, "benchmark": m["benchmark"],
                        "eval_setting": r[m["setting"]] if m.get("setting") else "",
                        "score": r[m["score"]].strip(), "score_unit": m["unit"],
                        "source_url": (r[m["source"]] if m.get("source") else "") or "https://epoch.ai/benchmarks",
                        "notes": "", "contributor": "epoch-ai-import", "date_added": TODAY, "origin": "epoch"})
    with open(DATA / "evals.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header(EVALS)); w.writeheader(); w.writerows(out)
    print(f"wrote {len(out)} evals; {len(unmatched)} model names didn't match models.csv")
    if unmatched: print("  e.g.", sorted(unmatched)[:15])
    # TODO: ECI -> models.csv eci column, once ECI's file/columns are known.

if __name__ == "__main__":
    main(*sys.argv[1:])
