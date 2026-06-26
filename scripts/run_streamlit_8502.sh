#!/bin/zsh
set -e

PROJECT_DIR="/Users/zijianchen/Documents/Codex/2026-06-14/1-vs-2-polymarket-3-4/worldcup-analyzer"
cd "$PROJECT_DIR"

source .venv/bin/activate
exec .venv/bin/streamlit run app.py \
  --server.port 8502 \
  --server.headless true \
  --browser.gatherUsageStats false
