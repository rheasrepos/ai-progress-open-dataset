"""Import Epoch AI's "AI Models" database (CC-BY 4.0) into data/models.csv.

    python scripts/import_epoch_models.py                 # downloads the CSV
    python scripts/import_epoch_models.py path/to/all_ai_models.csv

Re-running is safe: rows with origin=community are kept untouched, and on
Epoch rows the columns Epoch doesn't have (architecture, eci, notes) keep
whatever a contributor filled in.
"""
import csv, io, re, sys, datetime, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from schema import MODELS, LIST_SEP, header

URL = "https://epoch.ai/data/all_ai_models.csv"
FALLBACK_SOURCE = "https://epoch.ai/data/ai-models"
OUT = Path(__file__).parent.parent / "data" / "models.csv"
COMMUNITY_FIELDS = ("architecture", "eci", "notes")  # not in Epoch's data
TODAY = datetime.date.today().isoformat()

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def to_list(s):
    return LIST_SEP.join(p.strip() for p in (s or "").split(",") if p.strip())

def method(raw):
    r = (raw or "").lower()
    if not r: return "unknown"
    for key, val in (("operation", "operation_counting"), ("hardware", "hardware"),
                     ("benchmark", "benchmark_extrapolation"), ("report", "reported"),
                     ("disclos", "reported")):
        if key in r: return val
    return "other"

def confidence(raw):
    r = (raw or "").strip().lower()
    return r if r in {"confident", "likely", "speculative"} else "unknown"

def weights(raw):
    r = (raw or "").lower()
    if "open weights" in r:
        return "open" if "unrestricted" in r else "open_restricted"
    if "api" in r: return "api"
    if "unreleased" in r or "hosted" in r: return "closed"
    return "unknown"

def num(raw):
    raw = (raw or "").replace(",", "").strip()
    try: float(raw); return raw
    except ValueError: return ""

def convert(e):
    link = next((l.strip() for l in (e.get("Link") or "").splitlines() if l.strip().startswith("http")), "")
    raw_method = (e.get("Training compute estimation method") or "").strip()
    notes = (e.get("Training compute notes") or "").strip()
    return {
        "model_id": slugify(e["Model"]),
        "model_name": e["Model"].strip(),
        "organization": (e.get("Organization") or "").strip(),
        "domain": to_list(e.get("Domain")) or "Other",
        "task": to_list(e.get("Task")),
        "release_date": (e.get("Publication date") or "").strip()[:10],
        "training_compute_flop": num(e.get("Training compute (FLOP)")),
        "compute_lower_flop": num(e.get("Training compute lower bound")),
        "compute_upper_flop": num(e.get("Training compute upper bound")),
        "compute_estimate_method": method(raw_method),
        "compute_confidence": confidence(e.get("Confidence")),
        "compute_notes": (f"[Epoch method: {raw_method}] " if raw_method else "") + notes,
        "parameters": num(e.get("Parameters")),
        "training_data_size": num(e.get("Training dataset size (total)")),
        "architecture": "unknown",
        "weights": weights(e.get("Model accessibility")),
        "model_stage": "finetuned" if (e.get("Base model") or "").strip() else "unknown",
        "base_model": (e.get("Base model") or "").strip(),
        "frontier": "true" if (e.get("Frontier model") or "").strip().lower() in ("true", "yes") else "false",
        "eci": "",
        "source_url": link or FALLBACK_SOURCE,
        "notes": "",
        "contributor": "epoch-ai-import",
        "date_added": TODAY,
        "origin": "epoch",
    }

def main(src=None):
    if src: text = Path(src).read_text(encoding="utf-8")
    else:   text = urllib.request.urlopen(URL, timeout=60).read().decode("utf-8")
    epoch_rows = list(csv.DictReader(io.StringIO(text)))

    existing = list(csv.DictReader(open(OUT, encoding="utf-8"))) if OUT.exists() else []
    community = [r for r in existing if r["origin"] == "community"]
    old_epoch = {r["model_id"]: r for r in existing if r["origin"] == "epoch"}
    taken = {r["model_id"] for r in community}

    out, skipped = [], 0
    for e in epoch_rows:
        if not (e.get("Model") or "").strip() or not (e.get("Publication date") or "").strip():
            skipped += 1; continue
        row = convert(e)
        base, n = row["model_id"], 2
        while row["model_id"] in taken:
            row["model_id"] = f"{base}-{n}"; n += 1
        taken.add(row["model_id"])
        if row["model_id"] in old_epoch:
            prev = old_epoch[row["model_id"]]
            for k in COMMUNITY_FIELDS:
                if prev.get(k) and prev[k] != "unknown": row[k] = prev[k]
            row["date_added"] = prev["date_added"]
        out.append(row)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header(MODELS)); w.writeheader()
        w.writerows(sorted(out + community, key=lambda r: (r["release_date"], r["model_id"])))
    print(f"wrote {len(out)} Epoch + {len(community)} community models to {OUT} (skipped {skipped} with no name/date)")

if __name__ == "__main__":
    main(*sys.argv[1:])
