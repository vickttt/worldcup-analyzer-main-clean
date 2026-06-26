# Backtest Final Gate Check

This report answers whether backtest work can proceed independently after the shadow/golden assertion gate.

## Questions

### Can backtest run independently of app.py?

NO.

Reason: current backtest and validation behavior still depends on portfolio construction, settlement, score parsing, and output schemas that are embedded in `app.py` or share app-level contracts.

### Can backtest use shadow portfolio only?

NO.

Reason: `modules/portfolio/shadow.py` is an observation mirror. It does not own settlement, full strategy construction, score-grid generation, post-match comparison, or benchmark metrics.

### Are results reproducible from golden v2?

PARTIALLY.

Reason: golden v2 can reproduce saved pre-match ranking, selection, and allocation comparisons, but it cannot reproduce post-match settlement, ROI, final-score audits, or backfill benchmark results.

## Decision

BACKTEST_READY: NO

## Next Safe Step

Create a read-only post-match golden set and a no-data-write assertion runner before attempting backtest module split.