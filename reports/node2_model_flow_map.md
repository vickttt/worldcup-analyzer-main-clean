# NODE 2 Model Flow Map

Date: 2026-06-28
Node: `NODE 2 - MODEL-DESIGN ANALYSIS (READ ONLY)`
Scope: model layer only; no product code changes.

## Safety Boundary

- `app.py` modified: No.
- `modules/` modified: No.
- `data/` modified: No.
- Golden JSON modified: No.
- Model, ranking, portfolio, strategy, odds, or backtest logic changed: No.
- API calls performed: No.
- Workflow or Claude API triggered: No.

## Input To Output Flow

```text
schedule / selected fixture / match parser
  -> odds, Polymarket, API-Football context, mock news, user odds
  -> base model layer
       combine_probabilities
       recommend_scores
       rate_opportunity
       analyze_value
       build_betting_opinion
  -> scenario layer
       build_match_context
       build_result_distribution
       build_extreme_scenarios
  -> decision layer
       build_decision_engine
       participation_advice
       recommended_stake
  -> portfolio seed layer
       recommendation_combo
       stake_amounts
  -> portfolio construction and scoring
       strategy_comparison
       generate_style_portfolios
       optimize_betting_portfolio
       compute_portfolio_score
       portfolio_risk_gate
       rank1_eligibility_check
  -> ranking
       rank_key_with_eligibility
       render_portfolio_ranking
  -> outputs
       UI tables
       report generation
       pre-match snapshot
       golden snapshots and validation reports
```

## Where `risk_score` Is Computed

There is no single canonical `risk_score`.

Risk appears in five different forms:

1. `modules/decision_engine.py`
   - `extreme_path_risk_score(odds)` derives a coarse extreme-path risk from favorite probability and handicap depth.
   - `risk_adjustment_component(odds, upset)` deducts value-rating points from upset and extreme-path risk.
   - `participation_advice(...)` uses `upset["score"]` as `risk_score` when choosing participation labels.
   - `recommended_stake(...)` maps direction confidence and value rating into stake bands, with no canonical portfolio risk object.

2. `modules/strategy/core.py`
   - `strategy_score(...)` computes a blended strategy score.
   - The risk component is `risk_control_score`, derived from max-loss ratio and concentration penalty.
   - The returned score is a blended quality score, not a normalized risk contract.

3. `modules/portfolio_engine.py`
   - `portfolio_risk_gate(...)` calculates failed-path probability, adjacent-path failure, main-path coverage, correct-score concentration, and risk level.
   - `correct_score_exposure_control(...)` controls exact-score exposure.
   - `rank1_eligibility_check(...)` combines risk gate, exposure, pressure fit, coverage, and directional value into rank eligibility.

4. `app.py`
   - `portfolio_stability_score(...)`, `evaluate_allocation(...)`, and `optimize_betting_portfolio(...)` compute volatility, max loss, concentration, utility, and allocation behavior.
   - These still live inside the UI/orchestration entry point.

5. Display and golden layers
   - `recommended_stake_mvp(...)`, rendered stake displays, saved snapshots, and golden JSON preserve observable behavior but do not define risk semantics.

## Where Portfolio Is Constructed

Portfolio construction starts in `app.py` and crosses into `modules/portfolio_engine.py`.

| Step | Location | Role |
| --- | --- | --- |
| seed recommendation slots | `app.py::recommendation_combo` | wraps `build_recommendation_slots(...)` |
| stake mapping | `app.py::stake_amounts` | assigns amounts from decision stake and recommendation shares |
| app-local optimizer | `app.py::optimize_betting_portfolio` | builds score distribution and return matrix, then searches allocation vectors |
| style portfolios | `modules/portfolio_engine.py::generate_style_portfolios` | builds candidate families from recommended items |
| pressure templates | `modules/portfolio_engine.py::generate_portfolio_templates_by_pressure` | adds qualification-pressure-aware templates |
| score portfolio | `modules/portfolio_engine.py::compute_portfolio_score` | evaluates coverage, risk-adjusted value, pressure fit, directional odds value, drawdown, simplicity |
| risk gate | `modules/portfolio_engine.py::portfolio_risk_gate` | classifies portfolio risk level and blockers |
| rank eligibility | `modules/portfolio_engine.py::rank1_eligibility_check` | decides whether a portfolio may be Rank #1 |

## Where Ranking Decisions Are Made

Ranking is controlled by a combined payload contract:

```text
portfolio candidate payload
  -> score
  -> risk_gate
  -> rank1_eligibility
  -> correct_score_exposure
  -> rank_key_with_eligibility
  -> rendered portfolio ranking
```

The ranking order is sensitive to:

- `rank1_eligibility.rank1_eligible`.
- `risk_gate.risk_level`.
- `correct_score_exposure.stake_share`.
- strategy or portfolio `score`.
- score-grid availability.
- distribution and game-behavior metadata.

## Where Scenario Signals Are Generated

Scenario signals are generated mainly by `modules/result_distribution.py` and `modules/portfolio_engine.py`.

| Signal | Source | Use |
| --- | --- | --- |
| `main_path` | `build_result_distribution(...)` | base path display, scenario alignment |
| `boundary_path` | `build_result_distribution(...)` | handicap boundary reasoning |
| `extreme_path` | `build_result_distribution(...)` | risk display and tail-path reasoning |
| `game_behavior` | `build_result_distribution(...)` via behavior engine | pressure strictness and portfolio templates |
| score grid | `build_score_scenario_grid(...)` / app-local score distribution | PnL path, risk gate, coverage metrics |
| path category | `scenario_category(...)` | main/adjacent/tail/noise classification |
| extreme scenarios | `build_extreme_scenarios(...)` | UI risk analysis |

## Outputs

Final observable outputs include:

- strategy ranking list.
- portfolio ranking list.
- recommendation summary.
- match investment score.
- recommended stake display.
- saved pre-match snapshots under `data/history`.
- golden snapshots under `reports/`.

## Model Pipeline Clarity

Classification: `fragmented`.

Reason: the model pipeline is understandable, but the risk and portfolio contracts are not isolated. Risk semantics are spread across decision, strategy, portfolio, ranking, app-local optimizer, and UI display code.

## NODE 2 Conclusion

- NODE 2 read-only analysis: completed.
- Risk contract clarity: incomplete.
- Portfolio extraction readiness: blocked.
- Backtest readiness: no.
- Auto-advance safety: no.
