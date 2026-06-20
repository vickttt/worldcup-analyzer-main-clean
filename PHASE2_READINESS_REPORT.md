# Phase 2 Implementation Readiness Report

Date: 2026-06-21

Scope: static analysis only. No business code, data files, UI, branch, commit, push, app runtime, or API refresh was modified or executed.

## Executive Verdict

Phase 2 is ready only as a metadata-first integration.

The safest path is to compute Scenario Engine and Recommendation Auditor outputs as optional sidecar fields, store them in snapshots, and expose them gradually. Phase 2 should not change ranking order, optimizer behavior, recommendation selection, or Streamlit UI decision flow until the new fields have been validated against existing snapshots.

Primary risk: `app.py` currently owns recommendation evaluation, portfolio ranking, snapshot creation, and UI rendering in one file. The most dangerous functions are the ones that affect score calculation, optimization utility, and ranking sort order.

## Current Code Structure

### Main Application

`app.py` is the central integration point for:

- asset role classification
- user allocation evaluation
- strategy scoring
- portfolio ranking
- snapshot creation
- post-match snapshot refresh
- ranking UI rendering

Key functions identified:

- `role_exposure(...)`
- `role_balance_adjustment(...)`
- `evaluate_allocation(...)`
- `strategy_path_consistency(...)`
- `strategy_score(...)`
- `evaluate_strategy(...)`
- `strategy_comparison(...)`
- `strategy_table_rows(...)`
- `save_match_snapshot(...)`
- `snapshot_portfolio_candidates(...)`
- `portfolio_ranking_rows(...)`
- `evaluated_my_portfolio_strategy(...)`
- `render_portfolio_ranking(...)`
- `render_post_match_analysis_tab(...)`

### Modules

The `modules/` directory contains supporting clients, models, parsers, and report helpers. There is no dedicated Scenario Engine module yet.

Relevant existing module categories:

- data and API clients: odds, schedule, team profile, weather, Polymarket
- probability and score models
- value and decision models
- report generation
- local database helpers

Phase 2 should avoid changing existing model/client modules unless a new read-only module is added for Scenario Engine calculations.

## A. Scenario Engine 接入点

### Best Low-Risk Entry

Recommended future location:

- new isolated read-only module such as `modules/scenario_engine.py`

Risk: LOW

Reason:

- keeps Scenario Engine logic separate from existing recommendation logic
- avoids changing current scoring and ranking behavior
- allows testable pure functions using existing snapshot/data dictionaries

### Best Runtime Attachment Point

Recommended future call site:

- after `snapshot_combo` and `snapshot_strategies` are created
- before `snapshot_payload` is saved in the match detail flow

Risk: MEDIUM

Reason:

- this point has access to recommendation combo, strategy outputs, probability distribution, value analysis, and portfolio candidates
- adding optional snapshot metadata here is safer than changing ranking internals
- any failure must degrade to `scenario_engine: null` or a warning object, not block page rendering

### Strategy-Level Field Attachment

Best place to attach these fields:

- `evaluate_strategy(...)`

Fields:

- `scenario_consistency_score`
- `asset_scenario_mapping`
- `tail_exposure`
- `main_scenario_coverage`
- `secondary_insurance_coverage`

Risk: MEDIUM

Recommended Phase 2 behavior:

- compute and return these as metadata only
- do not include them in `score`
- do not change ranking sort order
- do not change optimized portfolio selection

### Role and Tail Exposure Sources

Useful existing helpers:

- `role_exposure(...)`
- `role_allocation_rows(...)`
- `role_balance_adjustment(...)`

Risk: MEDIUM

Recommendation:

- read from existing asset role outputs
- do not rewrite `betting_asset_roles(...)` during Phase 2
- do not reinterpret asset roles in a way that changes current recommendation behavior

### Legacy Consistency Function

Existing function:

- `strategy_path_consistency(...)`

Risk: HIGH if changed

Recommendation:

- keep existing function unchanged in Phase 2
- introduce Scenario Consistency Score as a separate field
- compare old and new consistency signals in reports before replacing any scoring logic

## B. Recommendation Auditor 接入点

### Best Snapshot Field

Recommended future top-level snapshot field:

- `recommendation_audit`

Suggested fields:

- `audit_status`
- `audit_severity`
- `conflict_flags`
- `auditor_notes`
- `checked_at`

Risk: LOW to MEDIUM

Reason:

- pre-match snapshots can safely carry additional optional JSON fields
- existing post-match snapshot refresh logic already recognizes `recommendation_audit` as a refreshable key

### Best Computation Point

Recommended future call site:

- after Scenario Engine output is generated
- after strategy evaluation is available
- before snapshot save

Risk: MEDIUM

Reason:

- Auditor depends on Scenario Engine output and recommendation assets
- should run after all recommendation candidates are available

### Phase 2 Auditor Behavior

Recommended behavior:

- detect and store conflict flags
- label severity
- produce warnings
- do not block recommendations
- do not reorder portfolios
- do not rewrite user-facing recommendation text

Risk: LOW if metadata-only, HIGH if it blocks or rewrites recommendations.

## C. Portfolio Ranking 2.0 接入点

| Function | Phase 2 Impact | Risk | Notes |
|---|---:|---:|---|
| `strategy_score(...)` | should not change yet | HIGH | Changing weights directly changes all rankings and recommendation order. Keep legacy score stable during Phase 2. |
| `evaluate_strategy(...)` | attach v2 metadata | MEDIUM | Best place to compute/store `scenario_consistency_score`, tail exposure, coverage, and role balance without changing ranking. |
| `evaluate_allocation(...)` | avoid scoring changes | HIGH | This affects optimization utility and selected allocation. Changing it can silently alter portfolio construction. |
| `portfolio_ranking_rows(...)` | display-only columns | LOW to MEDIUM | Safe if adding optional columns only. Risk rises if table logic changes score, rank, or default recommendation. |
| `strategy_comparison(...)` | avoid sorting changes | HIGH | Currently sorts by score and assigns ranks. Do not change sort key in Phase 2. |
| `render_portfolio_ranking(...)` | display-only warnings | MEDIUM | Safe for showing warnings. Risk rises if UI starts suppressing or reordering strategies. |
| `evaluated_my_portfolio_strategy(...)` | parity through shared evaluator | LOW to MEDIUM | If v2 fields are added in `evaluate_strategy(...)`, My Portfolio can inherit the same evaluation framework. |

### Recommended Phase 2 Ranking Rule

Do not replace the current score.

Add separate fields only:

- Scenario Consistency Score
- Tail Exposure
- Asset Role Balance
- Main Scenario Coverage
- Secondary Insurance Coverage
- Audit Status
- Audit Severity
- Conflict Flags

Ranking formula changes should wait until Phase 3 after the metadata is validated.

## D. Snapshot 影响

### Future Fields

Recommended future top-level snapshot fields:

```json
{
  "scenario_engine": {},
  "recommendation_audit": {}
}
```

### Historical Database

Risk: MEDIUM

Expected impact:

- older snapshots will not have `scenario_engine`
- older snapshots may not have `recommendation_audit`
- readers must use optional access and graceful fallback

Recommendation:

- do not mutate old historical snapshots in Phase 2
- do not require these fields for replay or post-match pages
- consider a schema version note only after the fields stabilize

### Post-Match Analysis

Risk: MEDIUM

Current observation:

- post-match snapshot refresh already has `recommendation_audit` in refreshable keys
- `scenario_engine` is not yet part of the known refreshable set

Recommendation:

- keep Scenario Engine as a pre-match optional field first
- only add post-match refresh behavior after read paths are confirmed

### Replay

Risk: LOW to MEDIUM

Expected impact:

- extra JSON fields should not break replay if readers ignore unknown keys
- replay can break if new UI assumes fields always exist

Recommendation:

- every read path must degrade when fields are missing
- use report-style display before using fields as mandatory inputs

## E. UI 影响

### Phase 2 需要改的页面

Only if Phase 2 proceeds beyond metadata storage:

- Portfolio Ranking table
- Portfolio Ranking detail dialog
- recommendation audit or report display area
- optional snapshot/report inspection area

Recommended visible additions:

- Scenario Consistency Score
- Audit Status
- Audit Severity
- Tail Exposure warning
- Conflict Flags

Risk: LOW to MEDIUM if display-only.

### Phase 2 不需要改的页面

Should remain unchanged in Phase 2:

- schedule/home page
- API refresh controls
- raw market data views
- team intelligence pages
- post-match settlement mechanics
- existing recommendation generation controls
- existing Portfolio Ranking sort order

### UI Constraint

Do not make the UI the source of truth.

Scenario Engine and Auditor outputs should first exist as structured snapshot/report data. UI should only render those outputs after they are stable.

## F. 推荐实施顺序

### Step 1: Add Read-Only Scenario Metadata Generator

Risk: LOW

Action:

- add isolated pure functions in a new module
- accept existing snapshot/recommendation dictionaries
- output structured `scenario_engine` metadata
- no app UI changes
- no ranking formula changes

### Step 2: Attach Scenario Engine Output to Snapshot

Risk: MEDIUM

Action:

- call Scenario Engine after strategies are evaluated
- add optional `scenario_engine` to `snapshot_payload`
- tolerate missing or failed Scenario Engine output
- keep current recommendation and ranking untouched

### Step 3: Attach Recommendation Auditor Output

Risk: MEDIUM

Action:

- run Auditor after Scenario Engine output exists
- add optional `recommendation_audit` to `snapshot_payload`
- store `audit_status`, `audit_severity`, and `conflict_flags`
- do not block or reorder recommendations

### Step 4: Add Display-Only Ranking Metadata

Risk: MEDIUM to HIGH

Action:

- add optional columns to Portfolio Ranking rows
- show warnings/details in ranking UI
- keep current `score` and ranking sort unchanged
- do not alter optimizer utility

Actual Portfolio Ranking 2.0 scoring changes should be deferred until Phase 3.

## Highest-Risk Areas

1. `evaluate_allocation(...)`

Changing this can alter optimized allocation selection.

2. `strategy_score(...)`

Changing this can alter all system strategy rankings.

3. `strategy_comparison(...)`

Changing sorting here can change the recommended top strategy.

4. Snapshot read paths

Adding fields is safe only if all readers tolerate missing fields.

5. Ranking UI density

Adding too many metrics can reduce decision clarity, which conflicts with product principles.

## Phase 2 Readiness Decision

Ready with restrictions.

Allowed Phase 2 scope:

- add optional Scenario Engine metadata
- add optional Recommendation Auditor metadata
- generate structured report fields
- display metadata only after validation

Not recommended in Phase 2:

- changing `strategy_score(...)`
- changing `evaluate_allocation(...)`
- changing ranking sort order
- changing default recommendation selection
- rewriting UI decision flow
- mutating historical data
