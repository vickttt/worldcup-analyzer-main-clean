# Scenario Engine Read-Only Script v0.1 Readiness Report

## Summary

The project is ready to implement a read-only Scenario Engine script v0.1, provided the first implementation remains report-only and does not modify business logic, UI, Portfolio Ranking, recommendation logic, or data files.

Recommended next implementation target:

- A read-only script under `scripts/`.
- Input: existing local snapshots.
- Output: a Markdown report such as `SCENARIO_ENGINE_REPORT.md`.
- No API refresh, no app run, no Git operation.

## 1. Branch Check

- Current branch: `dev`
- Result: Pass

The current branch is suitable for implementing a read-only script after the current documentation changes are reviewed and committed.

## 2. Uncommitted Changes Check

- Uncommitted changes exist: Yes
- Current uncommitted files:
  - `SCENARIO_ENGINE_AUTOMATION_PLAN.md`
  - `SCENARIO_ENGINE_SCRIPT_READINESS_REPORT.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

Result: Pass with caution

The working tree is not clean. The current changes are documentation-only, but they should be reviewed and committed before starting script implementation to keep the implementation diff clean.

## 3. Business Code Change Check

- Business code changed: No
- Data files changed: No
- UI files changed: No
- Recommendation logic changed: No

Result: Pass

Current uncommitted changes do not include `app.py`, `modules/`, `scripts/`, `data/`, UI files, or recommendation logic files.

## 4. Existing Script / Report Directories

Existing relevant directories:

- `scripts/`
- `docs/`
- `outputs/reports/`

Existing script examples:

- `scripts/build_worldcup_data_center.py`
- `scripts/build_worldcup_index.py`
- `scripts/performance_report.py`
- `scripts/refresh_api_data.py`
- `scripts/refresh_match_prematch_snapshot.py`
- `scripts/refresh_today_odds.py`
- `scripts/update_gpt_context.py`

Result: Pass

Recommendation:

- Place the future read-only implementation in `scripts/`, for example `scripts/generate_scenario_engine_report.py`.
- Write report output to the project root as `SCENARIO_ENGINE_REPORT.md` for v0.1, matching the automation plan.
- Later match-specific reports can move under `docs/scenario_reports/` or `outputs/reports/` after the naming policy is finalized.

## 5. Germany vs Ivory Coast Data File Check

Required local files:

- `data/history/2026_06_20_Germany_Ivory_Coast_pre.json`: exists
- `data/worldcup2026/2026_06_20_Germany_Ivory_Coast/pre_match.json`: exists
- `data/worldcup2026/2026_06_20_Germany_Ivory_Coast/odds.json`: exists
- `data/worldcup2026/2026_06_20_Germany_Ivory_Coast/fixture.json`: exists

Result: Pass

## 6. Field Structure Readiness

## Match

Available fields:

- `fixture.json.match`
- `fixture.json.schedule_fixture`
- `pre_match.json.match`
- `data/history/..._pre.json.match`
- `data/history/..._pre.json.fixture`

Can generate: Yes

The script can produce match name, teams, competition, group, venue, kickoff, and source from existing fixture and snapshot fields.

## Source Snapshot Summary

Available fields:

- `data/history/..._pre.json.decision.final_recommendation`
- `data/history/..._pre.json.decision.final_confidence_score`
- `data/history/..._pre.json.decision.value_rating`
- `data/history/..._pre.json.decision.participation_advice`
- `data/history/..._pre.json.decision.recommended_stake`
- `data/history/..._pre.json.decision.market_disagreement`
- `data/history/..._pre.json.decision.upset_index`
- `odds.json.effective_winner_totals`
- `pre_match.json.probability_distribution`
- `pre_match.json.top_probable_outcomes`

Can generate: Yes

The script can summarize current recommendation, confidence, value rating, market probabilities, handicap, total line, and path distribution.

## Main Scenario

Available fields:

- `pre_match.json.probability_distribution.main_path`
- `pre_match.json.probability_distribution.boundary_path`
- `pre_match.json.probability_distribution.rows`
- `pre_match.json.portfolios`
- `data/history/..._pre.json.recommendation_combo`
- `data/history/..._pre.json.decision.final_recommendation`
- `odds.json.effective_winner_totals.asian_handicap`
- `odds.json.effective_winner_totals.implied_probabilities`

Can generate: Yes

The script can infer the main scenario from the final recommendation, handicap line, probability rows, recommended portfolio, and correct score candidates.

## Secondary Scenario

Available fields:

- `pre_match.json.probability_distribution.rows`
- `pre_match.json.risk_paths`
- `data/history/..._pre.json.recommendation_combo`
- Non-recommended correct score rows inside `recommendation_combo`
- `odds.json.effective_winner_totals`

Can generate: Yes

The script can infer secondary paths such as favorite small win, favorite win without handicap cover, lower-tempo score path, or insurance path.

## Upset Scenario

Available fields:

- `pre_match.json.probability_distribution.rows`
- `pre_match.json.probability_distribution.risk_exposure`
- `pre_match.json.risk_paths`
- `data/history/..._pre.json.decision.upset_index`
- Non-recommended draw/underdog score candidates in `recommendation_combo`

Can generate: Yes

The script can infer draw zone, underdog unbeaten, and upset/tail paths.

## Asset Mapping

Available fields:

- `pre_match.json.asset_roles`
- `pre_match.json.portfolios`
- `data/history/..._pre.json.recommendation_combo`
- `data/history/..._pre.json.strategy_snapshot.strategy_table`
- Existing item fields: `type`, `selection`, `name`, `probability`, `standard_odds`, `score`, `share`, `amount`, `path_consistency_score`, `path_conflict_penalty`, `path_consistency_reason`, `not_recommended_reason`

Can generate: Yes

The script can map:

- Winner and handicap assets to Direction Asset.
- Totals to Tempo Asset.
- Main-path correct scores to Return Asset.
- Small-win or lower-tempo protection to Insurance Asset.
- Draw, underdog, and extreme-score paths to Tail Asset.

## Scenario Consistency Score

Available fields:

- `pre_match.json.probability_distribution`
- `pre_match.json.risk_paths`
- `pre_match.json.asset_roles`
- `pre_match.json.portfolios`
- `data/history/..._pre.json.recommendation_combo`
- Existing `path_consistency_score`
- Existing `path_conflict_penalty`
- Existing `path_consistency_reason`
- Existing `direction_alignment_score`
- Existing `strategy_snapshot.strategy_table` fields such as path consistency, direction consistency, EV, ROI, Sharpe

Can generate: Yes

The script can compute the 0-100 prototype score with a component breakdown. It should start with deterministic rules from `SCENARIO_ENGINE_AUTOMATION_PLAN.md` rather than changing any existing ranking logic.

## 7. Required / Optional / Degraded Data Judgment

## Required Fields Present

- Match identity: present
- Recommendation snapshot: present
- Recommendation or portfolio items: present
- Market type / asset type: present
- Selection name: present

Result: Pass

## Strongly Preferred Fields Present

- `probability_distribution`: present
- `risk_paths`: present
- `asset_roles`: present
- `portfolios`: present
- `recommendation_combo`: present
- `strategy_snapshot.strategy_table`: present
- `decision.final_recommendation`: present
- Winner probability: present
- Handicap line: present
- Total line: present
- Correct score candidates: present
- Existing path consistency fields: present

Result: Pass

## Optional Fields

Several optional files exist in the match folder, including lineups, injuries, players, team stats, match stats, events, and post-match data. They are not required for script v0.1.

Result: Pass

## 8. Implementation Readiness Verdict

Status: Ready with one process caution.

The codebase has enough saved local data to implement Scenario Engine Read-Only Script v0.1. The future script can generate all requested report sections:

- Match
- Source Snapshot Summary
- Main Scenario
- Secondary Scenario
- Upset Scenario
- Asset Mapping
- Scenario Consistency Score

Process caution:

- The working tree currently has uncommitted documentation changes. Commit or intentionally carry those docs before starting script implementation, otherwise the implementation diff will mix planning docs with executable code.

## 9. Implementation Recommendation

Recommended first script behavior:

- Read only local files.
- Accept a match slug or default to `2026_06_20_Germany_Ivory_Coast`.
- Load the historical pre-match snapshot first.
- Load `pre_match.json`, `odds.json`, and `fixture.json` as supporting sources.
- Generate `SCENARIO_ENGINE_REPORT.md`.
- Print a short summary to terminal.
- Never write to `data/`.
- Never refresh API.
- Never import or run Streamlit.
- Never mutate recommendation, ranking, or UI files.

Recommended implementation location:

- `scripts/generate_scenario_engine_report.py`

Recommended first report output:

- `SCENARIO_ENGINE_REPORT.md`

Recommended safety check before implementation:

- Confirm Git status is clean or documentation-only.
- Confirm branch is `dev`.
- Confirm script writes only the report output.

## 10. Prohibited Actions For Implementation

The future script must not:

- Modify `app.py`.
- Modify UI files.
- Modify recommendation logic.
- Modify Portfolio Ranking logic.
- Modify any files under `data/`.
- Refresh API.
- Run the app.
- Create branches.
- Commit Git changes.
- Push to GitHub.
- Delete files.
