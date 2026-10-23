"""Column definitions for models.csv and evals.csv. Single source of truth:
validate.py, the importers, and SCHEMA.md all follow this file."""

LIST_SEP = ";"  # separator for multi-valued cells (e.g. domain)

# kind: str | slug | date | float | int | enum | list | bool | url
MODELS = [
    # name,                    kind,   required, allowed values / notes
    ("model_id",               "slug",  True,  None),
    ("model_name",             "str",   True,  None),
    ("organization",           "str",   False, None),
    ("domain",                 "list",  True,  None),  # e.g. "Language;Vision"
    ("task",                   "list",  False, None),
    ("release_date",           "date",  True,  None),
    ("training_compute_flop",  "float", False, None),
    ("compute_lower_flop",     "float", False, None),
    ("compute_upper_flop",     "float", False, None),
    ("compute_estimate_method","enum",  True,
        {"reported", "operation_counting", "hardware", "benchmark_extrapolation", "other", "unknown"}),
    ("compute_confidence",     "enum",  True,  {"confident", "likely", "speculative", "unknown"}),
    ("compute_notes",          "str",   False, None),
    ("parameters",             "float", False, None),
    ("training_data_size",     "float", False, None),  # tokens for language models
    ("architecture",           "enum",  True,  {"dense", "moe", "other", "unknown"}),
    ("weights",                "enum",  True,  {"open", "open_restricted", "api", "closed", "unknown"}),
    ("model_stage",            "enum",  True,  {"base", "finetuned", "unknown"}),
    ("base_model",             "str",   False, None),
    ("frontier",               "bool",  False, None),
    ("eci",                    "float", False, None),  # Epoch Capabilities Index; LMs only
    ("source_url",             "url",   True,  None),
    ("notes",                  "str",   False, None),
    ("contributor",            "str",   True,  None),
    ("date_added",             "date",  True,  None),
    ("origin",                 "enum",  True,  {"epoch", "community"}),
]

EVALS = [
    ("model_id",     "slug",  True,  None),   # must exist in models.csv
    ("benchmark",    "str",   True,  None),
    ("eval_setting", "str",   False, None),   # e.g. "5-shot", "pass@1"
    ("score",        "float", True,  None),
    ("score_unit",   "enum",  True,  {"fraction", "percent", "elo", "other"}),
    ("source_url",   "url",   True,  None),
    ("notes",        "str",   False, None),
    ("contributor",  "str",   True,  None),
    ("date_added",   "date",  True,  None),
    ("origin",       "enum",  True,  {"epoch", "community"}),
]

def header(cols):
    return [c[0] for c in cols]
