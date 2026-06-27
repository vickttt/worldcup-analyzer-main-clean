# Model Design Dependency Map

Date: 2026-06-28
Task graph node: `NODE 2 - MODEL-DESIGN ANALYSIS (READ ONLY)`
Scope: read-only model, risk, scoring, ranking dependency preparation.

## Safety Boundary

- Product code modified: No.
- Model logic modified: No.
- Ranking logic modified: No.
- Portfolio logic modified: No.
- `app.py` runtime behavior modified: No.
- `modules/` modified: No.
- `data/` modified: No.
- Golden JSON modified: No.

## High-Level Dependency Flow

```text
match inputs / odds / API-Football context / public market context
  -> probability and result distribution helpers
  -> decision and recommendation helpers
  -> strategy scoring
  -> portfolio candidate generation and scoring
  -> ranking, eligibility, and UI display
  -> golden snapshots / QA reports
```

## Model-Layer Components

| Area | Current locations | Role | Dependency risk |
| --- | --- | --- | --- |
| probability blend | `modules/probability_model.py`, `app.py` imports | combine market, model, and contextual probabilities | medium |
| result distribution | `modules/result_distribution.py`, `app.py` helpers | build score/result paths used by strategy and portfolio evaluation | medium |
| decision engine | `modules/decision_engine.py`, `app.py` imports | produce participation and betting guidance | medium |
| strategy scoring | `modules/strategy/core.py` | score strategy quality, match betting attractiveness, and ranking key | high |
| portfolio engine | `modules/portfolio_engine.py` | generate and score portfolio candidates, risk gates, rank-1 eligibility | high |
| app-local portfolio orchestration | `app.py` | stake display, allocation optimization, strategy comparison, ranking rendering | high |
| golden validation | `reports/golden_output_snapshot_v*.json`, risk reports | behavior lock and extraction safety reference | high |

## Key Functions And Contracts

| Function | Location | Dependency role | Notes |
| --- | --- | --- | --- |
| `strategy_score` | `modules/strategy/core.py` | combines EV/ROI, loss risk, script consistency, odds value, simplicity | no canonical `risk_score` output |
| `match_betting_score` | `modules/strategy/core.py` | summarizes match-level betting attractiveness from ranked strategies | consumes strategy payload fields and risk hints |
| `recommended_stake_mvp` | `modules/strategy/core.py` | maps match score and decision to display stake bands | display-oriented, not canonical allocation |
| `rank_key_with_eligibility` | `modules/strategy/core.py` | sorting key using eligibility, risk gate, correct-score exposure, and score | high ranking sensitivity |
| `portfolio_risk_gate` | `modules/portfolio_engine.py` | classifies portfolio risk and rank eligibility signals | key hidden dependency for ranking |
| `rank1_eligibility_check` | `modules/portfolio_engine.py` | determines first-rank eligibility constraints | high behavior sensitivity |
| `compute_portfolio_score` | `modules/portfolio_engine.py` | scores strategy portfolios | depends on distribution and strategy payload shape |
| `generate_style_portfolios` | `modules/portfolio_engine.py` | builds style candidate portfolios | depends on recommendation combo contract |
| `compute_match_investment_score` | `modules/portfolio_engine.py` | summarizes match investment posture across strategies | aggregates risk and portfolio signals |
| `recommendation_combo` | `app.py` | builds primary recommendation combo | still app-local |
| `stake_amounts` | `app.py` | maps combo and decision into stake display | app-local coupling point |
| `evaluate_allocation` | `app.py` | evaluates vector allocation performance | app-local portfolio computation |
| `optimize_betting_portfolio` | `app.py` | builds optimized betting portfolio | app-local optimizer |
| `strategy_comparison` | `app.py` | builds strategy comparison payloads | app-local bridge to UI |
| `render_portfolio_ranking` | `app.py` | renders ranking and portfolio display | UI plus model-result coupling |

## Ranking Dependency Graph

```text
strategy payload
  -> score fields
  -> risk_gate
  -> rank1_eligibility
  -> correct_score_exposure
  -> rank_key_with_eligibility
  -> portfolio ranking order
  -> match recommendation display
```

The ranking path is not yet fully isolated because the payload is assembled across `modules/strategy/core.py`, `modules/portfolio_engine.py`, and app-local rendering/orchestration code.

## Model-Design Risks

- No canonical `risk_score` contract exists.
- Portfolio risk semantics are distributed across strategy score, portfolio score, risk gate, rank eligibility, correct-score exposure, stake display, and UI display.
- Several dependencies are implicit dictionary contracts rather than typed interfaces.
- App-local functions still perform model-adjacent portfolio allocation and comparison.
- Golden v2 coverage exists but does not fully prove all risk-gate payload fields.

## NODE 2 Readiness

- Ready for read-only analysis: Yes.
- Ready for model implementation: No.
- Ready for portfolio extraction: No.
- Ready for backtest enablement: No.
