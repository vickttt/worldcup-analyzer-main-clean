# Extraction Readiness Gate

This report decides whether portfolio and backtest extraction can proceed after the golden-output lock.

## Inputs Reviewed

- `reports/golden_output_functions.md`
- `reports/golden_output_snapshot_v1.json`
- `reports/portfolio_dependency_trace.md`
- `reports/backtest_entry_points.md`
- `reports/phase1_module_isolation_audit.md`
- `reports/app_responsibility_shrink_report.md`

## Portfolio Extraction

- Status: NOT READY.
- Coupling score: High.
- Golden output stability: Partial.
- Dependency entanglement: High.

Justification:

- A golden snapshot now exists, but it is one saved pre-match fixture and does not yet cover enough representative portfolio paths.
- `app.py` still owns `evaluate_allocation`, `evaluate_strategy`, `strategy_comparison`, portfolio row builders, and UI rendering.
- `modules/odds/core.py` still depends on `modules.portfolio_engine` through handicap helpers.
- `strategy_score` and `rank_key_with_eligibility` are extracted, but their upstream data contracts are implicit.

Required before readiness:

- Add at least one golden-output comparison script or documented manual check for `strategy_comparison`.
- Add representative snapshots for:
  - a low-score/risk-blocked match
  - a match with correct-score exposure
  - a match with My Portfolio input
- Lock expected strategy order, score values, and selected bets.

## Backtest Extraction

- Status: NOT READY.
- Coupling score: High.
- Golden output stability: Partial.
- Dependency entanglement: High.

Justification:

- Backtest scripts rely on saved snapshot schemas and settlement logic that still live partly in `app.py`.
- Multiple scripts duplicate validation or settlement behavior.
- Post-match audit outputs are not yet covered by a golden snapshot.

Required before readiness:

- Document post-match snapshot schema.
- Add a golden post-match audit snapshot.
- Decide whether settlement helpers move to `modules/backtest` or `modules/portfolio` first.

## Final Gate Decision

- READY FOR PORTFOLIO EXTRACTION: NO.
- READY FOR BACKTEST MODULE SPLIT: NO.

Next safe action:

- Create golden-output comparison tests using the snapshot file before moving more logic.
