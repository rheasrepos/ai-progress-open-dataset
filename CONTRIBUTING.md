# Contributing

1. Fork, then edit `data/models.csv` and/or `data/evals.csv` (any spreadsheet app works; save as CSV, UTF-8).
2. Set `origin` to `community`, `contributor` to your GitHub handle, and `date_added` to today.
3. Every number needs a `source_url`. For compute, fill in `compute_estimate_method` and `compute_confidence`; say how you got the number in `compute_notes`.
4. Run `python scripts/validate.py` (no installs needed), then open a pull request. CI runs the same check.

Correcting an Epoch-imported row? Email data@epoch.ai too, since re-imports overwrite Epoch rows (except `architecture`, `eci`, `notes`).
On merge to `main`, the data is published to Hugging Face automatically.
