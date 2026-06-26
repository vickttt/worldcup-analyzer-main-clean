# QA Report

## 2026-06-27 Phase 1-5 Checkpoint Commit

## Scope

- Added `reports/phase1_to_phase5_checkpoint_summary.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.
- Prepared accumulated Phase 1-5 refactor-preparation changes for checkpoint commit.

## Checks

- Confirmed current branch is `dev-clean`.
- Ran `git status`.
- Ran `python3 -m py_compile app.py modules/odds/core.py modules/strategy/core.py modules/portfolio/shadow.py`.
- Ran `git diff --check`.
- Reviewed `git diff -- app.py`.
- Ran `git diff -- modules/odds/core.py`.
- Ran `git diff -- modules/strategy/core.py`.
- Ran `git diff -- modules/portfolio/shadow.py`.
- Verified 23 moved odds/strategy functions match their `HEAD:app.py` source.
- Verified moved functions are not still defined in current `app.py`.
- Verified `modules.portfolio.shadow` is not imported by runtime code.
- Verified no `data/`, `data/history/`, or `data/worldcup2026/` files are modified.

## Result

- Passed checkpoint validation.
- Production behavior affected: No intended behavior change beyond pure move extraction already validated.
- Portfolio Score affected: No intended behavior change.
- `data/history` affected: No.
- Golden outputs affected: No.
- PORTFOLIO_EXTRACTION: BLOCKED.
- BACKTEST_READY: No.

## 2026-06-26 Risk Semantics Layer

## Scope

- Added `reports/risk_feature_extraction_v1.md`.
- Added `reports/risk_semantics_map.md`.
- Added `reports/risk_consistency_check.md`.
- Added `reports/risk_gap_analysis.md`.
- Added `reports/backtest_re_evaluation.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.

## Checks

- Extracted current risk semantics from `modules/strategy/core.py`, `app.py`, `modules/portfolio_engine.py`, `modules/portfolio/shadow.py`, and `reports/golden_output_snapshot_v2.json`.
- Mapped implicit risk fields including max loss, volatility, concentration, risk-control score component, portfolio score components, market disagreement, upset index, and decision stake.
- Confirmed no single canonical `risk_score` currently links strategy, portfolio, stake, allocation, and backtest behavior.
- Checked golden v2 consistency across score-to-stake, direction-confidence-to-stake, market-disagreement-to-stake, volatility, allocation, and rank-gate behavior.
- Classified risk semantics gap as `HIGH RISK GAP (BLOCKER)`.
- Kept backtest readiness conservative: `BACKTEST_READY: NO`.
- Ran `python3 -m py_compile app.py modules/portfolio/shadow.py modules/odds/core.py modules/strategy/core.py`.
- Ran `git diff --check`.

## Result

- Passed as read-only risk modeling and documentation.
- Production code behavior affected: No.
- Portfolio Score affected: No behavior change in this step.
- `data/history` affected: No writes.
- Golden outputs affected: No.
- Runtime shadow wiring affected: No.
- BACKTEST_READY: No.

## 2026-06-26 Golden Assertion Gate v1

## Scope

- Added `reports/portfolio_shadow_vs_production_diff.md`.
- Added `reports/golden_assertion_gate_v1.md`.
- Added `reports/portfolio_risk_final_gate.md`.
- Added `reports/backtest_final_gate_check.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.

## Checks

- Compared golden v2 saved production-reference output against shadow replay output for all five locked scenarios.
- Checked ranking order, stake allocation, portfolio selection, and available risk weighting fields.
- Confirmed all five golden v2 scenarios matched shadow replay on available saved fields with deviation score 100 / 100.
- Identified risk payload coverage gap: golden v2 does not include full `risk_gate` payloads for all strategy rows.
- Confirmed portfolio extraction remains blocked due to strategy scoring coupling, app/UI state coupling, implicit globals, and incomplete post-match/backtest coverage.
- Confirmed backtest is not ready to run independently of `app.py` and cannot use shadow portfolio only.
- Ran `python3 -m py_compile app.py modules/portfolio/shadow.py modules/odds/core.py modules/strategy/core.py`.
- Ran `git diff --check`.
- Confirmed no runtime import of `modules.portfolio.shadow` outside the shadow module itself.

## Result

- Golden assertion gate: PASS_WITH_COVERAGE_GAP.
- Portfolio extraction status: BLOCKED.
- BACKTEST_READY: No.
- Production code behavior affected: No.
- Portfolio Score affected: No behavior change in this step.
- `data/history` affected: No writes.
- Golden outputs affected: No.

## 2026-06-26 Portfolio Shadow System

## Scope

- Added `modules/portfolio/shadow.py`.
- Added `reports/portfolio_shadow_output_v1.md`.
- Added `reports/portfolio_shadow_deviation.md`.
- Added `reports/portfolio_shadow_coupling_map.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.

## Checks

- Created a read-only shadow module that mirrors current stake sizing, strategy scoring, ranking key, strategy item allocation, correct-score floor, and correlation-weighting rules for observation.
- Confirmed the shadow module is not imported by `app.py`.
- Confirmed no runtime wiring was added.
- Generated shadow output reports from `reports/golden_output_snapshot_v2.json`.
- Compared saved top strategy stake, positive combo stake, decision stake, and shadow replay allocation across all five golden v2 scenarios.
- Identified hidden coupling around strategy score fields, implicit amount normalization, odds-derived value fields, and UI orchestration.
- Ran `python3 -m py_compile modules/portfolio/shadow.py app.py modules/odds/core.py modules/strategy/core.py`.
- Did not modify golden output snapshots.
- Did not write `data/history` or `data/worldcup2026`.

## Result

- Passed as non-intrusive shadow/observation layer.
- Production code behavior affected: No.
- Portfolio Score affected: No behavior change in this step.
- `data/history` affected: Read only through existing golden v2 report input; no data files were written.
- Runtime import of shadow module: No.
- Portfolio extraction status: Still blocked until a diff-based golden assertion gate exists.

## 2026-06-26 Golden Output Expansion v2

## Scope

- Added `reports/golden_dataset_v2_manifest.md`.
- Added `reports/golden_output_snapshot_v2.json`.
- Added `reports/golden_consistency_check.md`.
- Added `reports/portfolio_exposure_pre_map.md`.
- Added `reports/backtest_expansion_readiness.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.

## Checks

- Selected five existing saved pre-match snapshots from `data/history/` for multi-scenario coverage.
- Covered high actual-odds mismatch, balanced market, low-exposure favorite, upset-prone favorite/handicap tension, and incomplete odds scenarios.
- Serialized existing saved output fields only: odds output, actual odds, probability distribution, strategy snapshot, recommendation combo, portfolio selection, and final decision.
- Confirmed the v2 snapshot was generated without recomputing ranking, allocation, odds, strategy, or portfolio logic.
- Created cross-scenario consistency notes for ranking stability, strategy score variance, portfolio allocation drift, and odds-vs-strategy disagreement.
- Created a portfolio exposure pre-map for allocation size, stake scaling, risk adjustment, constraints, caps, clamps, and high-risk coupling points.
- Marked backtest expansion as not ready until a diff-based golden assertion gate exists.
- Ran `python3 -m py_compile app.py modules/odds/core.py modules/strategy/core.py`.
- Ran `git diff --check`.

## Result

- Passed as multi-scenario behavior-lock documentation and saved-output serialization.
- Portfolio Score affected: No behavior change in this step.
- `data/history` affected: Read only; no data files were written.
- Business logic affected: No.
- Ranking/order logic affected: No.
- READY_FOR_BACKTEST_EXPANSION: No.

## 2026-06-26 Golden Output Lock

## Scope

- Added `reports/golden_output_functions.md`.
- Added `reports/golden_output_snapshot_v1.json`.
- Added `reports/portfolio_dependency_trace.md`.
- Added `reports/backtest_entry_points.md`.
- Added `reports/extraction_readiness_gate.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.

## Checks

- Identified golden output functions for ranking, scoring, allocation, recommendation ordering, summary generation, and backtest behavior.
- Serialized an existing saved pre-match snapshot from `data/history/2026_06_19_Turkey_Paraguay_pre.json` into `reports/golden_output_snapshot_v1.json`.
- Confirmed the golden snapshot was generated without recomputing portfolio or ranking logic.
- Traced portfolio dependencies across `app.py`, `modules.strategy.core`, `modules.odds.core`, `modules.user_odds`, and `modules.portfolio_engine`.
- Identified backtest and validation entry points.
- Created extraction readiness gate and marked portfolio/backtest extraction as not ready.
- Ran `python3 -m py_compile app.py modules/odds/core.py modules/strategy/core.py`.
- Did not refactor portfolio logic, move backtest logic, optimize scoring, change ranking order, or write data files.

## Result

- Passed as behavior-lock documentation and snapshot generation.
- Portfolio Score affected: No new behavior change in this step.
- `data/history` affected: No writes; one existing pre-match snapshot was read.
- READY FOR PORTFOLIO EXTRACTION: No.
- READY FOR BACKTEST MODULE SPLIT: No.

## 2026-06-26 Phase 1 Stabilization and Coupling Control

## Scope

- Added `reports/phase1_module_isolation_audit.md`.
- Added `reports/post_extraction_dependency_graph.md`.
- Added `reports/app_responsibility_shrink_report.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.
- Did not modify runtime code during this stabilization step.

## Checks

- Audited `modules/odds/core.py` dependencies and hidden state.
- Audited `modules/strategy/core.py` dependencies and hidden state.
- Confirmed odds module does not import strategy module.
- Confirmed strategy module does not import odds module.
- Confirmed neither extracted module imports `app.py`.
- Confirmed neither extracted module imports Streamlit directly.
- Generated post-extraction dependency graph.
- Evaluated `app.py` responsibility shrink after Phase 1.
- Ran `python3 -m py_compile app.py modules/odds/core.py modules/strategy/core.py`.
- Ran `git diff --check`.

## Result

- Passed as stabilization/report-only hardening.
- Circular imports introduced: No direct circular imports detected.
- Portfolio Score affected: No new behavior change in this step.
- `data/history` affected: No.
- READY FOR PORTFOLIO EXTRACTION: No.
- READY FOR BACKTEST MODULE SPLIT: No.

## 2026-06-26 Phase 1 Odds and Strategy Extraction

## Scope

- Added `modules/odds/core.py`.
- Added `modules/strategy/core.py`.
- Updated `app.py` imports and removed moved function definitions from `app.py`.
- Updated `reports/module_mapping_v1.md`.
- Updated `reports/dependency_snapshot.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.

## Moved Function Groups

- Odds:
  - `fmt_odds`
  - `market_odds_overview_rows`
  - `actual_odds_completeness`
  - `actual_odds_completeness_for_match`
  - `parse_handicap_selection`
  - `parse_total_selection`
  - `winner_outcome`
  - `handicap_outcome`
  - `handicap_profit_value`
  - `total_outcome`
  - `correct_score_outcome`
- Strategy:
  - `clamp`
  - `round_to_hundred`
  - `confidence_reason`
  - `market_disagreement_reason`
  - `shadow_verdict_label`
  - `hybrid_v2_status_label`
  - `match_betting_score`
  - `recommended_stake_mvp`
  - `item_path_consistency`
  - `strategy_path_consistency`
  - `strategy_score`
  - `rank_key_with_eligibility`

## Checks

- Ran `python3 -m py_compile app.py`.
- Ran `python3 -m py_compile modules/odds/core.py`.
- Ran `python3 -m py_compile modules/strategy/core.py`.
- Verified moved function source matches `HEAD:app.py` for 23 moved functions.
- Confirmed `modules.strategy.core` imports successfully in the current environment.
- Attempted lightweight runtime dependency check; current system Python is missing `streamlit`, so app startup/import was not run.
- Confirmed no data files were modified.

## Result

- Passed as pure move refactor preparation.
- Portfolio Score affected: No intended behavior change; `strategy_score` source was moved unchanged.
- `data/history` affected: No.
- App startup check: Skipped because runtime dependency `streamlit` is not installed in the current system Python environment.

## 2026-06-26 Module Architecture Skeleton and Mapping

## Scope

- Added package boundary placeholders:
  - `modules/analysis/__init__.py`
  - `modules/odds/__init__.py`
  - `modules/portfolio/__init__.py`
  - `modules/strategy/__init__.py`
  - `modules/backtest/__init__.py`
  - `modules/data/__init__.py`
  - `modules/ui/__init__.py`
- Added `reports/module_mapping_v1.md`.
- Added `reports/entry_points.md`.
- Added `reports/dependency_snapshot.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.

## Checks

- Confirmed current branch is `dev-clean`.
- Confirmed worktree was clean before edits.
- Scanned Python files under `app.py`, `modules/`, `scripts/`, and `test_api.py`.
- Built a logical mapping without moving source files.
- Identified current entry points without changing runtime behavior.
- Generated a lightweight static import snapshot.
- Confirmed no direct circular imports among current `modules/*.py` files by static import inspection.
- Did not edit existing business logic, formulas, algorithms, recommendation logic, Portfolio Score logic, data files, or existing function bodies.
- Ran `git diff --check`.
- Ran Python syntax check for the new package boundary `__init__.py` files.
- Ran `git status`.
- Attempted `tree -L 3`; command was unavailable in this environment.
- Used `find . -maxdepth 3 -type d` as the directory structure fallback.

## Result

- Passed as structural preparation.
- Portfolio Score affected: No.
- `data/history` affected: No.
- `tree` affected: Not run because the command is not installed.

## 2026-06-26 Git Sync Check

## Scope

- Added `docs/GIT_SYNC_CHECK_REPORT.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.
- Did not modify `app.py`, `modules/`, `data/`, or `reports/`.

## Checks

- Ran `git status`.
- Confirmed current branch is `dev-clean`.
- Confirmed working tree was clean before this documentation update.
- Ran `git pull origin dev-clean`.
- Confirmed remote branch was already up to date.
- Reviewed `docs/CHANGELOG.md`.
- Confirmed latest changelog records include the 2026-06-26 merge precheck and automation migration plan entries.

## Result

- Passed. Repository sync check completed.
- Portfolio Score affected: No.
- `data/history` affected: No.

## 2026-06-26 Merge Precheck and Automation Migration Plan

## Scope

- Added `docs/MERGE_PRECHECK_REPORT.md`.
- Added `docs/AUTOMATION_MIGRATION_PLAN.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.
- Did not modify `app.py`, `modules/`, `data/`, or `reports/`.

## Checks

- Confirmed current branch is `dev-clean`.
- Confirmed working tree was clean before this documentation update.
- Confirmed PR #7 is merged into `main`.
- Fetched `origin` and confirmed `origin/main` points to merge commit `792003f`.
- Fast-forwarded local `dev-clean` to `origin/main`.
- Pushed synchronized `dev-clean` to `origin/dev-clean`.
- Updated `main-clean-local` to track latest `origin/main`.
- Reviewed `docs/DEVELOPMENT_WORKFLOW.md`, `docs/CHANGELOG.md`, and `docs/QA_REPORT.md`.
- Confirmed next automation work is planned as documentation/workflow-only and must not modify business logic or data.
- Ran `git diff --check`.
- Confirmed changed files are limited to `docs/AUTOMATION_MIGRATION_PLAN.md`, `docs/MERGE_PRECHECK_REPORT.md`, `docs/CHANGELOG.md`, and `docs/QA_REPORT.md`.

## Result

- Passed. Merge precheck and next automation plan are documentation-only.
- Portfolio Score affected: No.
- `data/history` affected: No.

## 2026-06-26 Development Workflow Rules

## Scope

- Updated `docs/DEVELOPMENT_WORKFLOW.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.
- Did not modify `app.py`, `modules/`, `data/`, or `reports/`.

## Checks

- Confirmed the current branch is `dev-clean`.
- Confirmed this task is documentation-only.
- Confirmed workflow rules cover `main`, `dev-clean`, and `feature/*` branches.
- Confirmed large feature work requires a dedicated `feature/*` branch or worktree before merging through `dev-clean`.
- Confirmed the old `worldcup-analyzer` directory is marked as an archive and not a development target.
- Confirmed Codex task rules require allowed files and forbidden files to be declared.
- Confirmed every completed modification must update `docs/CHANGELOG.md` and `docs/QA_REPORT.md`.
- Confirmed UI, model, odds, backtest, and data/API tasks are separated.
- Confirmed `main` is PR-only and CI is required before merge.
- Confirmed Claude Review and Agent QA are auxiliary, not required gates.
- Confirmed API keys, `.env` values, tokens, passwords, and secrets are forbidden in code and Markdown.
- Confirmed `.env` and `.env.*` are ignored by `.gitignore`.
- Confirmed completion reports must state modified files, test/check results, Portfolio Score impact, `data/history` impact, protected data touches, and skipped checks.
- Confirmed `docs/PR_CREATION_REPORT.md` records current branch, PR target, involved files, QA status, high-risk actions avoided, and next steps.
- Ran `git diff --check`.
- Ran Python syntax check with system `python3 -B -m py_compile` for `app.py` and `scripts/*.py`.
- Created PR #7 from `dev-clean` to `main` and left it unmerged for user review.

## Result

- Passed. Documentation-only governance update.
- Portfolio Score affected: No.
- `data/history` affected: No.
- `.venv/bin/python` was not present, so the Python syntax check used the available system `python3`.
- PR status: Created, pending GitHub review and merge.

## 2026-06-22 Automation Status Report and Supervisor Issue Draft

## Scope

- Added `AUTOMATION_STATUS_REPORT.md`.
- Added `docs/NEXT_ISSUE_DRAFT.md`.
- Updated `docs/CHANGELOG.md`.
- Updated `docs/QA_REPORT.md`.
- Created a GitHub Issue for the automation hardening workflow.

## Checks

- Confirmed this task is documentation-only.
- Confirmed `data/performance_logs/app_performance.jsonl` remains unstaged and must not be committed.
- Confirmed no business code was intentionally modified.
- Confirmed `app.py`, `scripts/`, `modules/`, and `data/history/` were not modified by this task.
- Confirmed no production sorting, recommendation logic, or ranking functions were modified.
- Confirmed no API refresh was run.

## Result

- Passed. This task is safe to submit as a documentation-only Agent workflow PR.

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
