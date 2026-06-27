# NODE 3B Model-Design Continuation Analysis

Date: 2026-06-28
Node: `NODE 3B - MODEL-DESIGN ANALYSIS CONTINUATION (READ ONLY)`
Mode: Codex-GitHub-Claude loop test input

## Safety Boundary

- `app.py` modified: No.
- `modules/` modified: No.
- `data/` modified: No.
- Golden JSON modified: No.
- Model, ranking, portfolio, strategy, odds, or backtest logic changed: No.
- Branch merge/delete/archive performed: No.
- Execution phase task performed: No.

## Scope

This continuation validates model-design dependencies identified during NODE 2 without implementing any changes.

Focus:

- risk-score dependency flow validation.
- portfolio construction path tracing.
- ranking signal propagation.
- scenario engine input mapping.
- model-to-UI dependency touchpoints.

## 1. Risk-Score Dependency Flow Validation

There is still no canonical `risk_score`. The active risk path is a multi-signal chain:

```text
odds and market context
  -> upset and extreme-path risk
  -> participation and stake guidance
  -> strategy risk-control component
  -> portfolio risk gate
  -> rank-1 eligibility
  -> ranking key
  -> UI display and saved output
```

Validated dependency points:

| Risk signal | Source | Consumer | Contract status |
| --- | --- | --- | --- |
| upset risk score | `modules/decision_engine.py` | participation advice | implicit |
| extreme-path risk | `modules/decision_engine.py` | value/risk adjustment | implicit |
| risk-control component | `modules/strategy/core.py::strategy_score` | blended strategy score | implicit |
| zero-risk score | `modules/portfolio_engine.py` coverage metrics | portfolio score drawdown component | implicit |
| risk gate level | `modules/portfolio_engine.py::portfolio_risk_gate` | rank eligibility and ranking | semi-explicit |
| rank-1 eligibility | `modules/portfolio_engine.py::rank1_eligibility_check` | ranking key and UI | semi-explicit |

Conclusion:

- Risk is propagated through multiple payload fields, not one stable contract.
- A future implementation task should define a read-only risk contract before moving portfolio logic.

## 2. Portfolio Construction Path Tracing

Portfolio construction starts in `app.py` and crosses module boundaries:

```text
decision output
  -> recommendation_combo(...)
  -> stake_amounts(...)
  -> strategy_comparison(...)
  -> compute_portfolio_score(...)
  -> portfolio_risk_gate(...)
  -> rank1_eligibility_check(...)
  -> rank_key_with_eligibility(...)
  -> render_portfolio_ranking(...)
```

Validated touchpoints:

- `recommendation_combo(...)` wraps recommendation slot construction.
- `stake_amounts(...)` converts decision stake guidance into item amounts.
- `strategy_comparison(...)` evaluates and sorts candidate strategies.
- `compute_portfolio_score(...)` computes portfolio quality components.
- `portfolio_risk_gate(...)` computes risk level and failed paths.
- `rank1_eligibility_check(...)` gates first-rank eligibility.
- `rank_key_with_eligibility(...)` orders visible rankings.

Extraction risk remains high because amount assignment, optimization, scoring, ranking, and rendering share dictionary payloads rather than a typed boundary.

## 3. Ranking Signal Propagation

Ranking is driven by a tuple-like priority:

```text
rank-1 eligible
  -> risk level
  -> correct-score exposure penalty
  -> strategy or portfolio score
```

Signal propagation path:

```text
portfolio candidate
  -> score_rows and coverage metrics
  -> risk_gate
  -> correct_score_exposure
  -> rank1_eligibility
  -> rank_key_with_eligibility
  -> UI ranking
```

Risk:

- Missing or partial payload fields can change ranking behavior.
- A refactor that preserves function outputs but changes payload assembly order could alter visible rankings.
- Golden output checks protect final order, but intermediate rank reasons need stronger contract coverage before extraction.

## 4. Scenario Engine Input Mapping

Scenario inputs are produced from market and match context:

```text
odds probabilities
  + Polymarket probabilities
  + Asian handicap signal
  + totals signal
  + API-Football match context
  -> build_result_distribution(...)
  -> game_behavior
  -> main / boundary / extreme paths
  -> score grid and portfolio risk paths
```

Consumers:

- decision engine uses distribution-aware value analysis.
- portfolio engine uses scenario category, pressure fit, and score-grid risk.
- UI risk sections render extreme path and exposure descriptions.
- snapshots and reports persist distribution-shaped payloads.

Validation result:

- Scenario engine linkage is central to portfolio risk and ranking.
- Scenario payload shape must be treated as a contract before portfolio or backtest changes.

## 5. Model To UI Dependency Touchpoints

Model outputs are still assembled inside the Streamlit detail-page path.

Touchpoints:

- `render_analysis_page(...)` builds data, model, portfolio, report, and snapshot payloads.
- `render_portfolio_ranking(...)` is both UI and final ranking consumer.
- Streamlit session state controls selected fixture and page transitions.
- saved snapshots are produced after UI-route execution.

Implication:

- Model layer cannot yet be considered UI-independent.
- Future work should first define payload contracts, then isolate computation from rendering.

## 6. Readiness Decision

| Gate | Decision |
| --- | --- |
| Continue read-only model analysis | Yes |
| Implement canonical risk score | No |
| Extract portfolio | No |
| Enable backtest | No |
| Change ranking logic | No |
| Auto-advance to execution | No |

## 7. Claude Review Questions

Claude should review whether:

- NODE 3B remained read-only.
- the dependency summary is consistent with NODE 2 and consolidated analysis.
- protected paths remain untouched.
- `NEXT_NODE` should remain a review-only decision rather than execution.
- system health is acceptable for loop mechanics testing.

Expected review fields:

- `BRANCH_OK`
- `NEXT_NODE`
- `AUTO_ADVANCE`
- `SYSTEM_HEALTH`
- `REPORT_CONSOLIDATION_REQUIRED`
- review result
