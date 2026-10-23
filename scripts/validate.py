"""Validate data/models.csv and data/evals.csv. Stdlib only, so CI needs no installs.
Usage: python scripts/validate.py [data_dir]   (exit code 1 on any error)"""
import csv, re, sys, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from schema import MODELS, EVALS, LIST_SEP, header

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def check_cell(kind, allowed, v):
    if kind == "slug":  return bool(SLUG.match(v)) or "must be lowercase-with-hyphens"
    if kind == "date":
        try: datetime.date.fromisoformat(v); return True
        except ValueError: return "must be YYYY-MM-DD"
    if kind in ("float", "int"):
        try: x = float(v)
        except ValueError: return "must be a number (scientific notation ok, e.g. 3.1e23)"
        return x >= 0 or "must be non-negative"
    if kind == "enum":  return v in allowed or f"must be one of {sorted(allowed)}"
    if kind == "bool":  return v in ("true", "false") or "must be true or false"
    if kind == "url":   return v.startswith(("http://", "https://")) or "must start with http(s)://"
    if kind == "list":  return all(p.strip() for p in v.split(LIST_SEP)) or f"empty item in '{LIST_SEP}'-separated list"
    return True

def load(path, cols, errors):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if r.fieldnames != header(cols):
            errors.append(f"{path.name}: header must be exactly {header(cols)}")
            return []
        rows = list(r)
    for i, row in enumerate(rows, start=2):  # line 1 is the header
        for name, kind, required, allowed in cols:
            v = (row.get(name) or "").strip()
            if not v:
                if required: errors.append(f"{path.name}:{i} {name} is required")
                continue
            ok = check_cell(kind, allowed, v)
            if ok is not True: errors.append(f"{path.name}:{i} {name}={v!r} {ok}")
    return rows

def main(data_dir="data"):
    d, errors = Path(data_dir), []
    models = load(d / "models.csv", MODELS, errors)
    evals = load(d / "evals.csv", EVALS, errors)

    ids = {}
    for i, m in enumerate(models, start=2):
        if m["model_id"] in ids: errors.append(f"models.csv:{i} duplicate model_id {m['model_id']} (first on line {ids[m['model_id']]})")
        ids.setdefault(m["model_id"], i)
        try:
            lo, mid, hi = (float(m[k]) if m[k] else None for k in ("compute_lower_flop", "training_compute_flop", "compute_upper_flop"))
            tol = 1.01  # allow 1% for rounding in source data
            if lo is not None and hi is not None and lo > hi * tol: errors.append(f"models.csv:{i} compute_lower_flop > compute_upper_flop")
            if mid is not None and ((lo is not None and mid * tol < lo) or (hi is not None and mid > hi * tol)):
                errors.append(f"models.csv:{i} training_compute_flop outside [lower, upper]")
        except ValueError: pass  # already reported above
        if m["eci"] and "Language" not in m["domain"].split(LIST_SEP):
            errors.append(f"models.csv:{i} eci is only defined for Language models")

    seen = set()
    for i, e in enumerate(evals, start=2):
        if e["model_id"] and e["model_id"] not in ids: errors.append(f"evals.csv:{i} model_id {e['model_id']} not in models.csv")
        key = (e["model_id"], e["benchmark"], e["eval_setting"])
        if key in seen: errors.append(f"evals.csv:{i} duplicate (model_id, benchmark, eval_setting)")
        seen.add(key)
        if e["score_unit"] == "fraction" and e["score"]:
            try:
                if float(e["score"]) > 1: errors.append(f"evals.csv:{i} fraction score > 1 (use percent?)")
            except ValueError: pass

    for msg in errors[:200]: print("ERROR", msg)
    if len(errors) > 200: print(f"... and {len(errors) - 200} more")
    print(f"{len(models)} models, {len(evals)} evals, {len(errors)} errors")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
