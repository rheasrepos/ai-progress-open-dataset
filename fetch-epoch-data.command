#!/bin/bash
# Double-click to download Epoch AI's raw data into raw/ (not committed).
cd "$(dirname "$0")" && mkdir -p raw
curl -fL -o raw/all_ai_models.csv https://epoch.ai/data/all_ai_models.csv && \
curl -fL -o raw/benchmark_data.zip https://epoch.ai/data/benchmark_data.zip && \
echo && echo "Done. You can close this window." || echo "Download failed (see above)."
