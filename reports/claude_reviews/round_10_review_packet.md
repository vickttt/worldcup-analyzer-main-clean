# Task

Review Task 3 runtime churn cleanup before merging the UI-CACHE-API refresh status branch.

Claude should review only and must not write code. Please check whether the branch is safe to merge after moving refresh-status runtime output away from tracked files.

# Changed files

- `.gitignore`
- `app.py`
- `scripts/write_refresh_status_dry_run.py`
- `reports/samples/ui_refresh_status.sample.json`
- `reports/ui_refresh_status.json` removed from tracking
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`
- `reports/claude_reviews/round_10_review_packet.md`

# Product code impact

- `app.py` still changes only the existing Data Freshness / Refresh Status panel.
- The panel now reads `.runtime/ui_refresh_status.json` first.
- If runtime status is absent, a tracked sample may be shown only as sample/unknown.
- The sample is not treated as real freshness evidence, and its timestamp is not displayed as a real status check.
- No recommendation, ranking, portfolio, strategy, odds, settlement, or backtest behavior was changed.

# Protected files

- Protected modules were not modified.
- Protected data files were not intentionally modified or staged.
- Golden JSON fixtures were not modified.
- Runtime status output is ignored under `.runtime/`.
- Generated match-history runtime byproducts were removed from the working tree and are not part of this packet.

# Validation

Planned and local validation for this packet:

- `python3 scripts/write_refresh_status_dry_run.py` run twice: pass.
- Repeated dry-run writes only ignored `.runtime/ui_refresh_status.json`: pass.
- Tracked status after repeated runs contains only intended code/docs/sample/deletion changes: pass.
- `python3 -m py_compile app.py`: pending at packet creation.
- `python3 -m py_compile scripts/write_refresh_status_dry_run.py`: pending at packet creation.
- `python3 scripts/validate_claude_review_packet.py reports/claude_reviews/round_10_review_packet.md`: pending at packet creation.
- `git diff --check`: pending at packet creation.
- Protected-path diff check: pending at packet creation.
- Secret-shaped token scan on changed files: pending at packet creation.

# Secret scan

- No secrets, tokens, or environment values are intentionally included.
- The implementation does not read or print local environment files.
- The runtime status report path is ignored and is not included in this packet.

# Gate status

- PORTFOLIO_EXTRACTION: BLOCKED.
- BACKTEST_READY: NO.
- Real API refresh for this cleanup: not performed.
- External network calls for this cleanup: not added.
- API quota protection: preserved by dry-run-only status generation.

# Proposed next task

If Claude finds no material issue, this branch should be safe to merge into `dev-clean` after normal local validation and user approval.

# Questions for Claude

- Is `.runtime/ui_refresh_status.json` correctly treated as ignored runtime output?
- Is the tracked sample stable and clearly sample-only?
- Does the app avoid treating the sample as real freshness evidence?
- Does repeated dry-run execution avoid dirtying tracked files?
- Is the branch safe to merge after this cleanup?
