# Round 1 Sanitized Review Packet

## Task

Build a read-only review packet structure and secret safety validator for GitHub-mediated Claude review.

## Changed files

- `scripts/validate_claude_review_packet.py`
- `reports/claude_reviews/packet_validation_report.md`
- `reports/claude_reviews/round_1_review_packet.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`

## Product code impact

Product code modified: no.
Ranking, recommendation, odds, strategy, portfolio, data refresh, and backtest logic modified: no.

## Protected files

Protected files are expected to remain untouched:

- `app.py`
- `modules/`
- `data/`
- `reports/golden_output_snapshot_v1.json`
- `reports/golden_output_snapshot_v2.json`
- `reports/golden_risk_contract_v1.json`

## Validation

Local validation planned for this round:

- Run packet validator against this packet.
- Compile the packet validator with Python.
- Run whitespace diff check.
- Run protected-file diff checks.
- Run repository secret scan excluding ignored local environment files.

## Secret scan

No API keys, local environment file contents, GitHub tokens, Anthropic tokens, raw git diffs, full golden JSON, full application files, full module files, or data history content are intentionally included in this packet.

## Gate status

- PORTFOLIO_EXTRACTION: BLOCKED
- BACKTEST_READY: NO

## Proposed next task

Ask Claude to review whether the new packet validator and this sanitized review packet are safe enough for GitHub-mediated review, then recommend exactly one next Codex task.
