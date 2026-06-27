# Task

Review Task 4 of the UI-CACHE-API phase: API-Football-only key loading and refresh readiness gate.

Claude should review only and must not write code. Please check secret safety, readiness correctness, no-real-refresh behavior, and merge safety.

# Changed files

- `app.py`
- `scripts/write_refresh_status_dry_run.py`
- `reports/samples/ui_refresh_status.sample.json`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`
- `reports/claude_reviews/round_13_review_packet.md`

# Product code impact

- `app.py` was touched only inside the existing Data Freshness / Refresh Status panel support.
- The panel shows API-Football key present/missing, controlled refresh readiness, Odds API disabled, and real API refresh performed = No.
- API-Football key values are never displayed.
- The Odds API is not required for the current phase.
- Polymarket remains public-only and was not expanded.
- WorldCup2026 schedule remains a public cache source.
- No recommendation, ranking, portfolio, strategy, odds calculation, settlement, or backtest behavior was changed.

# Protected files

- Protected modules were not modified.
- Protected data files were not modified.
- Golden JSON fixtures were not modified.
- Runtime status output remains ignored under `.runtime/`.
- Local environment files remain ignored and are not committed.

# Validation

Planned and local validation for this packet:

- `python3 scripts/write_refresh_status_dry_run.py` run twice: pass.
- Repeated dry-run writes only ignored `.runtime/ui_refresh_status.json`: pass.
- `API_FOOTBALL_KEY`: present in local config, value redacted.
- `THE_ODDS_API_KEY`: not required for Task 4.
- Real API refresh: not performed.
- `python3 -m py_compile app.py`: pass.
- `python3 -m py_compile scripts/write_refresh_status_dry_run.py`: pass.
- `python3 scripts/validate_claude_review_packet.py reports/claude_reviews/round_13_review_packet.md`: pass.
- Packet budget guard: pass, estimated `$0.006817`.
- `git diff --check`: pass.
- Protected-path diff check: pass, no protected diffs.
- Secret-shaped token scan on changed files: pass, no matches.

# Secret scan

- No secret values are intentionally included.
- Environment and local config values are checked only by presence.
- Local environment files are ignored and not staged.

# Gate status

- PORTFOLIO_EXTRACTION: BLOCKED.
- BACKTEST_READY: NO.
- API provider policy: `api_football_only`.
- Real API refresh for this task: not performed.
- External network calls for this task: not added.
- API quota protection: preserved by dry-run/readiness-only status generation.

# Proposed next task

If Claude finds no material issue, Task 5 can be a controlled one-time API-Football refresh design or implementation gate that is bounded, logged, and explicitly user-approved before any real API call.

# Questions for Claude

- Is the API-Football key value protected from printing and commits?
- Does `.env` remain ignored?
- Is the Odds API correctly disabled and not required for this phase?
- Does missing `THE_ODDS_API_KEY` avoid blocking API-Football readiness?
- Does the UI avoid implying any real refresh occurred?
- Does repeated dry-run execution avoid tracked-file churn?
- Is this a good foundation for a later controlled one-time API-Football refresh?
