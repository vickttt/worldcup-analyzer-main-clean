# Portfolio Dependency Trace

This report traces portfolio dependencies after Phase 1 extraction. It is analysis-only.

## app.py Portfolio Logic

Direct portfolio functions still in `app.py`:

- `portfolio_metrics`
- `bet_correlation`
- `weighted_combo_correlation`
- `correlation_matrix_rows`
- `kelly_fraction`
- `kelly_reference_rows`
- `strategy_holdings_rows`
- asset-role helpers:
  - `betting_asset_roles`
  - `betting_asset_role`
  - `role_allocation_rows`
  - `role_exposure`
  - `role_balance_adjustment`
  - `role_constraint_rows`
- allocation/ranking helpers:
  - `optimizer_asset_pool`
  - `allocation_vectors`
  - `portfolio_stability_score`
  - `evaluate_allocation`
  - `optimize_betting_portfolio`
  - `build_strategy_library`
  - `build_auto_optimized_strategy`
  - `allocate_strategy_items`
  - `enforce_correct_score_floor`
  - `evaluate_strategy`
  - `strategy_comparison`
- display and row helpers:
  - `efficient_frontier_rows`
  - `strategy_table_rows`
  - `prematch_strategy_ranking_rows`
  - `portfolio_ranking_rows`
  - `render_portfolio_ranking`
  - `render_portfolio_detail_expanders`

## Imported Portfolio Engine Dependencies

`app.py` imports from `modules.portfolio_engine`:

- `build_bet_id`
- `compute_portfolio_marginal_utility`
- `compute_match_investment_score`
- `compute_portfolio_score`
- `correct_score_exposure_control`
- `dedupe_bets`
- `dedupe_portfolios`
- `generate_style_portfolios`
- `handicap_line_from_text`
- `normalize_handicap_line`
- `portfolio_style_name`
- `portfolio_risk_gate`
- `rank1_eligibility_check`
- `settle_asian_handicap`

## Implicit Portfolio Functions Inside Strategy Module

`modules/strategy/core.py` contains moved helpers that participate in portfolio output:

- `strategy_score`
- `rank_key_with_eligibility`
- `item_path_consistency`
- `strategy_path_consistency`
- `match_betting_score`
- `recommended_stake_mvp`

These functions are deterministic for their input dictionaries, but they depend on implicit keys populated by app-level portfolio evaluation.

## Hidden Coupling Via Ranking Keys

- `strategy_comparison` sorts evaluated strategies using `rank_key_with_eligibility`.
- `rank_key_with_eligibility` reads:
  - `rank1_eligibility.rank1_eligible`
  - `risk_gate.risk_level`
  - `correct_score_exposure.stake_share`
  - `score`
- Small changes to any of those upstream structures can change the displayed first recommendation.

## Hidden Coupling Via Score Aggregation

- `evaluate_strategy` computes intermediate metrics, then calls `compute_portfolio_score`.
- It overwrites `result["score"]` with the portfolio-engine score.
- It also appends risk gate, correct score exposure, rank eligibility, and marginal utility outputs.
- This means app-level strategy evaluation and `modules.portfolio_engine` are already tightly coupled.

## Hidden Coupling Via user_odds

- `modules/odds/core.py` imports `modules.user_odds`.
- `modules.user_odds` imports `modules.portfolio_engine` helpers:
  - `handicap_line_from_text`
  - `normalize_handicap_line`
- Manual portfolio parsing in `app.py` also relies on the same line and candidate semantics.

## Dangerous Shared State Or Contracts

- Strategy, portfolio, bet, fixture, and snapshot objects are dicts with implicit schemas.
- Snapshot data in `data/history/*_pre.json` stores strategy output shapes that future refactors must preserve.
- UI rows depend on Chinese column names and normalized display names.
- `st.session_state` controls current match, page, actual odds input, and portfolio input.

## Extraction Risk Summary

- Direct dependency risk: High.
- Indirect dependency risk: High.
- Dangerous shared state risk: Medium to High.

## Recommendation

Do not extract portfolio logic until golden-output tests compare:

- strategy order
- score values
- selected bet lists
- displayed ranking row values
- post-match settlement summaries
