# Backtest Expansion Readiness

This report evaluates whether the expanded golden output coverage is sufficient to begin backtest isolation. It is analysis-only.

## Current Golden Coverage

- v1 coverage: one saved pre-match snapshot.
- v2 coverage: five saved pre-match snapshots across high actual-odds divergence, balanced market, low-exposure favorite, upset-prone favorite/handicap tension, and incomplete odds.
- The v2 snapshot serializes existing odds, strategy ranking, recommendation combo, portfolio selection, and final decision outputs.
- No production scoring, ranking, allocation, odds, or strategy code was changed to create the snapshot.

## Sufficiency Assessment

The coverage is sufficient for a human-readable behavioral freeze, but not sufficient for backtest expansion or portfolio/backtest extraction.

Reasons:

- There is no automated assertion harness comparing future outputs against `reports/golden_output_snapshot_v2.json`.
- The current lock is pre-match only; backtest behavior also depends on post-match settlement, final score parsing, ROI, and audit summaries.
- Some scenarios rely on incomplete odds, which is valuable for coverage but not enough to validate settlement and benchmark paths.
- Portfolio allocation functions remain embedded in `app.py` and are still tightly coupled to `modules.portfolio_engine`.
- Ranking and allocation use implicit dictionary schemas that need explicit fixtures before backtest isolation.

## Missing Scenarios

- post-match settlement golden outputs for the same v2 matches where post files exist.
- My Portfolio settlement cases from `data/history/my_portfolios/`.
- full backfill benchmark fixture covering `data/history/backfill/` true pre-match odds.
- exact score heavy portfolio with high correct-score exposure.
- duplicate portfolio display merge case.
- loss-making top recommendation and draw/push Asian handicap settlement case.

## Readiness Decision

READY_FOR_BACKTEST_EXPANSION: NO

Backtest expansion should wait until a small golden assertion script exists and compares saved v2 outputs against regenerated outputs in a controlled, no-data-write mode.

## Allowed Next Step

Create a read-only golden assertion plan or script that loads fixed fixtures and reports diffs only. Do not move portfolio/backtest logic until that diff gate exists and passes.
