# Task Queue

## P0 Commit hygiene and governance sync

- Group current uncommitted files by theme before any further development.
- Keep performance logs out of normal feature commits.
- Keep historical `data/history/*_pre.json` and `data/history/my_portfolios/*.json` in separate data commits only when explicitly approved.
- Keep `docs/CHANGELOG.md`, `docs/QA_REPORT.md`, and `docs/DAILY_REPORT.md` synchronized with completed governance and validation work.
- Do not modify production ranking, recommendation logic, UI, or data refresh code during cleanup.

## P1 Historical odds backfill plan

- Use `API_FOOTBALL_HISTORICAL_ODDS_CHECK.md` as the capability baseline.
- Design a safe backfill pipeline that reads API-Football odds by official fixture/date, not by stale local fixture IDs.
- Store backfilled snapshots only in an isolated directory such as `data/history/backfill/`.
- Do not overwrite existing manual history snapshots.
- Require `odds_timestamp < kickoff_time` before marking a snapshot as true pre-match data.

## P2 Hybrid Ranking benchmark

- Continue Phase A report-only validation for Hybrid Ranking.
- Compare Legacy Top, Scenario Top, and Hybrid Top across historical snapshots.
- Use benchmark results before changing production sorting.
- Keep `strategy_score(...)`, `evaluate_allocation(...)`, and `strategy_comparison(...)` production behavior unchanged until an explicit implementation task is approved.

## P3 Scenario Guardrails UI / eligibility design

- Design how Scenario Guardrails should appear in the Portfolio Ranking UI.
- Keep Legacy ranking visible as reference during any transition.
- Add warnings for `Shadow Verdict = Disagreement`, tail-heavy portfolios, pure-tempo portfolios, and low-consistency portfolios.
- Do not promote Scenario or Hybrid signals into default recommendation eligibility without explicit review.
