# Commit Plan

Date: 2026-06-21

Scope: commit hygiene and governance sync only. This plan does not stage, commit, push, modify business code, change ranking, change recommendation logic, refresh API data, or delete files.

## Current Branch

- Branch: `dev`

## Working Tree Groups

## Group 1: Hybrid Ranking Report v0.1

Recommended commit together:

- `scripts/generate_hybrid_ranking_report.py`
- `HYBRID_RANKING_REPORT.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`

Reason:

- This is one self-contained report-only validation unit.
- The script computes Hybrid Ranking metadata in memory and does not alter production sorting, recommendation logic, UI, or data files.

Suggested commit message:

```text
Add hybrid ranking report generator
```

Notes:

- Include `docs/CHANGELOG.md` and `docs/QA_REPORT.md` only if this commit is intended to include the Hybrid Ranking Report v0.1 documentation updates.
- If `docs/CHANGELOG.md` and `docs/QA_REPORT.md` also include API-Football Historical Odds Check updates, either keep them in a combined governance/report commit or split the docs carefully before staging.

## Group 2: API-Football Historical Odds Check

Recommended commit together:

- `API_FOOTBALL_HISTORICAL_ODDS_CHECK.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`

Reason:

- This is a capability-check artifact for future historical odds backfill.
- It does not include backfill code or data pulls.

Suggested commit message:

```text
Document API-Football historical odds capability
```

Notes:

- This commit should not include `data/` files.
- This commit should not include `scripts/generate_hybrid_ranking_report.py` unless intentionally combining report work with capability-check work.

## Group 3: Governance Sync

Recommended commit together:

- `docs/TASK_QUEUE.md`
- `docs/DAILY_REPORT.md`
- `COMMIT_PLAN.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`

Reason:

- These files describe current project governance state, current task queue, and commit hygiene plan.
- They are not business code and do not alter runtime behavior.

Suggested commit message:

```text
Sync governance docs and commit plan
```

Notes:

- If `docs/CHANGELOG.md` and `docs/QA_REPORT.md` are already committed with Groups 1 or 2, avoid restaging unrelated changes from those files unless the diff is reviewed.

## Group 4: Operational / Product / Validation Design Docs

Recommended as one or more separate design-doc commits:

- `HYBRID_RANKING_REPLACEMENT_PLAN.md`
- `MY_PORTFOLIO_VALIDATION_CHECK.md`
- `OPERATIONAL_DASHBOARD_V1.md`
- `OPERATIONAL_WORKFLOW_V1.md`
- `POST_MATCH_VALIDATION_V1.md`
- `PRODUCT_REVIEW_V1.md`

Suggested commit message options:

```text
Add operational and product review docs
```

or split:

```text
Add hybrid ranking replacement plan
Add operational workflow and dashboard docs
Add post-match validation framework docs
```

Notes:

- These are design and review artifacts.
- Do not mix these with data commits or performance logs.

## Group 5: data/history pre and My Portfolio historical data

Current untracked historical data files:

- `data/history/2026_06_20_Ecuador_Cura_ao_pre.json`
- `data/history/2026_06_20_Tunisia_Japan_pre.json`
- `data/history/2026_06_21_Belgium_Iran_pre.json`
- `data/history/2026_06_21_Ecuador_Cura_ao_pre.json`
- `data/history/2026_06_21_New_Zealand_Egypt_pre.json`
- `data/history/2026_06_21_Spain_Saudi_Arabia_pre.json`
- `data/history/2026_06_21_Tunisia_Japan_pre.json`
- `data/history/my_portfolios/2026_06_20_Ecuador_Cura_ao.json`
- `data/history/my_portfolios/2026_06_20_Tunisia_Japan.json`
- `data/history/my_portfolios/2026_06_21_Belgium_Iran.json`
- `data/history/my_portfolios/2026_06_21_Ecuador_Cura_ao.json`
- `data/history/my_portfolios/2026_06_21_Spain_Saudi_Arabia.json`
- `data/history/my_portfolios/2026_06_21_Tunisia_Japan.json`

Recommended action:

- Do not include these in documentation or script commits.
- Commit only after explicit user approval that these snapshots should become project history.

Suggested commit message if approved:

```text
Add saved pre-match and portfolio history snapshots
```

Notes:

- These files affect historical validation inputs.
- They should be reviewed for source, timestamp, and match identity before committing.

## Group 6: Do Not Commit

Do not commit:

- `data/performance_logs/app_performance.jsonl`

Reason:

- Runtime/performance log noise.
- Not part of governance, validation, ranking, or historical snapshot source of truth.

Suggested action:

- Leave unstaged.
- Consider adding a future `.gitignore` rule only if approved in a separate cleanup task.

## Recommended Commit Order

1. Governance sync:

```text
Sync governance docs and commit plan
```

2. Hybrid report:

```text
Add hybrid ranking report generator
```

3. API-Football capability check:

```text
Document API-Football historical odds capability
```

4. Design docs:

```text
Add operational and product review docs
```

5. Historical data snapshots, only if explicitly approved:

```text
Add saved pre-match and portfolio history snapshots
```

## Safety Confirmation

- Business code changes planned for commit: No.
- Ranking logic changes planned for commit: No.
- Recommendation logic changes planned for commit: No.
- UI changes planned for commit: No.
- API refresh or data pull performed by this task: No.
- Git commit performed: No.
- Git push performed: No.

