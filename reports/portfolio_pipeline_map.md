# Portfolio Pipeline Map

Date: 2026-06-28
Task graph node: `NODE 2 - MODEL-DESIGN ANALYSIS (READ ONLY)`

## Safety Boundary

This report maps the portfolio pipeline without changing production behavior.

- Portfolio logic changed: No.
- Strategy logic changed: No.
- Ranking logic changed: No.
- Backtest enabled: No.
- Golden outputs changed: No.

## Current Pipeline

```text
match and odds inputs
  -> probability / result distribution
  -> recommendation combo
  -> stake amount mapping
  -> portfolio candidate generation
  -> allocation evaluation / optimization
  -> strategy comparison
  -> portfolio scoring
  -> risk gate and rank eligibility
  -> rank ordering
  -> UI rendering and reports
```

## Inputs

| Input | Source | Purpose |
| --- | --- | --- |
| match record | app data loaders and local data | base teams, metadata, status |
| odds | market fetch/cache paths | pricing and value signals |
| API-Football context | refresh/cache layer | optional fixture context |
| result distribution | probability/model helpers | scenario weights and score grid |
| actual odds | market/user odds payload | realized pricing for selected assets |
| existing portfolio | user/session inputs | compare against generated candidates |

## Generation And Scoring Functions

| Step | Function | Location | Notes |
| --- | --- | --- | --- |
| recommendation combo | `recommendation_combo` | `app.py` | app-local bridge from decision to portfolio seed |
| total stake hint | `recommended_total_stake` | `app.py` | decision-to-stake display mapping |
| stake split | `stake_amounts` | `app.py` | combo stake construction |
| style portfolios | `generate_style_portfolios` | `modules/portfolio_engine.py` | creates candidate portfolio families |
| portfolio templates | `generate_portfolio_templates_by_pressure` | `modules/portfolio_engine.py` | pressure-aware candidate generation |
| return matrix | `build_return_matrix` | `app.py` | scenario return computation |
| allocation evaluation | `evaluate_allocation` | `app.py` | vector scoring and risk stats |
| optimizer | `optimize_betting_portfolio` | `app.py` | optimized allocation generation |
| strategy comparison | `strategy_comparison` | `app.py` | assembled comparison payload |
| portfolio score | `compute_portfolio_score` | `modules/portfolio_engine.py` | portfolio quality scoring |
| risk gate | `portfolio_risk_gate` | `modules/portfolio_engine.py` | risk classification and eligibility |
| rank-1 eligibility | `rank1_eligibility_check` | `modules/portfolio_engine.py` | rank eligibility constraint |
| rank key | `rank_key_with_eligibility` | `modules/strategy/core.py` | final ranking order key |
| render ranking | `render_portfolio_ranking` | `app.py` | UI display and final table construction |

## Ranking Dependencies

The final ranking depends on:

- strategy score.
- risk gate level.
- rank-1 eligibility.
- correct-score exposure share.
- score-grid and distribution payload shape.
- portfolio score and style labels.
- app-local payload assembly.

Because these dependencies cross `app.py`, `modules/strategy/core.py`, and `modules/portfolio_engine.py`, portfolio extraction remains unsafe until a canonical contract is defined.

## Golden And Shadow Dependencies

Current behavior is protected by:

- golden output snapshots.
- portfolio shadow reports.
- golden assertion gate reports.
- risk semantics reports.

These assets are sufficient for read-only design analysis, but not enough to permit portfolio extraction or backtest enablement.

## High-Risk Coupling Points

- app-local optimizer and strategy comparison functions.
- dictionary payload fields shared between strategy, portfolio, and UI rendering.
- eligibility and risk-gate data used by ranking.
- stake display values that may look like allocation decisions but are not a canonical capital model.
- partial golden payload coverage for risk-gate internals.

## Conservative Readiness

- Ready for NODE 2 read-only model-design analysis: Yes.
- Ready to implement canonical risk contract: No, approval required.
- Ready to extract portfolio: No.
- Ready to split backtest: No.
