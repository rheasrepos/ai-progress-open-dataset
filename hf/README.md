---
license: cc-by-4.0
pretty_name: AI Progress Open Dataset
tags: [ai-progress, scaling, compute, benchmarks, algorithmic-progress]
configs:
  - config_name: models
    data_files: data/models.csv
  - config_name: evals
    data_files: data/evals.csv
---
# AI Progress Open Dataset

An open, community-contributed dataset for estimating software ("algorithmic") progress in AI: training compute, release dates, and capability measures for AI models across domains.

- `models`: one row per model (compute with its estimation method and confidence, parameters, data size, architecture, weights, ECI).
- `evals`: one row per model × benchmark score.

Schema and contribution guide: see the GitHub repo (SCHEMA.md, CONTRIBUTING.md). Edits go through GitHub pull requests; this dataset is synced from there.

## Attribution

Seeded from Epoch AI's [AI Models](https://epoch.ai/data/ai-models) and [Benchmarking Hub](https://epoch.ai/benchmarks) data, CC-BY 4.0. Cite Epoch AI when using imported rows (`origin = epoch`). Benchmark results from external sources keep their original licenses.
