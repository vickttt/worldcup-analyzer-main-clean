# Round 4 Review Packet

## Task

Create a report-only source availability matrix for mapped risk contract source keys across existing golden risk contracts.

## Changed files

- `scripts/validate_source_availability.py`
- `reports/risk_contract_source_availability_matrix.md`
- `reports/claude_reviews/round_4_review_packet.md`
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

- `python3 scripts/validate_source_availability.py`: pass.
- `python3 -m py_compile scripts/validate_source_availability.py`: pass.
- `python3 -m py_compile scripts/validate_claude_review_packet.py`: pass.
- `git diff --check`: pass.
- Protected-file diff checks will be run before commit.
- Packet validation will be run before commit.

## Secret scan

Fast staged-diff secret check will be run before commit. No secrets are intentionally included.

## Gate status

- PORTFOLIO_EXTRACTION: BLOCKED
- BACKTEST_READY: NO

## Matrix summary

The source availability matrix checks existing `risk_contract_v1` fixture fields only. It does not replay live functions or write golden data. Current coverage confirms that several mapped fields remain unavailable or unknown in the existing contracts, so extraction and backtest gates remain closed.

## Proposed next task

Create a report-only field readiness classification that groups unavailable fields into: available from existing serialized contract, requires read-only live-function replay, requires approved new formula, or requires settled post-match design.
