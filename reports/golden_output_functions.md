# Golden Output Functions

This report identifies functions that define output behavior and should be protected before portfolio/backtest extraction. It is analysis-only.

## Ranking And Sorting

- `strategy_comparison`
  - location: `app.py`
  - output role: ranking
  - downstream usage: Portfolio Ranking UI, pre-match snapshots, recommendation ordering
  - risk level: High
- `rank_key_with_eligibility`
  - location: `modules/strategy/core.py`
  - output role: ranking
  - downstream usage: strategy sorting in `strategy_comparison` and Portfolio Ranking display
  - risk level: High
- `portfolio_ranking_rows`
  - location: `app.py`
  - output role: summary/ranking display
  - downstream usage: Streamlit Portfolio Ranking table
  - risk level: High
- `prematch_strategy_ranking_rows`
  - location: `app.py`
  - output role: summary/ranking display
  - downstream usage: pre-match snapshot/report table rows
  - risk level: Medium

## Scoring

- `strategy_score`
  - location: `modules/strategy/core.py`
  - output role: scoring
  - downstream usage: `evaluate_allocation`, `evaluate_strategy`, ranking output
  - risk level: High
- `compute_portfolio_score`
  - location: `modules/portfolio_engine.py`
  - output role: scoring
  - downstream usage: `evaluate_strategy`, Portfolio Score, recommendation ordering
  - risk level: High
- `compute_match_investment_score`
  - location: `modules/portfolio_engine.py`
  - output role: scoring/summary
  - downstream usage: Match Investment Score card
  - risk level: Medium
- `match_betting_score`
  - location: `modules/strategy/core.py`
  - output role: scoring/summary
  - downstream usage: Match Summary and Recommended Stake card
  - risk level: Medium
- `recommended_stake_mvp`
  - location: `modules/strategy/core.py`
  - output role: summary/stake recommendation
  - downstream usage: Recommended Stake card
  - risk level: Medium

## Allocation

- `evaluate_allocation`
  - location: `app.py`
  - output role: allocation/scoring
  - downstream usage: `optimize_betting_portfolio`
  - risk level: High
- `optimize_betting_portfolio`
  - location: `app.py`
  - output role: allocation
  - downstream usage: auto optimized strategy and ranking candidate
  - risk level: High
- `allocate_strategy_items`
  - location: `app.py`
  - output role: allocation
  - downstream usage: `evaluate_strategy`, strategy construction, displayed bet amounts
  - risk level: High
- `enforce_correct_score_floor`
  - location: `app.py`
  - output role: allocation/risk adjustment
  - downstream usage: strategy item allocation
  - risk level: High

## Strategy Construction

- `build_strategy_library`
  - location: `app.py`
  - output role: recommendation list builder
  - downstream usage: `strategy_comparison`, snapshot ranking output
  - risk level: High
- `build_auto_optimized_strategy`
  - location: `app.py`
  - output role: recommendation list builder
  - downstream usage: `strategy_comparison`
  - risk level: High
- `evaluate_strategy`
  - location: `app.py`
  - output role: scoring/ranking summary
  - downstream usage: `strategy_comparison`, UI, snapshots, reports
  - risk level: High

## Portfolio Summary And Audit

- `portfolio_metrics`
  - location: `app.py`
  - output role: summary
  - downstream usage: portfolio display and risk summary
  - risk level: Medium
- `prediction_audit`
  - location: `app.py`
  - output role: post-match comparison
  - downstream usage: post-match audit UI and snapshots
  - risk level: High
- `recommendation_audit`
  - location: `app.py`
  - output role: post-match comparison
  - downstream usage: post-match recommendation audit table
  - risk level: High
- `settle_strategies`
  - location: `app.py`
  - output role: settlement/evaluation
  - downstream usage: post-match settlement snapshot and UI
  - risk level: High

## Backtest Scripts

- `evaluate_strategy`
  - location: `scripts/generate_world_cup_backfill_benchmark.py`
  - output role: backtest scoring
  - downstream usage: benchmark report generation
  - risk level: High
- `scripts/backtest_portfolio_engine.py`
  - location: script entry point
  - output role: backtest summary
  - downstream usage: reports/backtests outputs
  - risk level: High

## Lock Recommendation

Before moving portfolio or backtest logic, freeze outputs for:

- `strategy_comparison`
- `evaluate_strategy`
- `evaluate_allocation`
- `strategy_score`
- `compute_portfolio_score`
- post-match settlement/audit summaries
