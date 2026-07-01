# Scenario → Auditor → Ranking Integration Plan v1

## Goal

Integrate Scenario Engine, Recommendation Auditor, and Portfolio Ranking 2.0 into the existing WorldCup Analyzer without breaking current recommendation logic, UI, data snapshots, or post-match audit flows.

This is a design plan only. It does not modify business code, recommendation logic, UI, Portfolio Ranking code, data files, branches, commits, API data, or app runtime.

## 1. Current System Architecture

## Data

Current data lives mainly in:

- `data/worldcup2026/<match_slug>/`
- `data/history/`
- `data/history/my_portfolios/`

Important existing files:

- `pre_match.json`
- `odds.json`
- `fixture.json`
- `post_match.json`
- `data/history/*_pre.json`
- `data/history/*_post.json`
- `data/history/my_portfolios/*.json`

Current snapshot creation path:

- `app.py` builds `snapshot_payload` in the match detail flow.
- `save_match_snapshot(...)` saves pre/post snapshots.
- `scripts/refresh_match_prematch_snapshot.py` and `scripts/build_worldcup_data_center.py` generate local data-center snapshots.

## Recommendation Logic

Current recommendation and candidate logic is mainly in:

- `app.py`
  - `recommendation_combo(...)`
  - `stake_amounts(...)`
  - `betting_asset_roles(...)`
  - `role_allocation_rows(...)`
  - `portfolio_style(...)`
  - `strategy_path_consistency(...)`
  - `strategy_comparison(...)`
  - `optimize_betting_portfolio(...)`
- `modules/user_odds.py`
  - `apply_path_consistency(...)`
  - `correct_score_path_consistency(...)`
  - market candidate construction and actual-odds enrichment

## Portfolio Ranking

Current Portfolio Ranking is mainly in:

- `app.py`
  - `evaluate_strategy(...)`
  - `evaluate_allocation(...)`
  - `strategy_score(...)`
  - `portfolio_ranking_rows(...)`
  - `render_portfolio_ranking(...)`
  - `evaluated_my_portfolio_strategy(...)`

Current ranking already exposes some path/role information, but the Recommendation Audit says Scenario Consistency Score, Tail Exposure, Asset Role Balance, and User Decision Complexity are not yet first-class ranking inputs.

## UI

Current UI entry points are mainly in:

- `app.py`
  - `render_core_decision(...)`
  - `render_portfolio_ranking(...)`
  - `render_strategy_detail_dialog(...)`
  - `render_portfolio_detail_bundle(...)`
  - `render_post_match_analysis_tab(...)`
  - My Portfolio input and settlement functions

Current visible areas affected by future integration:

- Core Decision / 组合排行
- Portfolio detail dialogs
- Post Match Analysis / Recommendation Audit
- My Portfolio comparison
- Data Source tab, if read-only scenario/audit reports need display links

## 2. Scenario Engine Integration Points

## Read Inputs

Scenario Engine should read existing local structures first:

- `data/history/<match_slug>_pre.json`
- `data/worldcup2026/<match_slug>/pre_match.json`
- `data/worldcup2026/<match_slug>/odds.json`
- `data/worldcup2026/<match_slug>/fixture.json`

In app runtime, the same information already exists as:

- `match`
- `odds`
- `api_football_data`
- `result_distribution`
- `portfolio_candidates`
- `snapshot_combo`
- `snapshot_strategies`
- `decision`
- `betting_opinion`

## Call Sites

Recommended future module boundary:

- Add a new scenario module later, for example `modules/scenario_engine.py`.
- Keep `scripts/generate_scenario_engine_report.py` as read-only reporting and validation.

Future app integration points:

- After `portfolio_candidates = recommendation_combo(...)`.
- After `snapshot_combo = stake_amounts(...)`.
- After `snapshot_strategies = strategy_comparison(...)`.
- Before `snapshot_payload` is saved.

Scenario Engine should produce:

- `scenario_snapshot`
- `scenario_consistency_score`
- `asset_scenario_mapping`
- `tail_exposure`
- `main_scenario_coverage`
- `secondary_insurance_coverage`
- `critical_conflict_flags`
- `data_confidence`

## Snapshot Additions

Add to future `snapshot_payload`:

```text
scenario_engine:
  main_scenario
  secondary_scenario
  upset_scenario
  asset_mapping
  scenario_consistency_score
  score_breakdown
  conflict_flags
  data_confidence
```

Do not replace current recommendation fields in Phase 1.

## 3. Recommendation Auditor Integration Points

## Trigger Timing

Phase 1:

- Trigger manually through read-only report generation after Scenario Engine report exists.
- Output only Markdown report.

Phase 2:

- Trigger automatically after Scenario Engine output is produced and before snapshot save.
- Store audit result in snapshot, but do not block recommendation.

Phase 3:

- Use audit severity as a guardrail for ranking and default recommendation eligibility.

## Output Location

Current read-only output:

- `docs/RECOMMENDATION_AUDIT_REPORT.md`

Future app/snapshot output:

```text
recommendation_audit:
  status
  severity
  critical_conflicts
  high_conflicts
  findings
  ranking_guardrails
```

## Auditor Responsibilities

Auditor checks:

- Main recommendation is scenario-specific, not generic.
- Assets serve Main, Secondary, or Upset scenario.
- Over3.5 + 1:0 / 2:0 conflicts are blocked.
- Aggressive Return and Tail assets are not treated as core evidence.
- Portfolio Ranking consumes Scenario Consistency Score.
- My Portfolio uses the same scenario logic as system portfolios.

## 4. Portfolio Ranking 2.0 Integration Points

## New Fields

Add future strategy-level fields:

- `scenario_consistency_score`
- `tail_exposure`
- `asset_role_balance_score`
- `main_scenario_coverage`
- `secondary_insurance_coverage`
- `critical_conflict_count`
- `user_decision_complexity`
- `default_recommendation_eligible`
- `ranking_warnings`

## Data Flow

Scenario Engine produces:

- scenario labels
- asset mapping
- consistency score
- coverage fields
- tail exposure

Recommendation Auditor produces:

- severity
- conflict flags
- guardrail status

Portfolio Ranking 2.0 consumes both:

```text
strategy_score_v2 =
  value_layer(EV, ROI, Sharpe)
  + scenario_layer(Scenario Consistency Score)
  + role_layer(Asset Role Balance)
  + coverage_layer(Main + Secondary coverage)
  - risk_penalties(Tail, conflicts, complexity)
```

## Ranking Guardrails

Future Ranking must enforce:

- Critical Conflict cannot rank first.
- Scenario Consistency Score below 75 must show warning.
- Scenario Consistency Score below 60 cannot be default recommendation.
- Tail-heavy portfolio cannot be default recommendation unless labeled aggressive/upset.
- Aggressive Return and Tail assets cannot be core Main Scenario evidence.
- My Portfolio and system portfolios must use the same score framework.

## 5. UI Impact Analysis

## Pages That Need Changes

Core Decision / Portfolio Ranking:

- Add Scenario Consistency Score column.
- Add Tail Exposure or risk label.
- Add Default Eligible / Warning indicator.
- Separate Core Return, Aggressive Return, Insurance, and Tail in detail dialogs.

Portfolio detail dialog:

- Add scenario served by each asset.
- Add role mapping and conflict notes.
- Add Main/Secondary/Upset coverage summary.

Post Match Analysis:

- Add scenario audit replay from saved snapshot.
- Compare actual result against Main, Secondary, and Upset scenario.
- Include My Portfolio under same scenario audit fields.

My Portfolio:

- Show My Portfolio Score.
- Show rank against system portfolios.
- Show whether user portfolio is safer, more aggressive, tail-heavy, or contradictory.

## Pages That Do Not Need Changes In Phase 1

- Schedule/home page.
- Team Information tab.
- Market Data display, except optional source links later.
- API refresh scripts and terminal fetch mode.
- Static docs pages.

## 6. Implementation Order

## Phase 1: Minimum Change

Goal: prove integration without changing recommendation behavior.

Changes:

- Keep Scenario Engine as read-only script/report.
- Generate `SCENARIO_ENGINE_REPORT.md`.
- Generate `docs/RECOMMENDATION_AUDIT_REPORT.md`.
- Do not touch app ranking logic.
- Do not touch UI.
- Do not mutate snapshots.

Acceptance:

- Reports can be generated for Germany vs Ivory Coast.
- No data files change.
- No app behavior changes.

## Phase 2: Medium Change

Goal: attach scenario/audit metadata to snapshot and ranking rows without changing top recommendation.

Changes:

- Add a pure calculation module for Scenario Engine.
- Call it after portfolio strategy generation.
- Add scenario fields to `snapshot_payload`.
- Add Scenario Consistency Score and Tail Exposure to `portfolio_ranking_rows(...)`.
- Add warning labels in UI, but keep current ranking order initially.
- Evaluate My Portfolio with the same scenario fields.

Acceptance:

- Existing recommendations remain unchanged.
- Ranking UI shows scenario fields.
- Auditor can read snapshot fields instead of Markdown only.
- My Portfolio gets comparable scenario metrics.

## Phase 3: Full Implementation

Goal: make Ranking 2.0 govern default recommendations.

Changes:

- Replace or extend `strategy_score(...)` with Portfolio Ranking 2.0 score.
- Enforce guardrails in ranking sort.
- Prevent Critical Conflict from ranking first.
- Penalize tail-heavy portfolios.
- Require Scenario Consistency Score >= 75 for default recommendation.
- Use same score framework for system portfolios and My Portfolio.
- Save Scenario/Auditor/Ranking fields into pre/post snapshots.

Acceptance:

- Portfolio Ranking is scenario-aware.
- Default recommendation is audit-safe.
- Tail-heavy portfolios are clearly labeled.
- My Portfolio is ranked under the same rules.

## 7. Risk Analysis

Highest risk areas:

- `app.py` is large and currently owns recommendation, strategy, ranking, UI, My Portfolio, and snapshot saving. Broad edits here are risky.
- `strategy_score(...)`, `evaluate_strategy(...)`, and `evaluate_allocation(...)` affect ranking and optimizer behavior directly.
- `betting_asset_roles(...)` affects multiple displays and post-match role contribution.
- Snapshot structure changes can break replay, post-match analysis, and history files.
- UI changes in `render_portfolio_ranking(...)` can affect the main decision workflow.
- My Portfolio parsing and settlement must not diverge from system portfolio logic.

Risk controls:

- Keep Phase 1 report-only.
- In Phase 2, add fields without changing sort order.
- Add scenario metadata behind existing data structures instead of replacing them.
- Keep old score fields until Ranking 2.0 is proven.
- Test on Germany vs Ivory Coast first, then on matches with missing fields.
- Do not modify historical data during integration.

## 8. Final Integration Principle

Scenario Engine produces scenario truth.

Recommendation Auditor checks scenario safety.

Portfolio Ranking 2.0 decides which portfolio should be surfaced first.

UI should explain the decision, not hide the scenario tradeoffs.

