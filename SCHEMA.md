# Schema

Two linked tables. `scripts/schema.py` is the source of truth; `scripts/validate.py` enforces it.
Multi-valued cells use `;` (e.g. `Language;Vision`). Numbers may use scientific notation (`3.1e23`).

## data/models.csv (one row per model)

| Column | Required | Values | Notes |
|---|---|---|---|
| model_id | yes | lowercase-with-hyphens, unique | Primary key |
| model_name | yes | | |
| organization | | | |
| domain | yes | `;` list | Language, Vision, Games, Biology, … (Epoch's domains) |
| task | | `;` list | |
| release_date | yes | YYYY-MM-DD | Publication or announcement date |
| training_compute_flop | | number | Total training FLOP |
| compute_lower_flop / compute_upper_flop | | number | Uncertainty range; the estimate must sit inside it |
| compute_estimate_method | yes | reported, operation_counting, hardware, benchmark_extrapolation, other, unknown | How the FLOP number was estimated |
| compute_confidence | yes | confident, likely, speculative, unknown | Epoch's confidence labels |
| compute_notes | | | Working / reasoning behind the estimate |
| parameters | | number | |
| training_data_size | | number | Tokens for language models; datapoints otherwise (Epoch's convention) |
| architecture | yes | dense, moe, other, unknown | Not in Epoch's data, so community-filled |
| weights | yes | open, open_restricted, api, closed, unknown | |
| model_stage | yes | base, finetuned, unknown | |
| base_model | | | Set when finetuned |
| frontier | | true, false | Epoch's "frontier model" flag |
| eci | | number | Epoch Capabilities Index. Language models only; other domains use evals.csv |
| source_url | yes | URL | Paper, blog post, or Epoch page |
| notes | | | |
| contributor | yes | | GitHub handle, or `epoch-ai-import` |
| date_added | yes | YYYY-MM-DD | |
| origin | yes | epoch, community | Imported rows are refreshed on re-import; community rows never are |

## data/evals.csv (one row per model × benchmark score)

| Column | Required | Values | Notes |
|---|---|---|---|
| model_id | yes | must exist in models.csv | |
| benchmark | yes | | e.g. GPQA Diamond, ImageNet top-1, Atari-57 |
| eval_setting | | | e.g. 5-shot, pass@1. (model_id, benchmark, eval_setting) is unique |
| score | yes | number | |
| score_unit | yes | fraction, percent, elo, other | fraction must be ≤ 1 |
| source_url | yes | URL | |
| notes, contributor, date_added, origin | | | as above (contributor, date_added, origin required) |

## Why it's shaped this way

- **Two tables:** a new benchmark is new rows, not a new column, so contributions don't change the schema.
- **Compute uncertainty is first-class** (method, confidence, bounds) because Ho names missing and uncertain compute data as the main bottleneck.
- **All domains, with `eci` LM-only:** non-language models get their capability from domain benchmarks in evals.csv.
