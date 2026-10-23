"""Import Epoch's Benchmarking Hub data (benchmark_data.zip, CC-BY 4.0) into data/evals.csv,
and fill the eci column of data/models.csv from Epoch Capabilities Index scores.

    python scripts/import_epoch_benchmarks.py                       # downloads the zip
    python scripts/import_epoch_benchmarks.py raw/benchmark_data.zip

Driven by the zip's own benchmark_metadata.csv (which file and score column each
benchmark uses, plus a scale factor). Run import_epoch_models.py first: rows are
matched to models.csv by model name, via the zip's model_metadata.csv.
Community rows in evals.csv are kept.
"""
import csv, io, re, sys, zipfile, datetime, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from schema import EVALS, MODELS, LIST_SEP, header

URL = "https://epoch.ai/data/benchmark_data.zip"
DATA = Path(__file__).parent.parent / "data"
TODAY = datetime.date.today().isoformat()
FALLBACK_SOURCE = "https://epoch.ai/benchmarks"

def norm(s): return re.sub(r"[^a-z0-9]+", "", (s or "").lower())

def main(src=None):
    data = Path(src).read_bytes() if src else urllib.request.urlopen(URL, timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(data))
    rd = lambda n: list(csv.DictReader(io.StringIO(z.read(n).decode("utf-8"))))

    models = list(csv.DictReader(open(DATA / "models.csv", encoding="utf-8")))
    by_name = {}
    for m in models: by_name.setdefault(norm(m["model_name"]), m["model_id"])
    version_to_group = {r["model_version"]: r["model_group"] for r in rd("model_metadata.csv") if r["model_version"]}

    def match(row):
        for cand in (version_to_group.get(row.get("Model version", "")), row.get("Name"), row.get("Model version")):
            if cand and norm(cand) in by_name: return by_name[norm(cand)]
        return None

    existing = list(csv.DictReader(open(DATA / "evals.csv", encoding="utf-8")))
    out = [r for r in existing if r["origin"] == "community"]
    seen = {(r["model_id"], r["benchmark"], r["eval_setting"]) for r in out}
    names = set(z.namelist())
    stats = {"rows": 0, "unmatched": 0, "dupes": 0, "no_score": 0}
    unmatched = set()

    for b in rd("benchmark_metadata.csv"):
        f, col = b["source_file"], b["score_column"]
        if not f or f not in names: continue
        scale = float(b["scale"] or 1)
        for r in rd(f):
            stats["rows"] += 1
            try: score = float(r[col]) * scale
            except (KeyError, ValueError): stats["no_score"] += 1; continue
            mid = match(r)
            if not mid:
                stats["unmatched"] += 1; unmatched.add(r.get("Model version") or r.get("Name")); continue
            setting = LIST_SEP.join(x for x in (r.get("Model version", "").strip(),
                                                 f"{r['Shots']}-shot" if r.get("Shots") else "") if x)
            key = (mid, b["benchmark"], setting)
            if key in seen: stats["dupes"] += 1; continue
            seen.add(key)
            link = r.get("Source link") or r.get("Source Link") or r.get("Log viewer") or ""
            out.append({"model_id": mid, "benchmark": b["benchmark"], "eval_setting": setting,
                        "score": f"{score:.6g}", "score_unit": "fraction" if 0 <= score <= 1 else "other",
                        "source_url": link if link.startswith("http") else FALLBACK_SOURCE,
                        "notes": (r.get("Source") or "").strip(),
                        "contributor": "epoch-ai-import", "date_added": TODAY, "origin": "epoch"})

    with open(DATA / "evals.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header(EVALS)); w.writeheader()
        w.writerows(sorted(out, key=lambda r: (r["benchmark"], r["model_id"], r["eval_setting"])))

    # ECI -> models.csv (language models only; validator enforces this)
    eci_hits = eci_total = 0
    eci = {}
    for r in rd("epoch_capabilities_index/eci_scores.csv"):
        eci_total += 1
        mid = by_name.get(norm(r["Model"])) or by_name.get(norm(r["Display name"]))
        if mid and r["eci"]: eci[mid] = r["eci"]
    for m in models:
        if m["model_id"] in eci and "Language" in m["domain"].split(LIST_SEP):
            m["eci"] = eci[m["model_id"]]; eci_hits += 1
    with open(DATA / "models.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header(MODELS)); w.writeheader(); w.writerows(models)

    print(f"evals: wrote {len(out)} rows from {stats['rows']} source rows "
          f"({stats['unmatched']} unmatched model, {stats['dupes']} duplicate, {stats['no_score']} no score)")
    print(f"eci: filled {eci_hits} of {eci_total} ECI scores")
    if unmatched: print("  unmatched examples:", sorted(x for x in unmatched if x)[:12])

if __name__ == "__main__":
    main(*sys.argv[1:])
