# Related work: a meta-analysis

Surveyed 2026-10-23 and 2026-11-13. The question: does an open, contributable dataset that joins
**training compute**, **release date**, and **capability** already exist? Each source below is scored
on the same dimensions, so the gaps are comparable.

## Sources

| Source | Unit | Compute? | Capability? | Contribution model | Access / license | Status |
|---|---|---|---|---|---|---|
| [Epoch AI, AI Models](https://epoch.ai/data/epochdb/documentation) | model (3,600+) | yes, with method + confidence + bounds | no (separate hub) | email data@epoch.ai | CSV, CC-BY | active, updated daily |
| [Epoch AI, Benchmarking Hub](https://epoch.ai/benchmarks/about) | model × benchmark (~45 benchmarks) + ECI | partial (copied per row) | yes, incl. ECI | none public | zip, CC-BY (external results keep their own license) | active |
| [Papers with Code](https://www.codesota.com/papers-with-code/shutdown) | paper × task × dataset × metric (SOTA tables) | no | yes, very broad (all of ML) | was open editing | — | **shut down by Meta, July 2025** |
| [PwC archive on Hugging Face](https://huggingface.co/pwc-archive) (`evaluation-tables`) | task → dataset → SOTA rows with metrics and code links | no | yes, frozen at 2025 | none (archive) | parquet, CC-BY-SA 4.0 | frozen |
| PwC revival (Niels Rogge, [AI Weekly](https://aiweekly.co/alerts/hugging-face-revives-paperswithcode-benchmark-tracker)) | SOTA tracking + paper-to-code | unknown | yes | unknown | unknown | announced, no release date; personal project |
| Open LLM Leaderboard (Hugging Face) | model × eval run | no | yes, LMs only | submit a model to be evaluated | HF datasets (`open-llm-leaderboard-old/*`) | retired |

## What the comparison shows

1. **Compute and capability live in different places.** Epoch has the best compute data, but its
   capability data is a separate download with no shared model key. That's why 737 benchmark rows
   didn't match a model in our import.
2. **Nothing compute-aware is open to contributions.** Every source with compute data is
   curated by one team. Papers with Code was the one big open-contribution leaderboard, and it had no compute.
3. **Open-contribution leaderboards die when one sponsor leaves.** PwC depended on Meta. This is an argument for
   keeping the source of truth in plain CSVs on GitHub, mirrored to HF, rather than in a hosted app.
4. **Compute uncertainty is underreported.** ~60% of Epoch's models have no estimation method recorded
   (from our import). Only Epoch records bounds at all.
5. **Benchmark saturation is handled by one composite.** ECI is the only non-saturating capability measure
   found, and it's language-only and Epoch-specific.

## Implications for this repo

- [ ] Import PwC `evaluation-tables` (CC-BY-SA) for pre-2025 benchmark history. Note: CC-BY-SA is share-alike, so
      either keep those rows in a separate file with their own license, or relicense evals as CC-BY-SA.
- [ ] Add a `model_aliases` table (alias → model_id) so Epoch hub names, PwC names, and HF ids all join.
      This targets the 737 unmatched rows.
- [ ] Keep the GitHub-CSV-first design (finding 3).
- [ ] Make "fill in a compute estimation method" a first contribution task (finding 4).

## Does anyone track whether a model is used? (surveyed 2026-11-16)

A second question, from a paper on a classifier that was published but never released: how much open AI goes
unused, and does any tracker record it? Full report and per-tool rows live in the companion repo:
[UNUSED_TOOLS_REPORT.md](https://github.com/rheasrepos/ai-fixable-problems-db/blob/main/UNUSED_TOOLS_REPORT.md)
and `data/tools.csv`.

| Tracker | Records | Deployment recorded? | License |
|---|---|---|---|
| [Epoch AI, AI Models](https://epoch.ai/data/ai-models-documentation/records) | 33 fields: bibliographic, compute, hardware, accessibility | no ("significant use" is only an inclusion criterion) | CC-BY |
| Hugging Face Hub API | downloads, likes, dates, tags, license (field list not verified) | no, downloads only | platform terms (not verified) |
| [PeaTMOSS](https://arxiv.org/pdf/2310.03620) | 281,638 model packages; 44,337 links to GitHub repos that use them | partly: public code reuse only | not stated |
| [OpenSSF Criticality Score](https://github.com/ossf/criticality_score) | 10 activity and dependency signals | no | Apache-2.0 |
| [OECD.AI catalogue of tools and metrics](https://oecd.ai/en/tools-faq) | tools by principle and purpose; drops tools stale for 2 years | partly: optional self-reported use cases | not stated |
| [SciCat](https://arxiv.org/pdf/2504.18971) | 18,247 scientific repos labelled active or inactive | no | not checked |

Measured base rates (all Hub repositories, mostly personal fine-tunes, so not a rate for public-interest tools):

- 71% of Hugging Face models and 70% of datasets had zero downloads; under 1% of models took 80% of
  downloads; 65% of models had no license (348,181 models, Oct 2023, [Osborne et al.](https://arxiv.org/html/2405.13058v1)).
- Roughly half of 2M+ models have under 200 lifetime downloads (Mar 2026,
  [Hugging Face](https://huggingface.co/blog/huggingface/state-of-os-hf-spring-2026)). A different metric from
  the 2023 one, so the two don't form a trend.
- Hub download counts include every GET and HEAD request, with no documented bot filtering
  ([HF docs](https://huggingface.co/docs/hub/models-download-stats)).
- About 64% of scientific repositories had no commit in 6 months by 2023 (derived from counts in
  [SciCat](https://arxiv.org/pdf/2504.18971)).

What it shows: **no tracker checked records deployment as a measured field.** Epoch's 33 fields have none.

- [ ] Decide whether `models.csv` gets openness, lineage (`base_model` exists), maintenance and use-status
      columns. Proposed values are in the companion repo's `SCHEMA.md` (tools table). They are a proposal:
      no source validates downloads or dependents against real deployment.
- [ ] Recompute the zero-download share from a current Hub snapshot (last measured Oct 2023).
- Do not use "87% of ML projects never reach production": no primary source was found.

## Not yet checked

LMArena, Artificial Analysis, OpenCompass, Stanford HELM, Stanford AI Index data, LifeArchitect's models table.
