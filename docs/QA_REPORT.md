# QA Report

## 2026-06-22 Agent Automation Context Layer v1

## Scope

- Added `WORLDCUP.md`.
- Added `SUPERVISOR.md`.
- Added `docs/TODAY_NEXT_ACTION.md`.
- Added `docs/SUBAGENTS.md`.
- Added `docs/HOOKS_GUARDRAILS_PLAN.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.
- Updated `docs/TASK_QUEUE.md`.

## Checks

- Confirmed this task is documentation-only.
- Confirmed no business code was intentionally modified.
- Confirmed `app.py` was not modified by this task.
- Confirmed no production sorting, recommendation logic, or ranking functions were modified.
- Confirmed no API refresh was run.
- Confirmed no `data/history` files were modified.
- Confirmed no PR, commit, or push was created.

## Result

- Passed. Agent Automation Context Layer v1 is ready as project context for future Supervisor and subagent workflows.
- The recommended next step is a First Real Issue -> Branch -> PR rehearsal.

## 2026-06-21 GitHub Agent Workflow Infrastructure v1

## Scope

- Added GitHub Issue template:
  - `.github/ISSUE_TEMPLATE/agent_task.md`
- Added Pull Request template:
  - `.github/pull_request_template.md`
- Added GitHub Actions QA workflow:
  - `.github/workflows/agent-qa.yml`
- Added agent workflow runbook:
  - `docs/AGENT_WORKFLOW_RUNBOOK.md`
- Updated `docs/CHANGELOG.md`, `docs/QA_REPORT.md`, and `docs/TASK_QUEUE.md`.
- Did not modify business code, ranking logic, recommendation logic, UI behavior, API refresh logic, or `data/history`.

## Checks

- Confirmed the workflow performs Python syntax checks for `app.py` and `scripts/*.py`.
- Confirmed ranking-sensitive function guardrails cover:
  - `strategy_score(...)`
  - `strategy_comparison(...)`
  - `evaluate_allocation(...)`
- Confirmed protected history data guardrails cover:
  - `data/history/*_pre.json`
  - `data/history/*_post.json`
  - `data/history/my_portfolios/*.json`
- Confirmed docs synchronization check requires `docs/CHANGELOG.md` and `docs/QA_REPORT.md` when `app.py` or `scripts/*.py` changes.
- Confirmed high-risk overrides require explicit PR body tokens:
  - `approved:ranking`
  - `approved:data-write`

## Result

- Passed as infrastructure setup. The files are ready for GitHub to execute once pushed to the repository.
- No local API calls, data writes, commits, or pushes were performed.

## 2026-06-21 Decision UI Fix v0.1

## Scope

- Updated `app.py` display layer only.
- Added Duplicate Portfolio Detection MVP after the existing Legacy score sort.
- Merged duplicate portfolios in the display when actual betting assets, selection/line, odds, amount, and asset role match.
- Removed the active Portfolio Ranking detail pop-up flow and replaced it with a centralized list of default-collapsed expanders below the main table.
- Expanded Match Betting Score explanation with:
  - positive reasons
  - negative reasons
  - final judgement
- Expanded Recommended Stake explanation with explicit 0 / 300 / 500 / 800 / 1200 / 1500 yuan amount rules.

## Checks

- Ran syntax check: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m py_compile app.py`.
- Confirmed Portfolio Ranking still sorts by original score:
  - `comparison = sorted(comparison, key=lambda item: item.get("score", 0), reverse=True)`
- Confirmed there is no active `st.dialog` / `render_strategy_detail_dialog(...)` Portfolio Ranking detail path.
- Confirmed `strategy_score(...)`, `evaluate_allocation(...)`, and `strategy_comparison(...)` definitions were not modified.
- Confirmed no data files were intentionally modified by this task.

## Result

- Passed. Decision UI Fix v0.1 improves duplicate handling and decision explanation without changing production ranking, recommendation logic, default recommendation, scores, or data files.

## 2026-06-21 Phase A Match Betting Score + Recommended Stake MVP

## Scope

- Updated `app.py` display layer only.
- Added `Match Summary` card above Portfolio Ranking.
- Added `Recommended Stake` card above Portfolio Ranking.
- Match Betting Score uses existing signals:
  - Scenario Consistency
  - Shadow Verdict
  - Sleeve Status
  - Max Loss
  - Legacy comprehensive score
- Recommended Stake maps Match Betting Score to a 0-2000 yuan display recommendation.
- Did not implement Duplicate Detection, Detail UI Redesign, or Asset Role Refactor.

## Checks

- Ran syntax check: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m py_compile app.py`.
- Confirmed Portfolio Ranking still sorts by original score:
  - `comparison = sorted(comparison, key=lambda item: item.get("score", 0), reverse=True)`
- Confirmed `strategy_score(...)`, `evaluate_allocation(...)`, and `strategy_comparison(...)` definitions were not modified.
- Confirmed no data files were intentionally modified by this task.

## Result

- Passed. The MVP adds two decision cards without changing sorting, recommendation logic, default recommendation, or existing score functions.

## 2026-06-21 Hybrid v0.2 Visible Diagnostic MVP

## Scope

- Updated `app.py` display layer only.
- Added Portfolio Ranking table columns:
  - `Sleeve %`
  - `Sleeve Status`
- Added Portfolio Ranking caption:
  - `Hybrid v0.2 仅为观察，不影响正式排序、默认推荐或评分。`
- Added `Hybrid v0.2 Diagnostic` section to the strategy detail dialog.
- The detail section shows Core Portfolio, Upside Sleeve, Sleeve %, Sleeve Status, and Sleeve Reason.
- Did not add Benchmark ROI, Legacy ROI, Core ROI, Core+Upside ROI, Hybrid Rank, or Core+Upside Rank.

## Checks

- Ran syntax check: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m py_compile app.py`.
- Confirmed `comparison = sorted(comparison, key=lambda item: item.get("score", 0), reverse=True)` remains unchanged.
- Confirmed `strategy_score(...)`, `evaluate_allocation(...)`, and `strategy_comparison(...)` definitions were not modified.
- Confirmed the new fields read display-only `strategy["hybrid_v2"]` metadata and fall back to `-` when missing.
- Confirmed no data files were intentionally modified by this task.

## Result

- Passed. Hybrid v0.2 Visible Diagnostic MVP is implemented as display-only metadata.
- Production ranking, recommendation logic, default recommendation, scores, and data files remain unchanged.

## 2026-06-21 Hybrid v0.2 Report-Only Implementation

## Scope

- Added `scripts/generate_hybrid_v2_report_only.py`.
- Generated `HYBRID_V2_REPORT_ONLY_REPORT.md`.
- Read existing `data/history/backfill/` snapshots only.
- Compared report-only Core, Core + Upside Sleeve, and Legacy Tail-Heavy structures.
- Updated this QA report and `docs/CHANGELOG.md`.
- Did not modify `app.py`, production sorting, recommendation logic, UI, score functions, or existing source data.

## Checks

- Ran syntax check: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m py_compile scripts/generate_hybrid_v2_report_only.py`.
- Ran report generation: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/generate_hybrid_v2_report_only.py`.
- Confirmed `HYBRID_V2_REPORT_ONLY_REPORT.md` was generated.
- Confirmed the script reads `data/history/backfill/` and writes only the report.
- Confirmed no production ranking or recommendation functions were modified.

## Result

- Matches evaluated: 10.
- Core ROI: 18.2%.
- Core + Upside ROI: 20.6%.
- Legacy Tail-Heavy ROI: 46.5%.
- Recommendation: `Enter Visible Diagnostic`.

## Verdict

- Passed. Hybrid v0.2 should remain report-only until a separate Visible Diagnostic task is approved.

## 2026-06-21 Phase B Historical Odds Backfill 10-Match Pilot

## Scope

- Added `scripts/generate_world_cup_backfill_benchmark.py`.
- Wrote 10 isolated backfill snapshots under `data/history/backfill/`.
- Generated `WORLD_CUP_BACKTEST_PORTFOLIOS.md`.
- Generated `WORLD_CUP_RANKING_BENCHMARK_REPORT.md`.
- Updated this QA report and `docs/CHANGELOG.md`.
- Did not modify `app.py`, production ranking, recommendation logic, UI, score functions, or original `data/history/` pre/post/my_portfolio files.

## Sample Matches

- France vs Senegal.
- Argentina vs Algeria.
- Portugal vs Congo DR.
- England vs Croatia.
- Canada vs Qatar.
- Scotland vs Morocco.
- Brazil vs Haiti.
- Netherlands vs Sweden.
- Germany vs Ivory Coast.
- Ecuador vs Curaçao.

## Checks

- Ran syntax check: `./.venv/bin/python -m py_compile scripts/generate_world_cup_backfill_benchmark.py`.
- Ran the pilot script with API-Football historical odds.
- Confirmed all 10 generated snapshots are marked `true_pre_match`.
- Confirmed all 10 matches include Match Winner, Asian Handicap, Over/Under, and Correct Score markets.
- Confirmed `odds_update_timestamp < kickoff_timestamp` for each market in each valid snapshot.
- Confirmed benchmark deduplicates by match and counts each sample once.

## Benchmark Result

- Valid matches: 10.
- Invalid odds matches: 0.
- Legacy Wins: 3.
- Scenario Wins: 0.
- Hybrid Wins: 0.
- Draws: 7.
- Legacy ROI: 46.5%.
- Scenario ROI: 18.2%.
- Hybrid ROI: 18.2%.
- Best system in this 10-match pilot: `Legacy`.

## Result

- Passed. Phase B confirms the historical odds backfill path is technically usable for true pre-match benchmark data.
- Phase C is recommended as a report-only full completed-match benchmark, but Hybrid should not be promoted from this pilot alone because Legacy outperformed in this 10-match sample.

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

## 2026-06-21 Result Update And Post-Match Validation

## Scope

- Added 12 post-match result files under `data/history/*_post.json`.
- Regenerated `POST_MATCH_VALIDATION_REPORT.md`.
- Added `VALIDATION_UPDATE_SUMMARY.md`.
- Added `SCENARIO_GUARDRAILS_REVIEW.md`.
- Did not modify code, ranking logic, recommendation logic, UI, or existing data logic.

## Validation Metrics

- Valid validations: 12.
- Legacy Wins: 3.
- Scenario Wins: 3.
- Draws: 6.
- Legacy ROI: -40.8%.
- Scenario ROI: -2.1%.
- Promotion Status: `Enter Scenario Guardrails Phase`.

## Checks

- Confirmed `POST_MATCH_VALIDATION_REPORT.md` was regenerated.
- Confirmed the validation count reached the 5-match promotion threshold.
- Confirmed this update does not change `strategy_score(...)`, `evaluate_allocation(...)`, `strategy_comparison(...)`, sorting logic, recommendation logic, score, or UI.

## Result

- Passed. The project should enter Scenario Guardrails review while keeping Legacy Ranking as the official production ranking for now.

## 2026-06-21 Hybrid Ranking Report v0.1

## Scope

- Added `scripts/generate_hybrid_ranking_report.py`.
- Generated `HYBRID_RANKING_REPORT.md`.
- The script reads saved `data/history/` snapshots.
- The script uses `attach_shadow_metadata(...)` in memory to derive Scenario Rank and Shadow Verdict.
- The script computes report-only `strategy["hybrid"]` metadata in memory.
- Did not modify production sorting, recommendation logic, UI, score functions, or data files.

## Checks

- Ran `./.venv/bin/python scripts/generate_hybrid_ranking_report.py`.
- Confirmed `HYBRID_RANKING_REPORT.md` was generated.
- Ran syntax check with `./.venv/bin/python -m py_compile scripts/generate_hybrid_ranking_report.py`.
- Confirmed no changes to `app.py`, `strategy_score(...)`, `evaluate_allocation(...)`, `strategy_comparison(...)`, Portfolio Ranking sorting, recommendation logic, UI, or data files.

## Result

- Passed. Hybrid Ranking v0.1 is report-only and ready for review before any UI or sorting migration.

## 2026-06-21 API-Football Historical Odds Check

## Scope

- Added `API_FOOTBALL_HISTORICAL_ODDS_CHECK.md`.
- Checked whether API-Football can support historical pre-match odds backfill.
- Confirmed required market IDs:
  - Match Winner: `1`
  - Asian Handicap: `4`
  - Goals Over/Under: `5`
  - Exact Score / Correct Score: `10`
- Did not write backfill code.
- Did not pull full historical data.
- Did not modify production ranking, recommendation logic, UI, app code, or existing data files.

## Checks

- Confirmed date-based API-Football odds queries can return World Cup 2026 odds rows for historical dates.
- Confirmed returned odds rows include an `update` timestamp that can be compared with kickoff time.
- Confirmed strict backtest eligibility requires `odds_timestamp < kickoff_time`.
- Confirmed current local fixture IDs are not reliable for direct historical odds lookup and need official API-Football fixture mapping.

## Result

- Passed with constraints. Historical odds backfill planning may proceed, but every backfilled snapshot must include `source`, `odds_timestamp`, `kickoff_time`, `is_true_pre_match`, and `data_quality`.

## 2026-06-21 Historical Odds Backfill + Ranking Benchmark Plan

## Scope

- Added `WORLD_CUP_HISTORICAL_ODDS_BACKFILL_PLAN.md`.
- Designed a safe historical odds backfill and ranking benchmark readiness plan.
- Defined isolated storage under `data/history/backfill/`.
- Defined required odds quality fields:
  - `odds_source`
  - `odds_update_timestamp`
  - `kickoff_timestamp`
  - `is_before_kickoff`
  - `data_quality`
- Defined benchmark outputs for Legacy Top, Scenario Top, and Hybrid Top.
- Did not write backfill code.
- Did not call full API pulls.
- Did not write backfill data.
- Did not modify production ranking, recommendation logic, UI, app code, or existing data files.

## Checks

- Confirmed plan requires `update < kickoff` before a snapshot can be used for strict historical backtest.
- Confirmed backfilled snapshots must be written only under `data/history/backfill/`.
- Confirmed existing `data/history/` pre/post/my_portfolio files must not be overwritten.
- Confirmed benchmark must deduplicate by match, not by snapshot count.
- Confirmed Phase A should start with 3 sample matches before any 10-match or full backfill.

## Result

- Passed. The project is ready for Phase A planning only: a 3-match historical odds quality check. Full backfill and benchmark implementation remain blocked until sample quality is verified.
