# AI Progress Open Dataset

An open, community-contributed dataset of AI models for estimating software ("algorithmic") progress, hosted on Hugging Face.

## Status

v0 scaffold (2026-10-23): schema, validator, Epoch importers, CI, and HF publishing are in place. `data/` has headers only until the first import.

```
data/models.csv, data/evals.csv   the dataset (see SCHEMA.md)
scripts/schema.py                 column definitions (source of truth)
scripts/validate.py               checks every PR (stdlib only)
scripts/import_epoch_models.py    seeds models.csv from Epoch AI
scripts/import_epoch_benchmarks.py  seeds evals.csv (needs a one-time --inspect)
scripts/push_to_hf.py             publishes to Hugging Face (CI, on merge)
hf/README.md                      Hugging Face dataset card
```

Design: language and all other domains; two linked tables; ECI as the LM capability headline, plus raw benchmarks; GitHub PRs → CI validation → Hugging Face.

## Origin note

> "ok well lets make an open source / contribution thing of this data on huggingface ... right? does tha texist?"

Margin note, NYU AI Safety Association reading, week of Oct 2026.

## Passage it responds to

Ho says software-progress estimates are uncertain mainly because there isn't enough high-quality data. Each model in the dataset needs three things (p. 9, highlighted):

1. A training compute estimate.
2. A measure of its "capabilities".
3. A description of when it was released.

He notes that training compute is often unknown and that long-running capability metrics are hard to find, because benchmarks saturate quickly.

## Open questions

- [x] Does this already exist (on Hugging Face or elsewhere)? Partly. See "Existing data" below (checked 2026-10-23).
- [ ] Email data@epoch.ai to ask whether an HF mirror or join is welcome.
- [ ] Decide on a capability measure that doesn't saturate (ECI? a long-running benchmark?).

## Existing data (research, 2026-10-23)

- **Epoch AI "AI Models" database.** More than 2,000 models with training compute, as a daily-updated CSV (`epoch.ai/data/all_ai_models.csv`) under CC-BY. You can suggest additions by emailing data@epoch.ai, but there is no open contribution pipeline. https://epoch.ai/data/epochdb/documentation
- **Epoch Benchmarking Hub.** Benchmark results from Epoch and external sources, plus the Epoch Capabilities Index (ECI). Also CC-BY, but external results keep their original licenses. https://epoch.ai/benchmarks/about
- **Hugging Face.** A search of HF datasets for "epoch" and "training-compute" found no mirror of Epoch's model/compute data. The nearest thing is the retired Open LLM Leaderboard's per-model eval dumps (`open-llm-leaderboard-old/*`), which have scores but no compute.

**Gap this project could fill:** an HF dataset joining compute + release date (Epoch AI Models) with a non-saturating capability measure (Benchmarking Hub / ECI), open to community PRs.

## Citation

Ho, Anson. "The Least Understood Driver of AI Progress: An Opinionated Guide to 'Algorithmic Progress' and Why It Matters." *Gradient Updates*, Epoch AI. https://epoch.ai/gradient-updates/the-least-understood-driver-of-ai-progress
