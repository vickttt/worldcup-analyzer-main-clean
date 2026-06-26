# Round 3 Review Packet

## Task

Create a read-only field provenance map for missing `risk_contract_v1` fields.

## Changed files

- `reports/risk_contract_field_provenance_map.md`
- `scripts/validate_golden_risk_contract_v1.py`
- `reports/claude_reviews/round_3_review_packet.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`

## Product code impact

Product code modified: no.
Runtime logic, ranking, recommendation, odds, strategy, portfolio, data refresh, and backtest logic modified: no.

## Protected files

Protected files untouched:

- `app.py`
- `modules`
- `data`
- `reports/golden_output_snapshot_v1.json`
- `reports/golden_output_snapshot_v2.json`
- `reports/golden_risk_contract_v1.json`

## Validation

- `git diff --check`: pass.
- `python3 -m py_compile scripts/validate_golden_risk_contract_v1.py`: pass.
- `python3 -m py_compile scripts/validate_claude_review_packet.py`: pass.
- `python3 scripts/validate_golden_risk_contract_v1.py`: pass.
- Protected-file diff checks: no output.
- Packet validation will be run before commit.

## Secret scan

Fast staged-diff secret check will be run before commit. No secrets are intentionally included in the packet or report.

## Gate status

- PORTFOLIO_EXTRACTION: BLOCKED
- BACKTEST_READY: NO

## Provenance map summary

The new report maps missing risk contract fields to likely source functions and reports without implementing extraction. Key findings:

- `risk_gate.*` likely comes from `portfolio_risk_gate` and `rank1_eligibility_check`.
- `exposure_risk.correct_score_limit` likely comes from `correct_score_exposure_control`.
- scenario-risk internals likely come from `portfolio_risk_gate` calculations and returned gate fields.
- `canonical_risk_score` has no approved formula and should remain null.
- `post_match_risk_outcome` requires a future settled-contract design before backtest enablement.

## Proposed next task

Create a report-only source availability matrix for the mapped risk contract source keys across the existing golden fixtures, without writing golden JSON and without replaying portfolio logic.
