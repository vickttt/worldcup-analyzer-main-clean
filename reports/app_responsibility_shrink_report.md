# app.py Responsibility Shrink Report

This report evaluates `app.py` after Phase 1 extraction. It is report-only and does not modify code.

## Before vs After

| Responsibility | Before Phase 1 | After Phase 1 | Status |
|---|---|---|---|
| UI responsibility | `app.py` owned nearly all Streamlit rendering and routing. | Still owned by `app.py`. | Not reduced yet. |
| Odds logic presence | Odds formatting, actual odds completeness, handicap/total parsing, and outcome helpers lived in `app.py`. | First odds helper group moved to `modules/odds/core.py`; `app.py` imports and calls those helpers. | Reduced. |
| Strategy logic presence | Confidence text, match betting score, recommended stake, path consistency, `strategy_score`, and ranking key lived in `app.py`. | First strategy helper group moved to `modules/strategy/core.py`; `app.py` imports and calls those helpers. | Reduced. |
| Computation responsibility | `app.py` held odds, strategy, portfolio ranking, allocation, settlement, and audit helpers. | Odds/strategy surface reduced, but portfolio allocation, settlement, audit, and many row-building helpers remain. | Still high. |
| Orchestration responsibility | `app.py` loaded data, assembled match context, rendered tabs, and persisted snapshots. | Unchanged. | Still high. |

## Current app.py Role

`app.py` currently acts as:

- Runtime entry point.
- Streamlit UI renderer.
- Page router.
- Match orchestration layer.
- Portfolio ranking and allocation holder.
- Snapshot/history persistence holder.
- Post-match settlement/audit holder.
- Row/table formatting holder.

## Remaining Violations Of Target Role

Target role:

- input orchestration
- function calls
- rendering

Still violating or exceeding target:

- Portfolio allocation and ranking functions remain in `app.py`.
- Post-match settlement and audit functions remain in `app.py`.
- Snapshot path/load/save helpers remain in `app.py`.
- Manual portfolio parsing and matching remain in `app.py`.
- Many table row builders remain in `app.py`.
- `render_analysis_page` still combines data loading, analysis assembly, snapshot persistence, and UI rendering.

## Reduced Areas

- Odds helper definitions removed from `app.py` and wired through `modules.odds.core`.
- Strategy helper definitions removed from `app.py` and wired through `modules.strategy.core`.
- `app.py` no longer defines the moved Phase 1 functions directly.

## Readiness Decision

- READY FOR PORTFOLIO EXTRACTION: NO.
  - Reason: `app.py` is not yet reduced to pure orchestration; portfolio logic remains large and product-sensitive.
- READY FOR BACKTEST MODULE SPLIT: NO.
  - Reason: settlement/audit logic remains mixed with app-level snapshot and UI assumptions.

## Recommended Stabilization Before Next Extraction

- Add golden-output checks for `strategy_score`, `strategy_comparison`, and representative portfolio rows.
- Define snapshot fixture inputs for pre-match and post-match flows.
- Extract portfolio logic only after behavior comparison checks are available.
