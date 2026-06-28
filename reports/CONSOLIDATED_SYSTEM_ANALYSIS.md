# Consolidated System Analysis

Date: 2026-06-28
Status: active single source of truth for UI-CACHE-API, MODEL-DESIGN, API flow, cache behavior, and risk/portfolio dependency analysis.

## Scope

This report consolidates durable findings from:

- `reports/ui_cache_api_audit.md`
- `reports/streamlit_load_flow_map.md`
- `reports/api_refresh_flow_audit.md`
- `reports/cache_opportunity_map.md`
- `reports/model_design_dependency_map.md`
- `reports/risk_score_flow_analysis.md`
- `reports/portfolio_pipeline_map.md`
- `reports/node2_model_flow_map.md`
- `reports/node2_model_dependency_graph.md`
- `reports/branch_consolidation_execution_phase1.md`

It should be updated after every Codex-Claude loop or graph-governed analysis cycle.

## Current System State

- Current branch: `dev-clean`.
- Current graph node: `NODE 2 - MODEL-DESIGN ANALYSIS (READ ONLY)`.
- Execution gate: `Gate 2 - Pre-Execution`.
- Product code modified by current analysis cycle: No.
- `PORTFOLIO_EXTRACTION`: `BLOCKED`.
- `BACKTEST_READY`: `NO`.
- Auto-advance: No.

## Unified Runtime Flow

```text
schedule / selected fixture
  -> Streamlit routing
  -> data source selection
       local DB / cache
       API-Football context
       odds payloads
       Polymarket public data
       user odds and saved portfolio state
  -> base model computations
       probabilities
       score recommendations
       value analysis
       betting opinion
  -> scenario layer
       result distribution
       game behavior
       scenario categories
  -> decision layer
       direction confidence
       upset and extreme-path risk
       participation advice
       stake guidance
  -> portfolio layer
       recommendation combo
       stake amount mapping
       style portfolios
       portfolio optimization
       portfolio score
       risk gate
       rank eligibility
  -> output layer
       UI tables
       report generation
       pre-match snapshots
       golden validation references
```

## UI-CACHE-API Findings

The schedule page is comparatively bounded. The detail page is the main load and recomputation hotspot because it combines data loading, model computation, portfolio candidate generation, report generation, snapshot creation, and tab rendering in one path.

Important UI/API/cache boundaries:

- API-Football is the only keyed provider in the current phase.
- API-Football is disabled for current UI-CACHE-API work.
- Polymarket is public-only.
- WorldCup2026 schedule API is public and separate from keyed API-Football refresh.
- Streamlit refresh status display reads `.runtime/ui_refresh_status.json` first, then `reports/samples/ui_refresh_status.sample.json`.
- Controlled API-Football refresh is script-based, not Streamlit-triggered.

Primary cache opportunities:

- detail-page derived payload cache.
- unified freshness display contract.
- API fan-out visibility for cache hit/miss versus API attempt.
- rerun isolation for user-input widgets.

## MODEL-DESIGN Findings

The model pipeline is understandable but fragmented.

There is no canonical `risk_score`. Risk is currently distributed across:

- upset and extreme-path risk in the decision engine.
- `strategy_score(...)` risk-control component.
- portfolio risk gate.
- correct-score exposure control.
- rank-1 eligibility.
- app-local optimizer risk terms.
- recommended stake display.
- golden-output behavior locks.

The missing contract is not just a field name. It affects stake sizing, ranking eligibility, portfolio score, UI display, and future backtest reproducibility.

## Portfolio And Ranking Findings

Portfolio construction crosses `app.py`, `modules/portfolio_engine.py`, and `modules/strategy/core.py`.

Critical dependencies:

- `recommendation_combo` and `stake_amounts` are app-local.
- `optimize_betting_portfolio` and allocation evaluation are app-local.
- portfolio score and risk gate are in `modules/portfolio_engine.py`.
- final ranking key is in `modules/strategy/core.py`.
- UI rendering consumes the same payload that ranking depends on.

Ranking depends on implicit dictionary fields:

- `score`
- `risk_gate.risk_level`
- `rank1_eligibility.rank1_eligible`
- `correct_score_exposure.stake_share`
- score-grid and distribution payload shape
- game-behavior metadata

Portfolio extraction remains blocked until a stable risk and portfolio candidate contract exists.

## Golden Validation Findings

Golden output assets protect observable behavior, but they are not yet a full model contract.

Current golden dependencies:

- `reports/golden_output_snapshot_v1.json`
- `reports/golden_output_snapshot_v2.json`
- `reports/golden_risk_contract_v1.json`
- validation reports and shadow portfolio reports
- selected `data/history/*_pre.json` snapshots as historical source data

Coverage gap:

- golden outputs validate final behavior better than intermediate risk semantics.
- risk gate and rank eligibility payload coverage is partial.
- backtest scripts depend on historical snapshot schema produced by `app.py`.

## OPS And Branch Governance Findings

Branch consolidation is not in execution phase.

Phase 1 safe-mode result:

- no branch merged.
- no branch deleted.
- no branch physically archived.
- already-merged stale branches are archive candidates only.
- high-risk model, UI-CACHE-API, ops-protocol, legacy, release, and backup branches remain untouched.

The system is suitable for planning and review, not automatic branch execution.

## Consolidated Risk Register

| Area | Severity | Current decision |
| --- | --- | --- |
| report fragmentation | medium | mitigated by this consolidated report; must keep updating |
| UI/model coupling | high | do not extract model/portfolio yet |
| API refresh coupling | medium | keep real API refresh script-gated |
| cache/freshness contract | medium | design unified display contract before implementation |
| risk semantics | high | design canonical risk contract before portfolio extraction |
| portfolio extraction | high | blocked |
| backtest isolation | high | not ready |
| branch execution | medium-high | planning only; Jin approval required |

## Single Source Of Truth Rules

- This file is the first-read summary for system analysis state.
- New node reports may still be created, but their durable findings must be consolidated here.
- Avoid duplicating the same finding across UI, MODEL, API, CACHE, and OPS reports.
- If Claude or Codex detects fragmentation, update this file before continuing.
- Do not use this file to authorize execution; it is an analysis source, not a merge/delete approval.

## Next Safe Step

Recommended next step:

1. Create a sanitized Claude review packet for this consolidation state.
2. Ask Claude to review fragmentation, graph alignment, and execution-gate safety.
3. Do not auto-advance to execution.
4. Keep `PORTFOLIO_EXTRACTION: BLOCKED` and `BACKTEST_READY: NO`.

## Current Loop Status

- Claude review triggered in this cycle: No.
- Reason: report fragmentation was detected before review, so consolidation was required first.
- `REPORT_CONSOLIDATION_REQUIRED`: Yes at cycle start.
- `REPORT_CONSOLIDATION_STATUS`: Completed locally.
- `AUTO_ADVANCE`: No.
