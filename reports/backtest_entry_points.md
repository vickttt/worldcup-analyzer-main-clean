# Backtest Entry Points

This report identifies backtest and validation entry points without refactoring them.

## Historical Simulation Starts

- `scripts/backtest_portfolio_engine.py`
  - Reads `data/history/*_pre.json` and `data/history/*_post.json`.
  - Evaluates portfolio behavior across saved historical snapshots.
  - Generates backtest reports under `reports/backtests/`.
- `scripts/backtest_attribution.py`
  - Reads post-match history snapshots.
  - Produces attribution summaries for backtest outcomes.
- `scripts/generate_world_cup_backfill_benchmark.py`
  - Builds isolated backfill benchmark snapshots.
  - Contains a script-local `evaluate_strategy` for benchmark comparison.

## Evaluation Metrics Computed

- `scripts/backtest_portfolio_engine.py`
  - portfolio outcome summaries
  - hit/win/loss style metrics
  - generated markdown/csv reports
- `scripts/backtest_attribution.py`
  - attribution rows and aggregate backtest explanations
- `scripts/generate_post_match_validation_report.py`
  - Legacy vs Scenario validation comparisons
  - My Portfolio settlement when available
- `scripts/generate_hybrid_ranking_report.py`
  - Legacy Top vs Scenario Top vs Hybrid Top comparison from snapshots
- `scripts/generate_hybrid_v2_report_only.py`
  - report-only Hybrid v0.2 comparison

## Prediction vs Result Comparison

- `app.py`
  - `settle_items`
  - `settle_strategies`
  - `prediction_audit`
  - `recommendation_audit`
  - post-match snapshot save/load helpers
- `scripts/generate_post_match_validation_report.py`
  - reads post-match snapshots
  - settles or compares strategy outputs
- `scripts/backtest_portfolio_engine.py`
  - reads saved pre/post data and summarizes outcomes

## Backtest Isolation Risks

- Multiple scripts duplicate or partially mirror settlement/evaluation behavior.
- Some scripts import app-adjacent modules directly.
- Historical data files are protected and should remain read-only unless explicitly approved.
- Backtest output depends on snapshot schema produced by `app.py`.

## Recommendation

Backtest module split should wait until:

- portfolio output golden lock is committed
- settlement helpers are isolated behind stable contracts
- historical snapshot schema expectations are documented
