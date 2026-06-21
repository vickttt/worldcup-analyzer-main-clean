# QA Report

## 2026-06-21 Governance Setup

## Scope

- Created governance and automation documentation only.
- No business logic, recommendation logic, data refresh logic, or UI files should be changed.

## Checks

- Git status checked before setup.
- Current branch confirmed as `main`.
- Working tree confirmed clean before setup.
- Recent 10 commits recorded in `PROJECT_SETUP_REPORT.md`.

## Result

- Passed. Governance files were created and Git status shows only documentation additions:
  - `AGENTS.md`
  - `PROJECT_SETUP_REPORT.md`
  - `docs/`

## 2026-06-21 WorldCup Supervisor Design

## Scope

- Designed WorldCup Supervisor as a project-manager agent.
- Added `WORLDCUP_SUPERVISOR_PLAN.md`.
- Updated `docs/CHANGELOG.md` for the documentation change.
- No business code, data scripts, recommendation logic, or UI files should be changed.

## Checks

- Required governance documents were read before design.
- Current branch observed as `dev`.
- Supervisor rules explicitly forbid branch creation, Git commits, pushes, app runs, API refreshes, and business-code changes.

## Result

- Passed. Final Git status shows only documentation changes:
  - `WORLDCUP_SUPERVISOR_PLAN.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 WorldCup Supervisor Responsibility Refinement

## Scope

- Refined `WORLDCUP_SUPERVISOR_PLAN.md` to match the requested WorldCup Supervisor responsibilities exactly.
- Updated `docs/CHANGELOG.md`.
- No business code, branch operation, Git commit, push, app run, or automation was performed.

## Checks

- Confirmed current branch is `dev`.
- Confirmed the plan targets `docs/DAILY_REPORT.md`.
- Confirmed Supervisor design includes checks for `main`, stale changelog, uncommitted changes, and next-step recommendations.

## Result

- Passed. Final Git status shows only documentation changes:
  - `WORLDCUP_SUPERVISOR_PLAN.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 WorldCup Supervisor Run

## Scope

- Ran one WorldCup Supervisor governance check.
- Regenerated `docs/DAILY_REPORT.md`.
- Updated `docs/CHANGELOG.md` for the report generation.
- No business code, branch operation, Git commit, push, app run, API refresh, or product automation was performed.

## Checks

- Read `AGENTS.md`.
- Read `docs/GPT_CONTEXT.md`.
- Read `docs/TASK_QUEUE.md`.
- Read `docs/KNOWN_BUGS.md`.
- Read `docs/CHANGELOG.md`.
- Read `docs/QA_REPORT.md`.
- Confirmed current branch is `dev`.
- Confirmed current uncommitted changes are documentation-only.

## Result

- Passed. Final Git status shows only documentation changes:
  - `WORLDCUP_SUPERVISOR_PLAN.md`
  - `docs/CHANGELOG.md`
  - `docs/DAILY_REPORT.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 Recommendation Auditor Design

## Scope

- Designed Recommendation Auditor as a recommendation-logic audit agent.
- Added `RECOMMENDATION_AUDITOR_PLAN.md`.
- Updated `docs/CHANGELOG.md`.
- No business code, branch operation, Git commit, push, app run, API refresh, or product automation was performed.

## Checks

- Read `AGENTS.md`.
- Read `docs/GPT_CONTEXT.md`.
- Read `docs/PRODUCT_PRINCIPLES.md`.
- Read `docs/TASK_QUEUE.md`.
- Read `docs/KNOWN_BUGS.md`.
- Read `WORLDCUP_SUPERVISOR_PLAN.md`.
- Confirmed current branch is `dev`.
- Confirmed the auditor design forbids business-code edits, branch operations, Git operations, app runs, and API refreshes.

## Result

- Passed. Final Git status shows only documentation changes:
  - `RECOMMENDATION_AUDITOR_PLAN.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 Scenario Engine v1 Design

## Scope

- Designed Scenario Engine v1 as the scenario-first recommendation layer.
- Added `SCENARIO_ENGINE_V1_PLAN.md`.
- Updated `docs/CHANGELOG.md`.
- No business code, branch operation, Git commit, push, app run, API refresh, or product automation was performed.

## Checks

- Read `AGENTS.md`.
- Read `docs/PRODUCT_PRINCIPLES.md`.
- Read `docs/TASK_QUEUE.md`.
- Read `docs/KNOWN_BUGS.md`.
- Read `RECOMMENDATION_AUDITOR_PLAN.md`.
- Read `WORLDCUP_SUPERVISOR_PLAN.md`.
- Confirmed Scenario Engine v1 design defines Main, Secondary, and Upset scenarios.
- Confirmed Scenario Consistency Score is defined from 0 to 100.
- Confirmed the design forbids business-code edits, branch operations, Git operations, app runs, and API refreshes.

## Result

- Passed. Final Git status shows only documentation changes:
  - `RECOMMENDATION_AUDITOR_PLAN.md`
  - `SCENARIO_ENGINE_V1_PLAN.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 Scenario Engine Prototype v0.1

## Scope

- Generated a complete Scenario Engine prototype report for Germany vs Ivory Coast.
- Used existing local data only.
- Added `SCENARIO_ENGINE_PROTOTYPE_REPORT.md`.
- Updated `docs/CHANGELOG.md`.
- No business code, recommendation logic, branch operation, Git commit, push, app run, API refresh, or product automation was performed.

## Checks

- Read `SCENARIO_ENGINE_V1_PLAN.md`.
- Read `RECOMMENDATION_AUDITOR_PLAN.md`.
- Inspected existing local data for `2026_06_20_Germany_Ivory_Coast`.
- Used saved pre-match snapshots, odds, and fixture data.
- Confirmed the report includes Main Scenario, Secondary Scenario, Upset Scenario, Asset Mapping, and Scenario Consistency Score.

## Result

- Passed. Final Git status shows only documentation changes:
  - `RECOMMENDATION_AUDITOR_PLAN.md`
  - `SCENARIO_ENGINE_PROTOTYPE_REPORT.md`
  - `SCENARIO_ENGINE_V1_PLAN.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 Scenario Engine Read-Only Automation Plan

## Scope

- Designed the read-only automation plan for repeatable Scenario Engine reporting.
- Added `SCENARIO_ENGINE_AUTOMATION_PLAN.md`.
- Updated `docs/CHANGELOG.md`.
- No implementation code was written.
- No business code, UI, recommendation logic, Portfolio Ranking logic, data file, branch operation, Git commit, push, app run, API refresh, or product automation was performed.

## Checks

- Read `SCENARIO_ENGINE_V1_PLAN.md`.
- Read `SCENARIO_ENGINE_PROTOTYPE_REPORT.md`.
- Read `RECOMMENDATION_AUDITOR_PLAN.md`.
- Confirmed automation is specified as read-only.
- Confirmed allowed output is limited to report files.
- Confirmed missing-field degraded mode is defined.
- Confirmed Recommendation Auditor handoff and future Portfolio Ranking fields are defined.

## Result

- Passed. Final Git status shows only documentation changes:
  - `SCENARIO_ENGINE_AUTOMATION_PLAN.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 Scenario Engine Read-Only Script v0.1

## Scope

- Implemented `scripts/generate_scenario_engine_report.py`.
- Ran the script once.
- Generated `SCENARIO_ENGINE_REPORT.md`.
- Updated `docs/CHANGELOG.md`.
- No business code, UI, recommendation logic, Portfolio Ranking logic, data file, branch operation, Git commit, push, API refresh, or Streamlit app run was performed.

## Checks

- Confirmed current branch is `dev`.
- Confirmed the working tree was clean before implementation.
- Confirmed the script reads only local saved files for Germany vs Ivory Coast.
- Confirmed the script restricts v0.1 output to `SCENARIO_ENGINE_REPORT.md`.
- Confirmed report includes Match, Source Snapshot Summary, Main Scenario, Secondary Scenario, Upset Scenario, Asset Mapping, Scenario Consistency Score, Score Breakdown, Recommendation Auditor Handoff, Portfolio Ranking Implication, and Automation Verdict.

## Result

- Passed. Final Git status shows only the read-only script, generated report, and governance documentation changes:
  - `scripts/generate_scenario_engine_report.py`
  - `SCENARIO_ENGINE_REPORT.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 Scenario Engine Asset Mapping Correction

## Scope

- Corrected Scenario Engine read-only script asset mapping for high-score correct-score bets.
- Regenerated `SCENARIO_ENGINE_REPORT.md`.
- Updated `docs/CHANGELOG.md`.
- No business code, UI, recommendation logic, Portfolio Ranking logic, data file, branch operation, Git commit, push, API refresh, or Streamlit app run was performed.

## Checks

- Confirmed `2:0`, `3:0`, and `3:1` remain Main Scenario Return Assets.
- Confirmed `4:0`, `4:1`, and `4:2` are marked as Aggressive Return Asset / Tail Upside.
- Confirmed `5:0`, `5:1`, `5:2`, and `5:3` are marked as Tail Asset / Extreme Upside.
- Confirmed new Scenario Consistency Score is 82 / 100.
- Confirmed high-score correct scores no longer act as core Main Scenario evidence.

## Result

- Passed. Final Git status shows only the allowed script, generated report, and governance documentation changes:
  - `scripts/generate_scenario_engine_report.py`
  - `SCENARIO_ENGINE_REPORT.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 Recommendation Auditor v0.1 Run

## Scope

- Ran Recommendation Auditor v0.1 as a read-only report review.
- Generated `docs/RECOMMENDATION_AUDIT_REPORT.md`.
- Updated `docs/CHANGELOG.md`.
- No business code, UI, recommendation logic, Portfolio Ranking logic, data file, branch operation, Git commit, push, API refresh, or Streamlit app run was performed.

## Checks

- Read `SCENARIO_ENGINE_REPORT.md`.
- Read `RECOMMENDATION_AUDITOR_PLAN.md`.
- Read `SCENARIO_ENGINE_V1_PLAN.md`.
- Read `docs/PRODUCT_PRINCIPLES.md`.
- Read `docs/KNOWN_BUGS.md`.
- Confirmed main recommendation is labeled as Germany handicap-cover path.
- Confirmed high-score correct scores are downgraded to aggressive upside or tail.
- Confirmed Scenario Consistency Score is 82 / 100.
- Confirmed no Critical or High path conflict was found.

## Result

- Passed. Final Git status shows only recommendation audit documentation and governance documentation changes:
  - `docs/RECOMMENDATION_AUDIT_REPORT.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 Portfolio Ranking 2.0 Design

## Scope

- Designed Portfolio Ranking 2.0.
- Added `PORTFOLIO_RANKING_V2_PLAN.md`.
- Updated `docs/CHANGELOG.md`.
- No business code, UI, recommendation logic, Portfolio Ranking logic, data file, branch operation, Git commit, push, API refresh, or Streamlit app run was performed.

## Checks

- Read `docs/RECOMMENDATION_AUDIT_REPORT.md`.
- Read `SCENARIO_ENGINE_REPORT.md`.
- Read `docs/PRODUCT_PRINCIPLES.md`.
- Confirmed the design uses Scenario Consistency Score, Asset Role Balance, Tail Exposure, User Decision Complexity, Main Scenario Coverage, and Secondary Insurance Coverage.
- Confirmed My Portfolio uses the same scoring framework as system portfolios.

## Result

- Passed. Final Git status shows only Portfolio Ranking design documentation and governance documentation changes:
  - `PORTFOLIO_RANKING_V2_PLAN.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 2026-06-21 Scenario Auditor Ranking Integration Plan

## Scope

- Designed Scenario Engine, Recommendation Auditor, and Portfolio Ranking 2.0 integration plan.
- Added `INTEGRATION_PLAN_V1.md`.
- Updated `docs/CHANGELOG.md`.
- No business code, UI, recommendation logic, Portfolio Ranking logic, data file, branch operation, Git commit, push, API refresh, or Streamlit app run was performed.

## Checks

- Inspected current `app.py` recommendation, role, optimizer, ranking, My Portfolio, snapshot, and UI entry points.
- Inspected current `scripts/` report/data-center script structure.
- Confirmed plan uses phased integration to avoid changing current recommendation behavior in Phase 1.
- Confirmed risk areas are identified before implementation.

## Result

- Passed. Final Git status shows only integration/ranking design documentation and governance documentation changes:
  - `INTEGRATION_PLAN_V1.md`
  - `PORTFOLIO_RANKING_V2_PLAN.md`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## Required QA For Future Development

- Every development task must update this file.
- Recommendation logic changes must include path consistency checks.
- Portfolio Ranking changes must verify scenario consistency and user decision efficiency.

## 2026-06-21 Shadow Metadata v0.1 Implementation

## Scope

- Implemented `attach_shadow_metadata(...)` as a metadata-only helper.
- Added a read-only validation report script.
- Generated `SHADOW_METADATA_REPORT.md`.
- No UI, Legacy Ranking sort, recommendation logic, `strategy_score(...)`, `evaluate_allocation(...)`, data file, branch operation, Git commit, push, API refresh, or Streamlit app run was performed.

## Checks

- Ran `python3 scripts/generate_shadow_metadata_report.py`.
- Ran `python3 -m py_compile modules/shadow_metadata.py scripts/generate_shadow_metadata_report.py`.
- Validated Germany vs Ivory Coast from `data/history/2026_06_20_Germany_Ivory_Coast_pre.json`.
- Validated Scotland vs Morocco from `data/history/2026_06_20_Scotland_Morocco_pre.json`.
- Validated Brazil vs Haiti from `data/history/2026_06_20_Brazil_Haiti_pre.json`.
- Confirmed every strategy in all three snapshots received `strategy["shadow"]`.
- Confirmed generated fields include `legacy_rank`, `legacy_score`, `scenario_rank`, `scenario_score`, `rank_difference`, `shadow_verdict`, and `scenario_rank_reason`.
- Confirmed report states Legacy order, Legacy score, recommendation logic, UI, and data files were not changed.

## Result

- Passed. Shadow Metadata v0.1 is available for report-only validation.

## 2026-06-21 Visible Shadow Mode MVP Implementation

## Scope

- Implemented the minimum Visible Shadow Mode display in Portfolio Ranking.
- Added only `Scenario Rank` and `Shadow Verdict` columns.
- The Portfolio Ranking table reads only `strategy.get("shadow") or {}` for Shadow fields.
- Missing Shadow metadata displays `-`.
- No Scenario Score, Tail Exposure, Rank Difference, Conflict Flags, or Scenario Rank Reason is displayed.
- No Legacy Ranking sort, default recommendation, score, recommendation logic, data file, branch operation, Git commit, push, API refresh, or Streamlit app run was performed.

## Checks

- Confirmed current branch is `dev`.
- Confirmed initial working tree only had the prior `VISIBLE_SHADOW_MODE_MVP_PLAN.md` documentation file.
- Confirmed the existing `comparison = sorted(... score ...)` Legacy Ranking sort remains unchanged.
- Confirmed `attach_shadow_metadata(...)` runs after Legacy Ranking sorting.
- Confirmed displayed Portfolio rows read only `strategy["shadow"]` fields for `Scenario Rank` and `Shadow Verdict`.
- Ran `python3 -m py_compile app.py modules/shadow_metadata.py`.

## Result

- Passed. Visible Shadow Mode MVP is implemented as display-only metadata and does not change ranking, recommendations, scores, or data files.

## 2026-06-21 Visible Shadow Mode MVP Display Refinement

## Scope

- Added one Portfolio Ranking caption: `Legacy 排名仍为正式排序；Scenario Rank 仅供观察，不影响推荐。`
- Localized `Shadow Verdict` display values:
  - `Agreement` -> `一致`
  - `Watch` -> `观察`
  - `Disagreement` -> `分歧`
  - `Blocker Candidate` -> `高风险观察`
- Kept the MVP display limited to `Scenario Rank` and `Shadow Verdict`.
- Did not display Scenario Score, Tail Exposure, Rank Difference, Conflict Flags, or Scenario Rank Reason.
- No Legacy Ranking sort, default recommendation, score, recommendation logic, `strategy_score(...)`, `evaluate_allocation(...)`, `strategy_comparison(...)`, data file, branch operation, Git commit, push, or API refresh was changed.

## Checks

- Confirmed Portfolio Ranking still sorts by Legacy `score` before Shadow metadata is attached.
- Confirmed `portfolio_ranking_rows(...)` still reads only `strategy.get("shadow") or {}` for Shadow fields.
- Confirmed missing Shadow verdict displays `-`.
- Ran `python3 -m py_compile app.py modules/shadow_metadata.py`.

## Result

- Passed. Visible Shadow Mode MVP display copy is refined without changing ranking, recommendations, scores, or data files.

## 2026-06-21 Portfolio Ranking Decision Table Slimming v0.1

## Scope

- Slimmed the default Portfolio Ranking table into a main decision table.
- Kept default visible columns:
  - `组合名称`
  - `Scenario Rank`
  - `Shadow Verdict`
  - `主剧本`
  - `EV`
  - `ROI`
  - `最大亏损`
  - `剧本一致性评分`
  - `综合评分`
- Removed from the main table:
  - `让球资产`
  - `大小球资产`
  - `波胆资产`
- Kept the caption: `Legacy 排名仍为正式排序；Scenario Rank 仅供观察，不影响推荐。`
- Did not modify the detail dialog.
- Did not add any new metric.
- Did not change Legacy Ranking sort, recommendation logic, default recommendation, score, `strategy_score(...)`, `evaluate_allocation(...)`, `strategy_comparison(...)`, or data files.

## Checks

- Confirmed `portfolio_ranking_rows(...)` no longer outputs the three asset-detail columns in the main table.
- Confirmed Portfolio Ranking still sorts by Legacy `score` before Shadow metadata is attached.
- Confirmed `render_portfolio_ranking(...)` still displays the observation-only caption above the table.
- Ran Python syntax compilation check for `app.py` and `modules/shadow_metadata.py` without writing bytecode caches.

## Result

- Passed. Portfolio Ranking main table is slimmer while preserving ranking, recommendations, scores, and data behavior.

## 2026-06-21 Post-Match Validation Automation v0.1

## Scope

- Added read-only post-match validation automation script:
  - `scripts/generate_post_match_validation_report.py`
- Generated:
  - `POST_MATCH_VALIDATION_REPORT.md`
- The script reads existing pre-match snapshots and post-match final scores.
- The script identifies:
  - Legacy Top Portfolio
  - Scenario Top Portfolio
  - Current Recommendation
  - My Portfolio when available
- The script calculates:
  - hit status
  - P/L
  - ROI
  - max drawdown
  - Legacy vs Scenario Winner
- The report includes the 5-Match Promotion Rule and Scenario Guardrails Phase conditions.
- Did not replace `strategy_score(...)`.
- Did not change sorting.
- Did not change recommendation logic.
- Did not change default recommendation.
- Did not modify historical data files.

## Checks

- Ran `python3 scripts/generate_post_match_validation_report.py`.
- Confirmed `POST_MATCH_VALIDATION_REPORT.md` was generated.
- Confirmed 2 post-match files were discovered.
- Confirmed 2 valid comparisons were generated.
- Confirmed current promotion status is `Keep Shadow Mode` because only 2 / 5 valid validations exist.
- Ran Python syntax compilation check for `scripts/generate_post_match_validation_report.py` and `modules/shadow_metadata.py` without writing bytecode caches.

## Result

- Passed. Post-match validation automation v0.1 is report-only and does not change ranking, recommendations, scores, UI, or data files.

## 2026-06-21 Connect My Portfolio To Post-Match Validation v0.1

## Scope

- Updated `scripts/generate_post_match_validation_report.py` to read standalone My Portfolio history files.
- The script now checks `data/history/my_portfolios/<match_slug>.json` first.
- If standalone My Portfolio data exists and has non-empty `items`, the report uses it.
- If standalone My Portfolio data is missing or empty, the script falls back to `pre_snapshot["my_portfolio"]`.
- Regenerated `POST_MATCH_VALIDATION_REPORT.md`.
- Did not modify historical data files.
- Did not change ranking, sorting, recommendation logic, score, UI, or `strategy_score(...)`.

## Checks

- Ran `python3 scripts/generate_post_match_validation_report.py`.
- Confirmed `POST_MATCH_VALIDATION_REPORT.md` includes My Portfolio rows.
- Confirmed Switzerland vs Bosnia and Herzegovina includes My Portfolio:
  - Hit: `miss`
  - P/L: `-1500`
  - ROI: `-100.0%`
  - Max Drawdown: `-1500`
- Confirmed United States vs Australia includes My Portfolio:
  - Hit: `hit`
  - P/L: `+858`
  - ROI: `57.2%`
  - Max Drawdown: `-0`
- Confirmed My Portfolio sources are listed from `data/history/my_portfolios/`.
- Ran Python syntax compilation check for `scripts/generate_post_match_validation_report.py` and `modules/shadow_metadata.py` without writing bytecode caches.

## Result

- Passed. My Portfolio is now connected to post-match validation through read-only standalone history files.
