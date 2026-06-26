# Round 7 Review Packet

## Task

Review the Claude packet budget guard implementation for cost-control correctness, safety, and scope compliance.

Claude should review only and must not write code.

## Changed files

- `scripts/validate_claude_review_packet.py`
- `reports/claude_reviews/round_7_review_packet.md`
- `reports/claude_reviews/packet_validation_report.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`

## Product code impact

Product code modified: no.
Runtime logic, ranking, recommendation, odds, strategy, portfolio, cache, API refresh, data refresh, and backtest logic modified: no.

## Protected files

Protected files untouched:

- `app.py`
- `modules`
- `data`
- `reports/golden_output_snapshot_v1.json`
- `reports/golden_output_snapshot_v2.json`
- `reports/golden_risk_contract_v1.json`

## Validation

- `python3 -m py_compile scripts/validate_claude_review_packet.py`: pass.
- `python3 scripts/validate_claude_review_packet.py reports/claude_reviews/round_7_review_packet.md`: pass.
- `git diff --check`: pass.
- Protected-file diff check for `app.py`, `modules`, `data`, and golden JSON: pass, no output.
- Quick changed-file token-pattern scan: pass.

## Secret scan

No secrets are intentionally included. The implementation uses public pricing assumptions and environment variable names only. It does not print API keys, token values, local environment files, or GitHub secret values.

## Gate status

- PORTFOLIO_EXTRACTION: BLOCKED
- BACKTEST_READY: NO

## Budget guard summary

The validator now estimates packet input tokens using a conservative byte/character count divided by 4, assumes 1200 expected output tokens by default, uses Haiku pricing by default, and fails validation when estimated cost exceeds the per-round threshold unless an explicit approved override is set.

Cost policy is included in the validation report:

- $0.20 is the per-round guardrail.
- $20 is the total planning budget, not a per-round threshold.
- Haiku is default for docs/report packet review.
- Sonnet is reserved for product-code or high-risk API/cache/security review.
- Later rounds should send only incremental diff or a short previous findings checklist.

## Proposed next task

After this budget guard is reviewed and accepted, use it as the default packet validation step before any GitHub-mediated Claude review. Do not start product-code implementation from this task.
